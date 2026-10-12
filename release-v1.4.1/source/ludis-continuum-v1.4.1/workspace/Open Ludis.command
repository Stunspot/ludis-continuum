#!/bin/sh
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if ! /usr/bin/osascript -l JavaScript ./ludis-native-icons.js "$PWD/ludis.icns" "$PWD/Open Ludis.command"; then
  printf '%s\n' 'Ludis icon binding unavailable; opening the session desk.' >&2
fi
python3 ./desk.py
