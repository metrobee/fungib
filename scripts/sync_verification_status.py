#!/usr/bin/env python3
import sqlite3
import urllib.request
import json
import os
import sys
import subprocess

sys.path.insert(0, '/Users/metrobee/GEMINI/scripts')
try:
    import seen_cli
except ImportError:
    pass

DB_PATH = '/Users/metrobee/GEMINI/data/plutof_vaatlused.db'
EXPORT_SCRIPT = '/Users/metrobee/Projects/fungib/scripts/export_dashboard_data.py'

def sync_verifications():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Vali kõik vaatlused, mis on hetkel ootel (verified_by on tühi)
    c.execute("SELECT id, taxon_name FROM observations WHERE verified_by IS NULL OR verified_by = '';")
    pending_obs = c.fetchall()
    print(f"Ootel vaatlusi kontrollimiseks: {len(pending_obs)}")

    if not pending_obs:
        print("Kõik vaatlused on juba kinnitatud.")
        conn.close()
        return

    creds = seen_cli.load_credentials()
    token = seen_cli.get_plutof_token(creds)
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': 'Mozilla/5.0'}

    updated_count = 0

    for obs_id, taxon in pending_obs[:50]: # kontrolli partii kaupa
        url = f"https://api.plutof.ut.ee/v1/public/observations/{obs_id}/"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                d = json.loads(resp.read().decode('utf-8'))
                # Kontrolli kas on kinnitaja vms
                # PlutoF API tagastab vaatluse andmed
                # Kui tulevikus lisandub kinnitaja väli, uuendame
        except Exception as e:
            continue

    conn.close()
    print(f"Sünkroonimine lõpetatud. Uuendatud staatuseid: {updated_count}")

if __name__ == "__main__":
    sync_verifications()
