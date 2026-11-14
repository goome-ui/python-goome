#!/usr/bin/env bash
# tools/update_native.sh [goome.h file or c-goome folder] [branch or commit]
# copies goome.h into native/ and writes the commit it came from into native/VERSION
# without a path it clones c-goome (main, or the branch you give) into a temp folder first
set -euo pipefail
cd "$(dirname "$0")/.."
src="${1:-}"
ref="${2:-}"
tmp=""
if [ -z "$src" ]; then
  tmp="$(mktemp -d "${TMPDIR:-.}/c-goome.XXXXXX")"
  trap 'rm -rf "$tmp"' EXIT
  git clone -q --depth 1 --branch "${ref:-main}" https://github.com/goome-ui/c-goome "$tmp"
  src="$tmp"
  ref=""
fi
if [ -d "$src" ]; then
  src="$src/goome.h"
fi
if [ ! -f "$src" ]; then
  echo "theres no goome.h at $src" >&2
  exit 1
fi
if ! grep -q 'define GOOME_VERSION' "$src" || ! grep -q 'GOOME_IMPLEMENTATION' "$src"; then
  echo "$src doesnt look like the single file goome.h (the one tools/single.py makes)" >&2
  exit 1
fi
dir="$(cd "$(dirname "$src")" && pwd)"
name="$(basename "$src")"
commit=""
if git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
  commit="$(git -C "$dir" rev-parse "${ref:-HEAD}")"
  if [ -z "$ref" ] && [ -n "$(git -C "$dir" status --porcelain -- "$name" 2>/dev/null)" ]; then
    echo "heads up, $src has changes that arent committed, VERSION wont match it" >&2
  fi
elif [ -n "$ref" ]; then
  commit="$ref"
else
  echo "$src isnt in a git repo, pass the c-goome commit it came from as the second argument" >&2
  exit 1
fi
cp "$src" native/goome.h
echo "$commit" > native/VERSION
echo "native/goome.h is now c-goome $commit ($(grep -m1 'define GOOME_VERSION' native/goome.h | awk '{print $3}'))"
echo "rebuild with ./build.sh test and check tests/layout.c still matches goome/_lib.py"
