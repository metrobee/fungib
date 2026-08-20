# PlutoFF Mycology Dashboard (`fungib.web.app`)

> **Minimalistlik, monokroomne ja reaalajas mükoloogia veebidashboard seenevaatluste haldamiseks.**

Live veebirakendus: **[https://fungib.web.app](https://fungib.web.app)**

---

## Peamised Funktsioonid

1. **Monokroomne Light / Dark Disain:**
   - Rangelt kahevärviline: must, valge ja neutraalsed halltoonid.
   - Puhas tüpograafia (SF Pro / Inter / SF Mono).
   - 0 emotikoni ja 0 visuaalset müra.
2. **Interaktiivne GIS-kaart (Leaflet):**
   - CartoDB monokroomsed kaardikihid (`Positron` valges režiimis, `DarkMatter` tumedas režiimis).
   - 207+ ametlikku leiukohta üle Eesti koos detailse infoga.
3. **Reaalajas otsing ja filtrid:**
   - Otsing taksoni ladina ja eesti nime, substraadi, asukoha ja ID järgi (kiirklahv `/`).
   - Rippfiltrid maakondade ja substraatide järgi.
4. **Detailne vaatlusvaade (Modal):**
   - Tartu Ülikooli HPC S3 kõrglahutusega fotod.
   - Täpsed GPS koordinaadid (5 komakohta).
   - PlutoF Vormi 72 mõõtmised (puuliik, substraadi tüüp, viljakehade ohtrus).
   - Otselink ametlikule PlutoF lehele.
5. **Automaatne sünkroon:**
   - `seen` käsk terminalis värskendab automaatselt `public/data/observations.json` andmestikku.

---

## Arhitektuur ja Tehnoloogiad

- **Frontend:** Vanilla JS (ES6+), modulaarne CSS, Leaflet 1.9.4.
- **Hosting:** Firebase Hosting (`fungib.web.app`).
- **Andmeallikas:** PlutoF API & Tartu Ülikooli HPC S3 fotoladu.

---

## Paigaldus ja Käivitamine Kohapeal

```bash
# Klooni repo
git clone https://github.com/metrobee/fungib.git
cd fungib

# Uuenda andmestikku
python3 scripts/export_dashboard_data.py

# Juuruta Firebase Hostingusse
firebase deploy --only hosting
```

---

## Litsents

MIT License. Boris Meldre, 2026.

---

## Otsing ja Sektsioonide Jaotus

Otsingutulemused on visuaalselt jagatud kaheks selgeks plokiks:
1. **Minu sisestatud vaatlused:** Esmased vaatlused koos kõrglahutusega fotodega.
2. **Kaasvaatlused ja ühisretked:** Vaatlused, kus kasutaja on märgitud kaasvaatlejaks (kuvab peavaatleja nime, määraja, asukoha ja otselingi).
