import sqlite3
import json
import csv
import os

DB_PATH = '/Users/metrobee/GEMINI/data/plutof_vaatlused.db'
CSV_PATH = '/Users/metrobee/.gemini/antigravity/brain/449c0ec9-80fc-480c-9ff4-b1a8f94963a9/.user_uploaded/media_1787168498815.csv'
OUTPUT_JSON = '/Users/metrobee/Projects/fungib/public/data/observations.json'

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

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
    SELECT id, taxon_name, date_time, latitude, longitude, altitude, locality, county, commune, substrate, substrate_type, abundance, remarks, url, created_at
    FROM observations
    ORDER BY date_time DESC, id DESC;
    """)
    rows = c.fetchall()
    
    observations = []
    taxa_set = set()
    county_set = set()

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
        
        c.execute("SELECT filename, filepath FROM observation_photos WHERE observation_id = ?;", (obs_id,))
        p_rows = c.fetchall()
        
        photos = []
        for pr in p_rows:
            fn = pr[0]
            fp = pr[1]
            if fp.startswith("http"):
                photos.append({"url": fp, "thumbnail": fp, "filename": fn})
            elif obs_id in csv_meta and csv_meta[obs_id]["image_url"]:
                s3_url = csv_meta[obs_id]["image_url"]
                photos.append({"url": s3_url, "thumbnail": s3_url, "filename": fn})

        if not photos and obs_id in csv_meta and csv_meta[obs_id]["image_url"]:
            s3_url = csv_meta[obs_id]["image_url"]
            photos.append({"url": s3_url, "thumbnail": s3_url, "filename": os.path.basename(s3_url)})

        extra = csv_meta.get(obs_id, {})

        if taxon:
            taxa_set.add(taxon)
        if county:
            county_set.add(county)

        observations.append({
            "id": obs_id,
            "taxon": taxon,
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
            "determiner": extra.get("determiner", ""),
            "observer": extra.get("observer", "Boris Meldre"),
            "url": url,
            "photos": photos
        })

    conn.close()

    payload = {
        "metadata": {
            "total_observations": len(observations),
            "unique_taxa": len(taxa_set),
            "counties": sorted(list(county_set)),
            "generated_at": os.popen("date -u +'%Y-%m-%dT%H:%M:%SZ'").read().strip()
        },
        "observations": observations
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Eksport edukas: {len(observations)} vaatlust salvestatud faili {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
