#!/usr/bin/env python3
import urllib.request
import json
import sqlite3
import os
import sys
import subprocess
import datetime

sys.path.insert(0, '/Users/metrobee/GEMINI/scripts')
try:
    import seen_cli
except ImportError:
    pass

DB_PATH = '/Users/metrobee/GEMINI/data/plutof_vaatlused.db'
EXPORT_SCRIPT = '/Users/metrobee/Projects/fungib/scripts/export_dashboard_data.py'

def sync_live_observations():
    print(f"[{datetime.datetime.now().isoformat()}] Alustan PlutoF reaalajas sünkroonimist...")
    creds = seen_cli.load_credentials()
    token = seen_cli.get_plutof_token(creds)
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': 'Mozilla/5.0'}

    # 1. Päri viimased vaatlused
    url = "https://api.plutof.ut.ee/v1/public/observations/?page%5Bsize%5D=100"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"PlutoF API päring ebaõnnestus: {e}")
        return

    # 2. Ekspordi uuendatud andmestik ja juuruta Firebase'i
    print("Käivitan andmete ekspordi ja Firebase juurutamise...")
    subprocess.run(["python3", EXPORT_SCRIPT], check=True)
    subprocess.run(["firebase", "deploy", "--only", "hosting"], cwd="/Users/metrobee/Projects/fungib", check=True)
    print("Sünkroonimine ja avaldamine edukalt lõpetatud.")

if __name__ == "__main__":
    sync_live_observations()
