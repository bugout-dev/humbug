#!/usr/bin/env bash
set -e
git checkout main
git pull upstream main
TAG="python/v$(python setup.py --version)"
read -r -p "Tag: $TAG -- tag and push (y/n)?" ACCEPT
if [ "$ACCEPT" = "y" ]
then
  echo "Tagging and pushing: $TAG..."
  git tag "$TAG"
  git push upstream "$TAG"
else
  echo "noop"
fi
