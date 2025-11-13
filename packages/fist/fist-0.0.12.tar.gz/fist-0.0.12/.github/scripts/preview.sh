#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/_internal.sh"

fn() {
	if ! type -P gh >/dev/null 2>&1; then
		raise "GitHub CLI is not installed."
	elif (( $# < 2 )) || ! [[ "$1" =~ ^[a-z]+:[0-9]+$ ]]; then
		raise "Missing command or argument, or invalid input."
	fi

	local -r command="${1%%:*}" pr_number="${1##*:}"
	shift

	local -A args report
	parse_args "$@"
	# Do not modify 'args' after this point!

	local -r target_directory="out" subfolder="pr-${pr_number:?}"
	local -r local_folder="$target_directory/$subfolder" remote_folder="docs/$subfolder"
	case "$command" in
		open)
			generate_files "$target_directory" "$subfolder/bundle.json" "$subfolder"
			sync_repo_files "$@" \
				--local-folder "$local_folder" \
				--remote-folder "$remote_folder" \
				--commit-message "$({
					echo "chore: :rocket: deploy $subfolder preview pages"
					echo ""
					echo "See associated pull request for more information."
					echo ""
					echo "Refs: ${args[owner]}/${args[source-repo]}#$pr_number"
				})"
			
			echo "page_url=${BASE_URL:?}/$subfolder" >> "${GITHUB_OUTPUT:-/dev/null}"
			{
				printf ":robot: Subfolder \`%s\` has been synchronized in [%s](%s) _beep boop_." \
					"$subfolder" \
					"${args[owner]}/${args[target-repo]}@\`${report[sha]::7}\`" \
					"/${args[owner]}/${args[target-repo]}/commit/${report[sha]::7}"
			} >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
			{
				echo ":rocket: Deployed preview to ${BASE_URL:?}/$subfolder"
				echo "_If the page displays 404, please wait a few minutes; the update may be pending._"
				echo "> [!IMPORTANT]"
				printf "> **%'.d file(s) changed in %s@%s**\n"\
					"${report[total]:-0}" "${args[owner]}/${args[target-repo]}" "${report[sha]::7}"
				echo "> | State | Count |"
				echo "> | :---- | ----: |"
				(( ${report[created]:-0} )) && printf "> | Created | %'d |\n" "${report[created]}"
				(( ${report[updated]:-0} )) && printf "> | Updated | %'d |\n" "${report[updated]}"
				(( ${report[deleted]:-0} )) && printf "> | Deleted | %'d |\n" "${report[deleted]}"
				echo ">"
				printf "> See also: [job summary](%s)\n" \
					"/${args[owner]}/${args[source-repo]}/actions/runs/${GITHUB_RUN_ID:?}?pr=$pr_number"
				echo ""
				echo ":robot: Please review changes carefully before merging _beep boop_."
			} | gh pr comment "$pr_number" --body-file -
			;;
		close)
			sync_repo_files "$@" \
				--local-folder "$local_folder" \
				--remote-folder "$remote_folder" \
				--commit-message "$({
					echo "chore: :fire: remove $subfolder preview pages"
					echo ""
					echo "See associated pull request for more information."
					echo ""
					echo "Closes: ${args[owner]}/${args[source-repo]}#$pr_number"
				})"
			{
				printf ":robot: Subfolder \`%s\` has been removed in [%s](%s) _beep boop_." \
					"$subfolder" \
					"${args[owner]}/${args[target-repo]}@\`${report[sha]::7}\`" \
					"/${args[owner]}/${args[target-repo]}/commit/${report[sha]::7}"
			} >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
			{
				echo ":wastebasket: Preview removed because the pull request was closed"
				echo "_Once the update is completed, the previous preview page will no longer be available._"
				echo "> [!TIP]"
				printf "> **%'.d file(s) changed in %s@%s**\n"\
					"${report[total]:-0}" "${args[owner]}/${args[target-repo]}" "${report[sha]::7}"
				echo "> | State | Count |"
				echo "> | :---- | ----: |"
				printf "> | Deleted | %'d |\n" "${report[deleted]:-0}"
				echo ">"
				printf "> See also: [job summary](%s)\n" \
					"/${args[owner]}/${args[source-repo]}/actions/runs/${GITHUB_RUN_ID:?}?pr=$pr_number"
				echo ""
				echo ":robot: Please review this merge carefully before releasing _beep boop_."
			} | gh pr comment "$pr_number" --body-file -
			;;
		*)
			raise "No such command '$command'."
			;;
	esac
}

fn "$@"