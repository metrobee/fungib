# PLUTOFF Mycology Archive (Fungib)

Executive minimalistlik ja suure jõudlusega mükoloogiline arhiiv ja reaalajas veebidashboard.

- **Veebiaadress:** https://fungib.web.app
- **Lähtekood:** https://github.com/metrobee/fungib

---

## 1. Arhitektuur ja Komponendid

- **Frontend:** Puhas natiivne Vanilla JS ja modulaarne CSS ilma väliste raamistiketa.
- **Kaardirakendus:** Leaflet.js koos CartoDB Positron (Light) ja CartoDB Dark Matter (Dark) kihtidega.
- **Andmebaas ja ladu:** SQLite (`/Users/metrobee/GEMINI/data/plutof_vaatlused.db`) ja Tartu Ülikooli HPC S3 pilveserver (`https://s3.hpc.ut.ee/plutof-public/large/...`).
- **Terminali CLI (`seen`):** macOS natiivne fotode töötlemine (`sips` HEIC konverteerimine), EXIF metaandmete väljalugemine ja automaatne taustajuurutus.

---

## 2. Vaatluste ja Fotode Arhiiv

- **Vaatlusi kokku:** 774 vaatlust
- **Erinevaid liike:** 464 liiki
- **Fotodega vaatlusi:** 646 vaatlust (sh 215 peavaatlust ja 431 kaasvaatlust)
- **Eestikeelsed liiginimed:** 600+ taksoni sõnastik ClipSnippet baasil.

---

## 3. Funktsionaalsus ja Kasutajaliides

1. **Ühtne integreeritud vaade:**
   - Kõik vaatlused kuvatakse ühtses võrgustikus.
   - Kaasvaatlustel on foto ülanurgas selge kontrastne märgis `KAASVAATLEJA` ja all autori nimi.
2. **Kinnituse staatused:**
   - **`OOTEL`:** kuvatakse silmatorkava märgina foto ülemises paremas nurgas vaatlustel, mis ootavad eksperdi kinnitust.
   - **`Kinnitatud (Irja Saar jt)`:** kuvatakse eksperdi poolt kinnitatud vaatlustel.
3. **Sorteerimine:**
   - Vaikimisi: **Viimati lisatud (Sisestamise aeg / `created_at DESC`)**.
   - Valikud: **Leiu kuupäev (Uusimad ees)** ja **Liiginimi (A-Z)**.
4. **Otsing ja Filtrid:**
   - Reaalajas otsing (kiirklahv `/`): otsib eesti tavanime, teadusliku nime, kaaslaste, substraadi ja asukoha järgi.
   - Filtrid: Roll (*Kõik / Minu / Kaasvaatleja*), Staatus (*Kõik / Kinnitatud / Ootel*), Autor, Maakond ja Substraat.
5. **Ühisvaatluste värskuse indikaator:**
   - Päiseribal kuvatakse reaalajas viimase kaasvaatluste impordi vanus (nt `Värske (äsja uuendatud)` või `X päeva tagasi`).

---

## 4. Deduplikatsioon ja Apple Photos tugi

- **Kolmetasemeline deduplikatsioon (`seen_cli.py`):**
  1. SHA-256 failiräsi kontroll.
  2. Failinime kontroll.
  3. EXIF kuupäeva/kellaaja ja 5-komakohalise GPS-koordinaadi ristkontroll.
- **Apple Photos otsetugi:** Fotosid saab kopeerida otse macOS Photos rakendusest vahemällu ja kleepida terminali. Isegi kui failinimi on `Photos Library.photoslibrary/resources/derivatives/...`, hoiab süsteem ära topeltkirjed täpse GPS ja ajatempli alusel.
