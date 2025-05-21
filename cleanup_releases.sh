#!/bin/bash

# Settings
REPO="briis/affalddk"
DAYS_OLD=360

# Get date for cutoff
CUTOFF_DATE=$(date -v-"$DAYS_OLD"d +"%Y-%m-%d")

echo "Deleting releases older than end $CUTOFF_DATE in repo $REPO..."

# Get all releases as JSON
gh release list -R "$REPO" --limit 100 --json tagName,publishedAt | jq -c '.[]' |
while read -r release; do
  TAG=$(echo "$release" | jq -r '.tagName')
  DATE=$(echo "$release" | jq -r '.publishedAt')

  if [[ "$DATE" < "$CUTOFF_DATE" ]]; then
    echo "Deleting release $TAG (published $DATE)..."
    gh release delete "$TAG" -R "$REPO" -y
    git push origin ":refs/tags/$TAG"
  fi
done
