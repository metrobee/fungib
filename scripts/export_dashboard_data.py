import sqlite3
import json
import csv
import os
import re
import datetime

DB_PATH = "/Users/metrobee/GEMINI/data/plutof_vaatlused.db"
CSV_PATH = "/Users/metrobee/GEMINI/data/plutof_full_export_latest.csv"
SNIPPETS_PATH = os.path.expanduser("~/.clipsnippet_snippets.json")
RED_LIST_PATH = "/Users/metrobee/GEMINI/data/eesti_punane_nimestik_seened.json"
OUTPUT_JSON = "/Users/metrobee/Projects/fungib/public/data/observations.json"

def load_red_list():
    if os.path.exists(RED_LIST_PATH):
        try:
            with open(RED_LIST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

RED_ORDER = {"CR": 1, "EN": 2, "VU": 3, "NT": 4, "DD": 5, "RE": 6}

def find_red_list_info(taxon_name, est_name, red_dict):
    if not red_dict:
        return {"status": "", "label": "", "protection": "", "score": 99}
    
    t_clean = re.sub(r"\(.*?\)", "", taxon_name or "").strip().lower()
    words = t_clean.split()
    bin_name = f"{words[0]} {words[1]}" if len(words) >= 2 else t_clean
    
    v_clean = (est_name or "").strip().lower()
    v_words = [v.strip() for v in v_clean.split(",") if v.strip()]
    
    info = red_dict.get(bin_name) or red_dict.get(t_clean)
    if not info:
        for vw in v_words:
            if vw in red_dict:
                info = red_dict[vw]
                break

    if info:
        raw_status = info.get("punane_nimestik") or ""
        code = raw_status.split()[0] if raw_status else ""
        prot = info.get("kaitsekategooria") or ""
        score = RED_ORDER.get(code, 50)
        return {
            "status": code,
            "label": raw_status,
            "protection": prot,
            "score": score
        }
        
    return {"status": "", "label": "", "protection": "", "score": 99}

def load_est_name_map():
    est_map = {}
    if os.path.exists(SNIPPETS_PATH):
        try:
            with open(SNIPPETS_PATH, "r", encoding="utf-8") as f:
                d = json.load(f)
            seened = d.get("Seened", {})
            for trigger, val in seened.items():
                m = re.match(r"^(.*?)\s*\((.*?)\)$", val)
                if m:
                    est = m.group(1).strip()
                    sci = m.group(2).strip().lower()
                    sci_species = " ".join(sci.split()[:2])
                    est_map[sci_species] = est
                    est_map[sci] = est
        except Exception:
            pass
    return est_map

def find_est_name(taxon_name, est_map):
    if not taxon_name:
        return ""
    clean_name = re.sub(r"\(.*?\)", "", taxon_name).strip()
    parts = clean_name.split()
    if len(parts) >= 2:
        bin_name = f"{parts[0]} {parts[1]}".lower()
        if bin_name in est_map:
            return est_map[bin_name]
    return est_map.get(taxon_name.lower(), "")

def extract_specimen_info(remarks, substrate, locality, csv_notes):
    combined = f"{remarks} {substrate} {locality} {csv_notes}"
    
    is_specimen = False
    specimen_type = ""
    specimen_code = ""
    microscopic_notes = ""
    
    # 1. Herbarium / Collector voucher codes
    herb_match = re.search(r"(TU\s*\d+|TAA\s*\d+|KM\d+-\d+|#\w+-\w+|coll\.?)", combined, re.IGNORECASE)
    if herb_match or "herbaar" in combined.lower() or "kuivatis" in combined.lower():
        is_specimen = True
        specimen_type = "herbaarium"
        if herb_match:
            specimen_code = herb_match.group(0).strip()
            
    # 2. DNA Sample / Sequencing tags
    if re.search(r"(DNA|sekveneer|ITS|ekstraktsioon)", combined, re.IGNORECASE):
        is_specimen = True
        specimen_type = "dna"
        dna_tag_match = re.search(r"(#[\w-]+|\w+-\w+)?\s*(?:->)?\s*DNA[^\.,;]*", combined, re.IGNORECASE)
        if dna_tag_match:
            tag_str = dna_tag_match.group(0).strip()
            specimen_code = tag_str if not specimen_code else f"{specimen_code} ({tag_str})"
            
    # 3. Microscopic notes & Spore dimensions
    micro_match = re.search(r"(\d+[\.,]?\d*\s*[-–xX]\s*\d+[\.,]?\d*(?:\s*[-–xX]\s*\d+[\.,]?\d*)?\s*(?:μm|mikromeetr|µm)?|eosed|tsüstidi|basidia|pooride niidid|tsüanofiil|KOH|amüloid)", combined, re.IGNORECASE)
    if micro_match:
        if not specimen_type:
            specimen_type = "mikroskoopia"
            is_specimen = True
        microscopic_notes = remarks.strip()
        
    return {
        "is_specimen": is_specimen,
        "specimen_type": specimen_type,
        "specimen_code": specimen_code,
        "microscopic_notes": microscopic_notes
    }

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    est_map = load_est_name_map()
    red_dict = load_red_list()

    csv_meta = {}
    csv_mtime = None
    if os.path.exists(CSV_PATH):
        csv_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(CSV_PATH), tz=datetime.timezone.utc).isoformat()
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                link = r.get("Veebilink", "").strip()
                if "/" in link:
                    obs_id = link.split("/")[-1]
                    img_url = r.get("Image URL", "").strip()
                    csv_meta[obs_id] = {
                        "image_url": img_url,
                        "determiner": r.get("Määrang.Määrajad", "").strip(),
                        "observer": r.get("Sündmus.Kogujad", "").strip() or r.get("Õiguste hoidja", "").strip(),
                        "notes": r.get("Märkused", "").strip(),
                        "locality_csv": r.get("Ala.Asukoha tekst", "").strip() or r.get("Ala.Nimi", "").strip()
                    }

    c.execute("""
    SELECT o.id, o.taxon_name, o.date_time, o.latitude, o.longitude, o.altitude,
           o.locality, o.county, o.commune, o.substrate, o.substrate_type,
           o.abundance, o.remarks, o.url, o.created_at,
           o.is_co_observer, o.collectors, o.primary_observer, o.determiner, o.verified_by, o.habitat,
           COALESCE(o.project_id, ''), COALESCE(o.project_name, ''),
           COALESCE(o.vernacular_name, ''), COALESCE(o.taxon_id, ''),
           COALESCE(tv.vernacular_names_json, '[]'), COALESCE(tv.est_names, ''), COALESCE(tv.all_names_search, '')
    FROM observations o
    LEFT JOIN taxa_vernacular_names tv ON o.taxon_id = tv.taxon_id
    ORDER BY o.created_at DESC, o.date_time DESC, o.id DESC;
    """)
    rows = c.fetchall()
    
    observations = []
    taxa_registry = {}
    taxa_set = set()
    county_set = set()
    collectors_set = set()
    projects_dict = {}

    red_stats = {
        "total_listed": 0,
        "CR": 0,
        "EN": 0,
        "VU": 0,
        "NT": 0,
        "DD": 0,
        "RE": 0,
        "protected": 0
    }

    specimen_stats = {
        "total": 0,
        "herbaarium": 0,
        "dna": 0,
        "mikroskoopia": 0
    }

    now = datetime.datetime.now(datetime.timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    cur_year_str = now.strftime("%Y")
    cur_month_str = now.strftime("%Y-%m")
    start_of_week = (now - datetime.timedelta(days=now.weekday())).strftime("%Y-%m-%d")

    added_today = 0
    added_this_week = 0
    added_this_month = 0
    added_this_year = 0

    primary_count = 0
    co_count = 0
    verified_count = 0
    pending_count = 0

    for r in rows:
        obs_id = str(r[0])
        taxon = r[1] or "Tundmatu takson"
        date_str = (r[2] or "").split("T")[0]
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
        proj_id = str(r[21] or "").strip()
        proj_name = str(r[22] or "").strip()
        vernacular_db = str(r[23] or "").strip()
        taxon_id = str(r[24] or "").strip()
        v_json_str = r[25] or "[]"
        tv_est_names = str(r[26] or "").strip()
        all_names_search = str(r[27] or "").strip()

        try:
            vernacular_list = json.loads(v_json_str)
        except Exception:
            vernacular_list = []

        is_verified = bool(verified_by)
        if is_verified:
            verified_count += 1
        else:
            pending_count += 1

        if is_co:
            co_count += 1
        else:
            primary_count += 1

        created_date = created_at.split("T")[0] if created_at else date_str

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

        est_name = tv_est_names or vernacular_db or find_est_name(taxon, est_map)

        if not all_names_search:
            all_names_search = f"{est_name} {taxon}"

        # Registreeri taksonite sõnastik (Normaliseerimine)
        taxon_key = taxon_id or taxon
        if taxon_key and taxon_key not in taxa_registry:
            taxa_registry[taxon_key] = {
                "vernacular_names": vernacular_list,
                "all_names_search": all_names_search,
                "est_name": est_name
            }

        # Punane nimestik ja kaitsekategooria
        red_info = find_red_list_info(taxon, est_name, red_dict)
        if red_info["status"]:
            red_stats["total_listed"] += 1
            if red_info["status"] in red_stats:
                red_stats[red_info["status"]] += 1
        if red_info["protection"]:
            red_stats["protected"] += 1

        # Herbaariumi ja näidiste analüüs
        csv_notes = csv_meta[obs_id]["notes"] if obs_id in csv_meta else ""
        specimen_res = extract_specimen_info(remarks, substrate, locality, csv_notes)
        if specimen_res["is_specimen"]:
            specimen_stats["total"] += 1
            stype = specimen_res["specimen_type"]
            if stype in specimen_stats:
                specimen_stats[stype] += 1

        if taxon:
            taxa_set.add(taxon)
        if county:
            county_set.add(county)
        if primary_observer:
            collectors_set.add(primary_observer)

        if proj_id:
            if proj_id not in projects_dict:
                projects_dict[proj_id] = {"id": proj_id, "name": proj_name or f"Projekt {proj_id}", "count": 0}
            projects_dict[proj_id]["count"] += 1

        obs_item = {
            "id": obs_id,
            "taxon": taxon,
            "taxon_id": taxon_id,
            "taxon_key": taxon_key,
            "est_name": est_name,
            "red_list_status": red_info["status"],
            "red_list_label": red_info["label"],
            "protection_category": red_info["protection"],
            "red_list_score": red_info["score"],
            "date": date_str,
            "latitude": lat,
            "longitude": lon,
            "altitude": alt,
            "locality": locality,
            "county": county,
            "commune": commune,
            "substrate": substrate,
            "substrate_type": substrate_type,
            "abundance": abundance,
            "remarks": remarks,
            "is_co_observer": is_co,
            "collectors": collectors,
            "primary_observer": primary_observer,
            "determiner": determiner,
            "verified_by": verified_by,
            "is_verified": is_verified,
            "habitat": habitat,
            "project_id": proj_id,
            "project_name": proj_name,
            "url": url,
            "created_at": created_at,
            "photos": photos,
            "is_specimen": specimen_res["is_specimen"],
            "specimen_type": specimen_res["specimen_type"],
            "specimen_code": specimen_res["specimen_code"],
            "microscopic_notes": specimen_res["microscopic_notes"]
        }

        observations.append(obs_item)

    # Viimati sisestatud vaatlus
    c.execute("SELECT id, taxon_name, date_time, locality, county, url, created_at, is_co_observer, primary_observer, COALESCE(vernacular_name, '') FROM observations ORDER BY created_at DESC, id DESC LIMIT 1;")
    last_r = c.fetchone()
    latest_obs = None
    if last_r:
        last_est = (last_r[9] or "").strip() or find_est_name(last_r[1], est_map)
        latest_obs = {
            "id": str(last_r[0]),
            "taxon": last_r[1],
            "est_name": last_est,
            "date": (last_r[2] or "").split("T")[0],
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
            "co_data_updated_at": csv_mtime or now.isoformat(),
            "role_stats": {
                "total": len(observations),
                "primary": primary_count,
                "co_observer": co_count
            },
            "verification_stats": {
                "verified": verified_count,
                "pending": pending_count
            },
            "red_list_stats": red_stats,
            "specimen_stats": specimen_stats,
            "time_stats": {
                "today": added_today,
                "this_week": added_this_week,
                "this_month": added_this_month,
                "this_year": added_this_year
            },
            "projects": list(projects_dict.values()),
            "user_profile": {
                "name": "Boris Meldre",
                "first_name": "Boris",
                "last_name": "Meldre",
                "username": "borismeldre",
                "email": "borismeldre@gmail.com",
                "person_id": "83911"
            },
            "latest_observation": latest_obs
        },
        "taxa": taxa_registry,
        "observations": observations
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Eksport edukas: {len(observations)} vaatlust ja {len(taxa_registry)} taksonit salvestatud faili {OUTPUT_JSON}")
    print(f"Herbaariumikirjeid: {specimen_stats["total"]} (DNA: {specimen_stats["dna"]}, Herbaarium: {specimen_stats["herbaarium"]}, Mikroskoopia: {specimen_stats["mikroskoopia"]})")
    print(f"Faili suurus: {os.path.getsize(OUTPUT_JSON) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
