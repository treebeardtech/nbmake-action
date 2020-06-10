#!/bin/bash
set -euo pipefail
set -x

# ensure dir is named correctly
mkdir -p "/var/$GITHUB_REPOSITORY"
cp -r . "/var/$GITHUB_REPOSITORY"
cd "/var/$GITHUB_REPOSITORY"

treebeard configure --api_key "$1" --project_id "$GITHUB_REPOSITORY_OWNER" 
treebeard run -n "$2" --confirm --watch