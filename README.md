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

---

## Ühtne Kaardivõrgustik ja Märgendid

Kõik 768 vaatlust kuvatakse ühtses minimalistlikus võrgustikus. Kaasvaatlustel on foto/kaardi ülanurgas selge kontrastne märgis **`KAASVAATLEJA`** ning all autori nimi (nt *Autor: Allar Antson*).

---

## Sorteerimise Loogika

Vaikimisi sorteeritakse kõik vaatlused **sisestamise aja järgi (Viimati lisatud süsteemi / `created_at DESC`)**, mis tagab, et terminalist või PlutoF-ist värskelt sisestatud vaatlus on koheselt esikohal.

Kasutaja saab rippmenüüst valida:
- **Viimati lisatud (Uusimad ees)**
- **Leiu kuupäev (Uusimad ees)**
- **Liiginimi (A-Z)**

---

## Vaatluste Kinnituse Staatused (Kinnitatud vs Ootel)

Arhiivis peetakse arvestust määramise kinnituse üle:
- **Kinnitatud (586 vaatlust):** Eksperdi (nt Irja Saar) poolt modereeritud ja kinnitatud vaatlused.
- **Ootel (185 vaatlust):** Äsja või varem sisestatud vaatlused, mis ootavad PlutoF süsteemis eksperdi kinnitust.

Kõikidel kaartidel kuvatakse vastav märgend (`Kinnitatud` või `Ootel`). Lisaks on vasakul paneelis filtri rippmenüü staatuse järgi sorteerimiseks.

---

## Ootel Märgendi Positsioneerimine

Märgis **`OOTEL`** on eemaldatud alumisest siltide reast ja viidud kaardi/foto ülemisse paremasse nurka selgelt eraldatud staatuseindikaatorina.

---

## Täielik Fotoarhiiv (646 Fotot)

Kõikidele vaatlustele (sh kaasvaatlused ja ühisretked) on imporditud Tartu Ülikooli HPC S3 serveri ametlikud kõrglahutusega fotod. 774 vaatlusest omavad fotot **646 vaatlust** (215 peavaatlust ja 431 kaasvaatlust).
