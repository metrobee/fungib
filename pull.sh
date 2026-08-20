#!/bin/bash
# See skript tõmbab slaidid Google Drive'i PowerPointist ja laeb need Firebase'i üles.

export PATH="/opt/homebrew/bin:/Users/metrobee/.nvm/versions/node/v20.19.2/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

echo "=== 1. Tõmban slaidid PowerPointist (Google Drive) HTML-i ==="
python3 pull_from_pptx.py

echo "=== 2. Laen uuendatud slaidid Firebase Hostingusse (Web) ==="
npx -y firebase-tools@latest deploy --only hosting --project fungib

echo "=== Sünkroniseerimine valmis! ==="
