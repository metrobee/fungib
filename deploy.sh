#!/bin/bash
# See skript sünkroniseerib slaidid PowerPointi (Google Drive) ja laeb need Firebase'i üles.

export PATH="/opt/homebrew/bin:/Users/metrobee/.nvm/versions/node/v20.19.2/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

echo "=== 1. Sünkroniseerin slaidid PowerPointi (Google Drive) ==="
python3 sync_to_pptx.py

echo "=== 2. Laen slaidid Firebase Hostingusse (Web) ==="
npx -y firebase-tools@latest deploy --only hosting --project fungib

echo "=== Sünkroniseerimine valmis! ==="
