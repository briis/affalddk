#!/bin/bash

# Settings
REPO="briis/affalddk"
DAYS_OLD=14

# Get date for cutoff
CUTOFF_DATE=$(date -v-"$DAYS_OLD"d +"%Y-%m-%d")

echo "Deleting pre-releases older than $CUTOFF_DATE in repo $REPO..."

# Get all releases with required fields
gh release list -R "$REPO" --limit 100 --json tagName,publishedAt,isPrerelease | jq -c '.[]' |
while read -r release; do
  TAG=$(echo "$release" | jq -r '.tagName')
  DATE=$(echo "$release" | jq -r '.publishedAt')
  IS_PRERELEASE=$(echo "$release" | jq -r '.isPrerelease')

  if [[ "$IS_PRERELEASE" == "true" && "$DATE" < "$CUTOFF_DATE" ]]; then
    echo "Deleting pre-release $TAG (published $DATE)..."
    gh release delete "$TAG" -R "$REPO" -y
    git push origin ":refs/tags/$TAG"
  fi
done
