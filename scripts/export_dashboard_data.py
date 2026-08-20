import sqlite3
import json
import csv
import os
import re
import datetime

DB_PATH = '/Users/metrobee/GEMINI/data/plutof_vaatlused.db'
CSV_PATH = '/Users/metrobee/.gemini/antigravity/brain/449c0ec9-80fc-480c-9ff4-b1a8f94963a9/.user_uploaded/media_1787168498815.csv'
SNIPPETS_PATH = os.path.expanduser('~/.clipsnippet_snippets.json')
OUTPUT_JSON = '/Users/metrobee/Projects/fungib/public/data/observations.json'

def load_est_name_map():
    est_map = {}
    if os.path.exists(SNIPPETS_PATH):
        try:
            with open(SNIPPETS_PATH, 'r', encoding='utf-8') as f:
                d = json.load(f)
            seened = d.get('Seened', {})
            for trigger, val in seened.items():
                m = re.match(r'^(.*?)\s*\((.*?)\)$', val)
                if m:
                    est = m.group(1).strip()
                    sci = m.group(2).strip().lower()
                    sci_species = ' '.join(sci.split()[:2])
                    est_map[sci_species] = est
                    est_map[sci] = est
        except Exception:
            pass
    return est_map

def find_est_name(taxon_name, est_map):
    if not taxon_name:
        return ""
    clean_name = re.sub(r'\(.*?\)', '', taxon_name).strip()
    parts = clean_name.split()
    if len(parts) >= 2:
        bin_name = f"{parts[0]} {parts[1]}".lower()
        if bin_name in est_map:
            return est_map[bin_name]
    return est_map.get(taxon_name.lower(), "")

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    est_map = load_est_name_map()

    csv_meta = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                link = r.get('Veebilink', '').strip()
                if '/' in link:
                    obs_id = link.split('/')[-1]
                    img_url = r.get('Image URL', '').strip()
                    csv_meta[obs_id] = {
                        "image_url": img_url,
                        "determiner": r.get('Määraja.Nimi', '').strip(),
                        "observer": r.get('Vaatleja.Nimi', '').strip(),
                        "notes": r.get('Lisainfo', '').strip(),
                        "locality_csv": r.get('Ala.Nimi', '').strip()
                    }

    c.execute("""
    SELECT id, taxon_name, date_time, latitude, longitude, altitude,
           locality, county, commune, substrate, substrate_type,
           abundance, remarks, url, created_at,
           is_co_observer, collectors, primary_observer, determiner, verified_by, habitat
    FROM observations
    ORDER BY created_at DESC, date_time DESC, id DESC;
    """)
    rows = c.fetchall()
    
    observations = []
    taxa_set = set()
    county_set = set()
    collectors_set = set()

    now = datetime.datetime.now(datetime.timezone.utc)
    today_str = now.strftime('%Y-%m-%d')
    cur_year_str = now.strftime('%Y')
    cur_month_str = now.strftime('%Y-%m')
    start_of_week = (now - datetime.timedelta(days=now.weekday())).strftime('%Y-%m-%d')

    added_today = 0
    added_this_week = 0
    added_this_month = 0
    added_this_year = 0

    primary_count = 0
    co_count = 0

    for r in rows:
        obs_id = str(r[0])
        taxon = r[1] or "Tundmatu takson"
        date_str = (r[2] or "").split('T')[0]
        lat = r[3]
        lon = r[4]
        alt = r[5]
        locality = r[6] or ""
        county = r[7] or ""
        commune = r[8] or ""
        substrate = r[9] or ""
        substrate_type = r[10] or ""
        abundance = r[11] or ""
        remarks = r[12] or ""
        url = r[13] or f"https://app.plutof.ut.ee/observation/view/{obs_id}"
        created_at = r[14] or ""
        is_co = bool(r[15])
        collectors = r[16] or ""
        primary_observer = r[17] or "Boris Meldre"
        determiner = r[18] or ""
        verified_by = r[19] or ""
        habitat = r[20] or ""

        if is_co:
            co_count += 1
        else:
            primary_count += 1

        created_date = created_at.split('T')[0] if created_at else date_str

        # Perioodide loendus
        if created_date == today_str:
            added_today += 1
        if created_date >= start_of_week:
            added_this_week += 1
        if created_date.startswith(cur_month_str):
            added_this_month += 1
        if created_date.startswith(cur_year_str):
            added_this_year += 1

        # Pildid
        c.execute("SELECT filename, filepath, plutof_file_id FROM observation_photos WHERE observation_id = ?;", (obs_id,))
        p_rows = c.fetchall()
        
        photos = []
        for pr in p_rows:
            fn = pr[0]
            fp = pr[1]
            if fp and fp.startswith("http"):
                photos.append({"url": fp, "thumbnail": fp, "filename": fn})
            elif obs_id in csv_meta and csv_meta[obs_id]["image_url"]:
                s3_url = csv_meta[obs_id]["image_url"]
                photos.append({"url": s3_url, "thumbnail": s3_url, "filename": fn})

        if not photos and obs_id in csv_meta and csv_meta[obs_id]["image_url"]:
            s3_url = csv_meta[obs_id]["image_url"]
            photos.append({"url": s3_url, "thumbnail": s3_url, "filename": os.path.basename(s3_url)})

        extra = csv_meta.get(obs_id, {})
        est_name = find_est_name(taxon, est_map)

        if taxon:
            taxa_set.add(taxon)
        if county:
            county_set.add(county)
        if primary_observer:
            collectors_set.add(primary_observer)

        obs_item = {
            "id": obs_id,
            "taxon": taxon,
            "est_name": est_name,
            "date": date_str,
            "latitude": lat,
            "longitude": lon,
            "altitude": alt,
            "locality": locality or extra.get("locality_csv", ""),
            "county": county,
            "commune": commune,
            "substrate": substrate,
            "substrate_type": substrate_type,
            "abundance": abundance,
            "remarks": remarks or extra.get("notes", ""),
            "is_co_observer": is_co,
            "collectors": collectors or ("Boris Meldre" if not is_co else f"{primary_observer}, Boris Meldre"),
            "primary_observer": primary_observer,
            "determiner": determiner or extra.get("determiner", ""),
            "verified_by": verified_by,
            "habitat": habitat,
            "url": url,
            "created_at": created_at,
            "photos": photos
        }

        observations.append(obs_item)

    # Viimati sisestatud vaatlus
    c.execute("SELECT id, taxon_name, date_time, locality, county, url, created_at, is_co_observer, primary_observer FROM observations ORDER BY created_at DESC, id DESC LIMIT 1;")
    last_r = c.fetchone()
    latest_obs = None
    if last_r:
        last_est = find_est_name(last_r[1], est_map)
        latest_obs = {
            "id": str(last_r[0]),
            "taxon": last_r[1],
            "est_name": last_est,
            "date": (last_r[2] or "").split('T')[0],
            "locality": last_r[3] or "",
            "county": last_r[4] or "",
            "url": last_r[5] or f"https://app.plutof.ut.ee/observation/view/{last_r[0]}",
            "created_at": last_r[6],
            "is_co_observer": bool(last_r[7]),
            "primary_observer": last_r[8]
        }

    conn.close()

    payload = {
        "metadata": {
            "total_observations": len(observations),
            "unique_taxa": len(taxa_set),
            "counties": sorted(list(county_set)),
            "observers": sorted(list(collectors_set)),
            "generated_at": now.isoformat(),
            "role_stats": {
                "total": len(observations),
                "primary": primary_count,
                "co_observer": co_count
            },
            "time_stats": {
                "today": added_today,
                "this_week": added_this_week,
                "this_month": added_this_month,
                "this_year": added_this_year
            },
            "latest_observation": latest_obs
        },
        "observations": observations
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Eksport edukas: {len(observations)} vaatlust salvestatud faili {OUTPUT_JSON}")
    print(f"Esikohal: {observations[0]['est_name']} ({observations[0]['taxon']}) ID: {observations[0]['id']}")

if __name__ == "__main__":
    main()
