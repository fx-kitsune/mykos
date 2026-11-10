#!/bin/bash
# Run Actions shell steps in the persistent Debian builder. The workspace and
# runner temp are mounted at identical absolute paths; artifacts stay on host.
set -euo pipefail
args=(docker exec --workdir "$GITHUB_WORKSPACE")
for name in BUILD_DIRECTORY ARTIFACT_DIRECTORY DIAGNOSTIC_DIRECTORY BUILD_RESULT \
  GITHUB_WORKSPACE GITHUB_SHA GITHUB_RUN_ID GITHUB_RUN_ATTEMPT GITHUB_REPOSITORY \
  GITHUB_STEP_SUMMARY GITHUB_OUTPUT GITHUB_ENV GITHUB_PATH RUNNER_TEMP \
  GH_TOKEN GH_REPO ARTIFACT_RESULT DRAFT_RESULT; do
    if [[ -v "$name" ]]; then args+=(--env "$name"); fi
done
exec "${args[@]}" mykos-debian bash --noprofile --norc -e -o pipefail "$1"
