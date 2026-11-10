#!/usr/bin/env bash
# tools/update_native.sh [c-goome folder] [branch]
# copies goome.h from c-goome into native/ and writes the commit it came from into native/VERSION
# without a folder it clones c-goome (main, or the branch you give) into a temp folder first
set -euo pipefail
cd "$(dirname "$0")/.."
src="${1:-}"
branch="${2:-main}"
tmp=""
if [ -z "$src" ]; then
  tmp="$(mktemp -d "${TMPDIR:-.}/c-goome.XXXXXX")"
  trap 'rm -rf "$tmp"' EXIT
  git clone -q --depth 1 --branch "$branch" https://github.com/goome-ui/c-goome "$tmp"
  src="$tmp"
fi
if [ ! -f "$src/goome.h" ]; then
  echo "theres no goome.h in $src" >&2
  exit 1
fi
cp "$src/goome.h" native/goome.h
git -C "$src" rev-parse HEAD > native/VERSION
if [ -n "$(git -C "$src" status --porcelain goome.h 2>/dev/null)" ]; then
  echo "heads up, goome.h in $src has changes that arent committed, VERSION wont match it" >&2
fi
echo "native/goome.h is now c-goome $(cat native/VERSION)"
echo "rebuild with ./build.sh test and check tests/layout.c still matches goome/_lib.py"
