#!/usr/bin/env sh

set -eu

REPO_ROOT="$(git rev-parse --show-toplevel)"

git config core.hooksPath "${REPO_ROOT}/.githooks"
chmod +x "${REPO_ROOT}/.githooks/post-commit"

echo "Hooks configurados em ${REPO_ROOT}/.githooks"
