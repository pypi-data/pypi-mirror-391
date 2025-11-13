#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

declare -i group_log_started=0

group_log_start() {
	echo "::group::$*"
	group_log_started=1
}

group_log_end() {
	if (( group_log_started )); then
		echo "::endgroup::"
		group_log_started=0
	fi
}

sync_repo_files() {
	if ! type -P gh >/dev/null 2>&1; then
		raise "GitHub CLI is not installed."
	fi

	local -A args
	parse_args "$@"
	# Do not modify 'args' after this point!

	local -r temp_folder=$(mktemp -d)
	trap '{ group_log_end; rm -rf -- '"$temp_folder"'; }' EXIT
	local -r temp_file=$(mktemp -p "$temp_folder")

	group_log_start "1. Fetch the latest commit and tree SHA on default branch"
	if ! branch=$(
		gh api "repos/${args[owner]}/${args[target-repo]}" \
			--jq '.default_branch'
	); then
		raise "Cannot get '${args[owner]}/${args[target-repo]}' default branch."
	elif ! commit_sha=$(
		gh api "repos/${args[owner]}/${args[target-repo]}/git/ref/heads/$branch" \
			--jq '.object.sha' 2>/dev/null
	); then
		if ! IFS=$'\t' read -r commit_sha tree_sha < <(
			gh api "repos/${args[owner]}/${args[target-repo]}/contents/.gitkeep" \
				--method PUT \
				--field message="feat: :tada: initial project" \
				--field content="$(printf '' | base64 -w 0)" \
				--field branch="$branch" \
				--jq '[.commit.sha // "", .commit.tree.sha // ""] | @tsv'
		); then
			raise "Cannot create initial commit on '${args[owner]}/${args[target-repo]}'."
		fi
	elif ! tree_sha=$(
		gh api "repos/${args[owner]}/${args[target-repo]}/git/commits/$commit_sha" \
			--jq '.tree.sha'
	); then
		raise "Cannot get '${args[owner]}/${args[target-repo]}' tree SHA."
	fi

	readonly branch commit_sha tree_sha
	echo "::debug::Default branch: $branch"
	echo "::debug::Commit SHA: $commit_sha"
	echo "::debug::Tree SHA: $tree_sha"

	local new_commit_sha="${commit_sha:?}" new_tree_sha="${tree_sha:?}"
	local -i batch_no=0 current_batch_size=0
	local -r payload=$(mktemp -p "$temp_folder")
	create_batch_commit() {
		(( batch_no+=1 ))
		echo "::debug::Calling batch commit #$batch_no (size: $(numfmt --to=si --suffix=B "$current_batch_size"))"
		if [[ -s "$temp_file" ]]; then

			echo "::debug::Create new trees and commits for batch files."

			: > "$payload"
			jq -nc --arg base_tree "$new_tree_sha" --slurpfile tree "$temp_file" \
				'{base_tree: $base_tree, tree: $tree}' >> "$payload"

			if ! new_tree_sha=$(
				gh api "repos/${args[owner]}/${args[target-repo]}/git/trees" \
					--method POST \
					--input "$payload" \
					--jq '.sha'
			); then
				raise "Failed to create new tree."
			elif ! new_commit_sha=$(
				gh api "repos/${args[owner]}/${args[target-repo]}/git/commits" \
					--method POST \
					--field message="build: :bento: sync source files (batch ${batch_no})" \
					--field tree="$new_tree_sha" \
					--field parent="$new_commit_sha" \
					--jq '.sha'
			); then
				raise "Failed to create new commit."
			else
				echo "::debug::New tree SHA: $new_tree_sha"
				echo "::debug::New commit SHA: $new_commit_sha"
				: > "$temp_file"
			fi
		else
			echo "::debug::No files to commit in this batch."
		fi
	}
	group_log_end

	group_log_start "2. Prepare a list of new, updated and deleted files"
	echo "::notice::Blob size limit - 100MB per file."
	echo "::notice::Tree array limit - max 100k entries or 7MB per request."
	echo "::notice::Preparing to upload archives..."

	local -i created=0 updated=0 deleted=0
	local -i -r max_file_size=90000000	# 90MB
	local -i -r max_batch_size=6500000	# 6.5MB
	local -i -r max_entries=50000		# 50k entries
	# 1. Add a deletion entries
	local -a jq_filters=( '.tree[]' '| select(.type == "blob")')
	if [[ "${args[remote-folder]}" != "." ]]; then
		jq_filters+=( '| select(.path | startswith("'"${args[remote-folder]#./}"'"))' )
	fi
	jq_filters+=( '| .path' )
	while IFS= read -r -u 9; do
		local file_path="${REPLY#"${args[remote-folder]#./}/"}"
		[[ "${args[local-folder]}" != "." ]] && file_path="${args[local-folder]#./}/$file_path"
		if ! [[ -e "$file_path" ]]; then
			(( deleted+=1 ))
			echo "::debug::Deleted file #$deleted: $REPLY"
			jq -nc --arg path "$REPLY" \
				'{path: $path, mode: "100644", type: "blob", sha: null}' >> "$temp_file"
			(( $(wc -l < "$temp_file") >= max_entries )) && create_batch_commit
		fi
	done 9< <(
		gh api "repos/${args[owner]}/${args[target-repo]}/git/trees/$tree_sha?recursive=true" \
			--jq "${jq_filters[*]}"
	)
	# 2. Add a creation/modification entries
	if [[ -d "${args[local-folder]}" ]]; then
		local -a find_args=( "${args[local-folder]}" \( -type d -name .git -prune \) -o -type 'f,l' )
		if [[ -n "${args[exclude]:-}" ]]; then
			find_args+=( \( )
			while IFS= read -r -u 9; do
				find_args+=( -not -path "$REPLY" )
			done 9<<<"${args[exclude]}"
			find_args+=( \) )
		fi
		if [[ -n "${args[include]:-}" ]]; then
			local -i index=0
			find_args+=( \( )
			while IFS= read -r -u 9; do
				(( index )) && find_args+=( -o )
				find_args+=( -path "$REPLY" )
				(( index+=1 ))
			done 9<<<"${args[include]}"
			find_args+=( \) )
		fi
		find_args+=( -print0 )

		while IFS= read -r -d '' -u 9; do
			local mode="100644"; [[ -x "$REPLY" ]] && mode="100755";
			local file_path="${REPLY#"${args[local-folder]}/"}"
			[[ "${args[remote-folder]}" != "." ]] && file_path="${args[remote-folder]#./}/$file_path"
			local file_size; file_size=$(stat -c%s "$REPLY")
			if (( file_size >= max_file_size )); then
				echo "::warning::File $REPLY (size: %s) exceeds the maximum size limit and will be ignored." \
					"$(numfmt --to=si --suffix=B "$file_size")"
				continue
			else
				: > "$payload"
				if [[ -L "$REPLY" ]]; then
					mode="120000"
					# For symlinks, use the symlink target as content
					printf '{"encoding":"base64","content":"%s"}' "$(readlink "$REPLY" | base64 -w 0)" >> "$payload"
				else
					printf '{"encoding":"base64","content":"%s"}' "$(base64 -w 0 "$REPLY")" >> "$payload"
				fi

				if ! blob_sha=$(
					gh api "repos/${args[owner]}/${args[target-repo]}/git/blobs" \
						--method POST \
						--input "$payload" \
						--jq '.sha'
				); then
					raise "Cannot create '$file_path' blob SHA."
				elif ! remote_blob_sha=$(
					gh api "repos/${args[owner]}/${args[target-repo]}/contents/$file_path" \
						--jq '.sha' 2>/dev/null
				); then
					(( created+=1 ))
					echo "::debug::Created file #$created: $file_path (size: $(numfmt --to=si --suffix=B "$file_size"))"
				elif [[ "$blob_sha" != "$remote_blob_sha" ]]; then
					(( updated+=1 ))
					echo "::debug::Updated file #$updated: $file_path (size: $(numfmt --to=si --suffix=B "$file_size"))"
				else
					echo "::debug::Unchanged file: $file_path (size: $(numfmt --to=si --suffix=B "$file_size"))"
					continue
				fi

				if (( current_batch_size + file_size >= max_batch_size )) || (( $(wc -l < "$temp_file") >= max_entries )); then
					create_batch_commit
					current_batch_size=$file_size
				else
					(( current_batch_size+=file_size ))
				fi
				jq -nc --arg path "$file_path" --arg mode "$mode" --arg sha "$blob_sha" \
					'{path: $path, mode: $mode, type: "blob", sha: $sha}' >> "$temp_file"
			fi
		done 9< <(find "${find_args[@]}")
	fi

	local -i -r total=$(( created + updated + deleted ))
	if (( total )); then
		# Commit final batch if needed
		[[ -s "$temp_file" ]] && create_batch_commit
		[[ -f "$payload" ]] && rm "$payload"
		[[ -f "$temp_file" ]] && rm "$temp_file"
		echo "::notice::$total file(s) changed across $batch_no batch(es)."
		group_log_end
	else
		echo "::notice::No changes detected. Skipping commit."
		exit 0
	fi

	group_log_start "3. Create final squash commit and then push"
	if ! new_commit_sha=$(
		gh api "repos/${args[owner]}/${args[target-repo]}/git/commits" \
			--method POST \
			--input - <<< "$(jq -nc \
				--arg message "${args[commit-message]}" \
				--arg tree "$new_tree_sha" \
				--arg parent "$commit_sha" \
				'{message: $message, tree: $tree, parents: [$parent]}')" \
			--jq '.sha'
	); then
		raise "Failed to create squash commit."
	elif ! gh api "repos/${args[owner]}/${args[target-repo]}/git/refs/heads/$branch" \
		--method PATCH \
		--field force=true \
		--field sha="$new_commit_sha" \
		--silent 2>/dev/null; then
		raise "Failed to update branch reference."
	else
		echo "::debug::New commit SHA: $new_commit_sha"
		group_log_end
	fi

	if [[ "$(declare -p report 2>/dev/null)" =~ "declare -A" ]]; then
		group_log_start "4. Send back output/statistics report"
		report=(
			[created]="$created"
			[updated]="$updated"
			[deleted]="$deleted"
			[total]="$total"
			[sha]="$new_commit_sha"
		)
		group_log_end
	fi

	echo "::notice::Synchronization completed."
}