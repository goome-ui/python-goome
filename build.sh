#!/usr/bin/env bash
# ./build.sh          builds the native lib into goome/_native/
# ./build.sh test     same, then runs the tests
# ./build.sh win      goome.dll with mingw
set -euo pipefail
cd "$(dirname "$0")"
what="${1:-}"
out=goome/_native
mkdir -p "$out"
flags=(-O2 -std=c99 -Wall -Wextra -Wno-unused-parameter -Wno-missing-field-initializers ${WERROR:+-Werror})
os="$(uname -s)"
if [ "$what" = win ]; then
  cc="${CC:-x86_64-w64-mingw32-gcc}"
  "$cc" "${flags[@]}" -shared -static-libgcc -Wl,--export-all-symbols -o "$out/goome.dll" native/goome_lib.c
  echo "built $out/goome.dll"
  exit 0
fi
case "$os" in
MINGW* | MSYS* | CYGWIN*)
  "${CC:-gcc}" "${flags[@]}" -shared -static-libgcc -Wl,--export-all-symbols -o "$out/goome.dll" native/goome_lib.c
  lib="$out/goome.dll"
  ;;
Darwin)
  "${CC:-cc}" "${flags[@]}" -fPIC -dynamiclib -mmacosx-version-min=11.0 -o "$out/libgoome.dylib" native/goome_lib.c
  lib="$out/libgoome.dylib"
  ;;
*)
  "${CC:-cc}" "${flags[@]}" -fPIC -shared -o "$out/libgoome.so" native/goome_lib.c
  lib="$out/libgoome.so"
  ;;
esac
echo "built $lib"
if [ "$what" = test ]; then "${PY:-python3}" -m unittest discover -s tests -v; fi
