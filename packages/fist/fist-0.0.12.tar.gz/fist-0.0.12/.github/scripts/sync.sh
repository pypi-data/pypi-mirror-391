#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/_internal.sh"

fn() {
	if ! type -P gh >/dev/null 2>&1; then
		raise "GitHub CLI is not installed."
	fi

	local -A args report
	parse_args "$@"
	# Do not modify 'args' after this point!

	printf "::notice::Replacing all instances of '%s' with '%s'.\n" \
		"${args[owner]}/${args[source-repo]}" "${args[owner]}/${args[target-repo]}"

	local -a files=()
	while IFS= read -r -d '' f; do files+=("$f"); done < <(find . -maxdepth 1 -type f -name "*.md" -print0)
	while IFS= read -r -d '' f; do files+=("$f"); done < <(find i18n -type f -name "*.md" -print0)
	while IFS= read -r -d '' f; do files+=("$f"); done < <(find .github -type f -name "*.yml" -print0)
	while IFS= read -r -d '' f; do files+=("$f"); done < <(find docs -type f -name "*.yml" -print0)

	if (( ${#files[@]} )); then
		sed -i -E \
			-e "s#${args[owner]}/${args[source-repo]}([^a-zA-Z0-9._-]|$)#${args[owner]}/${args[target-repo]}\1#g" \
			-e "s#${args[owner]}(.github.io)/${args[source-repo]}([^a-zA-Z0-9._-]|$)#${args[owner]}\1/${args[target-repo]}\2#g" \
			"${files[@]}"
	fi

	echo "::notice::Replacement completed."
	
	# 1. Format co-authors' information
	local -a co_authors=()
	if [[ -n "${args[co-authors]:-}" ]]; then
		local pattern="^[a-zA-Z0-9_-]+$"
		while IFS= read -r -u 9; do
			if [[ "$REPLY" == - ]]; then
				continue
			elif [[ "$REPLY" == teams/* ]]; then
				if ! [[ "${REPLY#teams/}" =~ $pattern ]]; then
					raise "Team name '$REPLY' does not match the format '${pattern/^/^teams/}'."
				elif ! team_members=$(
					gh api "orgs/${args[owner]}/$REPLY/members" \
						--jq 'if (.|type) == "array" then .[].id else empty end'
				); then
					raise "Team name '$REPLY' does not exist or you do not have permission to view."
				else
					while IFS= read -r -u 9; do
						co_authors+=(
							"Co-Authored-By: $(
								gh api "user/$REPLY" \
									--jq '(.name // .login)
									+ " <" + (.id | tostring) + "+" + .login + "@users.noreply.github.com>"'
							)"
						)
					done 9<<<"$team_members"
				fi
			elif ! [[ "$REPLY" =~ $pattern ]]; then
				raise "Username '$REPLY' does not match the format '$pattern'."
			elif ! user_id=$(
				gh api "search/users?q=user:$REPLY" \
					--jq '.items[0].id'
			); then
				raise "Username '$REPLY' does not exist or you do not have permission to view."
			else
				co_authors+=(
					"Co-Authored-By: $(
						gh api "user/$user_id" \
							--jq '(.name // .login)
							+ " <" + (.id | tostring) + "+" + .login + "@users.noreply.github.com>"'
					)"
				)
			fi
		done 9<<<"${args[co-authors]}"
	fi

	# 2. Fetch release tag name
	local tag_name=""
	if [[ "${GITHUB_REF:-}" == refs/tags/* ]]; then
		tag_name="${GITHUB_REF##refs/tags/}"
		if [[ "$tag_name" == latest ]]; then
			tag_name=$(
				gh api "repos/${args[owner]}/${args[source-repo]}/releases/latest" \
					--jq '.tag_name'
			)
		elif ! [[ "$tag_name" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
			tag_name=$(
				gh api "repos/${args[owner]}/${args[source-repo]}/releases" \
					--jq 'map(select(.tag_name | startswith("'"$tag_name"'"))) | first.tag_name'
			)
		fi
		# 2-1. Use v0.x.x for initial development; use v1.0.0+ for stable/production.
		[[ "$tag_name" == v0.* ]] && tag_name="v1.0.0"
		# 2-2. Verify target repository and tag
		if ! gh api "repos/${args[owner]}/${args[target-repo]}" --silent 2>/dev/null; then
			raise "Repository '${args[owner]}/${args[target-repo]}' cannot be found."
		elif gh api "repos/${args[owner]}/${args[target-repo]}/releases/tags/$tag_name" --silent 2>/dev/null; then
			echo "::warning::Duplicate tag name '$tag_name'."
		fi
	fi

	# 3. Combine custom commit message
	if ! commit_message="$(echo -e "${args[commit-message]:-}")" && [[ -z "$commit_message" ]]; then
		raise "Commit message cannot be empty."
	elif [[ "$commit_message" =~ $'\nCo-Authored-By' ]]; then
		raise "Do not add co-authors in the commit footer."
	elif [[ "$commit_message" =~ $'\nRelease-As' ]]; then
		raise "Do not add release-tag in the commit footer."
	elif ! branch=$(
        gh api "repos/${args[owner]}/${args[target-repo]}" \
            --jq '.default_branch'
    ); then
        raise "Cannot get '${args[owner]}/${args[target-repo]}' default branch."
    elif ! pattern="$(
        gh api "repos/${args[owner]}/${args[source-repo]}/rules/branches/${branch}" \
            --jq 'first(.[] | select(.type == "commit_message_pattern")) | .parameters.pattern'
        )"; then
        raise "Cannot get commit message pattern."
    elif ! grep -Pq "$pattern" <<< "$commit_message"; then
        raise "Commit message should match the pattern: '${pattern//\\/\\\\}'"
    fi

	local -a exclude=(
		"CHANGELOG.md"
		".github/**/preview.*"
		".github/**/sync.*"
		".github/scripts/_*"
		".github/dependabot.yml"
	)
	local -r manifest_path=".github/release-please/.release-please-manifest.json"
	if gh api "repos/${args[owner]}/${args[target-repo]}/contents/$manifest_path" \
		--silent 2>/dev/null; then
		exclude+=( "$manifest_path" )
	fi
	readonly exclude

	sync_repo_files "$@" \
		--local-folder "." \
		--remote-folder "." \
		--exclude "$(IFS=, ; echo "${exclude[*]}")" \
		--commit-message "$({
			echo "$commit_message"
			( [[ -n "$tag_name" ]] || (( ${#co_authors[@]} )) ) && echo ""
			[[ -n "$tag_name" ]] && echo "Release-As: $tag_name"
			(( ${#co_authors[@]} )) && printf '%s\n' "${co_authors[@]}" | sort -u
		})"
	{
		echo "### :twisted_rightwards_arrows: Result"
		[[ -n "$tag_name" ]] && {
			echo "_If the release-please PR is not ready yet, please wait; CI/CD may be running._"
		}
		echo "> [!NOTE]"
		printf "> **%'.d file(s) synchronized to [%s](%s)**\n" \
			"${report[total]:-0}" \
			"${args[owner]}/${args[target-repo]}@\`${report[sha]::7}\`" \
			"/${args[owner]}/${args[target-repo]}/commit/${report[sha]::7}"
		echo "> | State | Count |"
		echo "> | :---- | ----: |"
		printf "> | Created | %'d |\n" "${report[created]:-0}"
		printf "> | Updated | %'d |\n" "${report[updated]:-0}"
		printf "> | Deleted | %'d |\n" "${report[deleted]:-0}"
		[[ -n "$tag_name" ]] && {
			echo ""
			echo ":robot: Please review changes carefully before releasing _beep boop_."
			echo "_If you do not have permission, please contact a code owner for approval_"
		}
	} >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
}

fn "$@"