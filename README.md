# PLUTOFF Mycology Archive (Fungib)

Executive minimalistlik ja suure jõudlusega mükoloogiline arhiiv ja reaalajas veebidashboard.

- **Veebiaadress:** https://fungib.web.app
- **Lähtekood:** https://github.com/metrobee/fungib

---

## 1. Arhitektuur ja Komponendid

- **Frontend:** Puhas natiivne Vanilla JS, modulaarne CSS (Dark/Light mode, mobiilne kohanduvus) ilma väliste raamistiketa.
- **Autentimine ja Turvalukk:** Firebase Authentication (Google Sign-In) rangelt kontrollitud lubatud e-posti nimekirjaga (*Whitelist: `ALLOWED_EMAILS`*).
- **Lehekülgede süsteem (Pagination):** 50 kirjet lehel, kiire topeltnavigatsiooniga (loendi alguses ja lõpus) ning sujuva kerimisega.
- **Kaardirakendus:** Leaflet.js koos ESRI Canvas World Light Gray Base (Light) ja World Dark Gray Base (Dark) kihtidega (puhtad, ilma vesimärkideta ja kiire laadimisega).
- **Dünaamiline Mitmikfotode Võrgustik (Multi-Photo Layouts):**
  - **1 foto:** Üksik täismõõdus eelvaatepilt.
  - **2 fotot:** 2-veeruline kõrvuti jaotus (50% / 50%), võimaldades kohe näha nii seene kübarat kui ka eoslehekesi/torikuid.
  - **3+ fotot:** Hero-põhine fotovõrgustik (60% peafoto + 2 lisafotot) koos diskreetse looriga `+N FOTOT` ja kaardi arvu tähisega.
- **Interaktiivne Detailgalerii (Modal Gallery):**
  - Suur kõrgresolutsioonis peafoto koos klikitava täissuuruses vaatega.
  - Interaktiivne pisipiltide riba (*thumbnail strip*), millel klõpsates vahetub peafoto koheselt.
  - Reaalajas fotode indeks (*nt Foto 1 / 4*).
- **Mitmekeelne Taksonoomiamootor ja Sõnasõnaline Etümoloogia:**
  - Ühendab PlutoF/eElurikkuse, Laji.fi (FinBIF), Dyntaxa (SLU), iNaturalist (vene keel) ja Wikidata/GBIF registrid 14 keeles.
  - Iga võõrkeelse seenenime all kuvatakse selle sõnasõnaline (toores) etümoloogiline tõlge eesti keelde (`≈ "..."`).
- **Projektide ja Uuringute Seostamine:**
  - Tugi projektipõhisele filtreerimisele ja automaatsele sidumisele (*nt 2023 Autumn Mushroom Foray, Karula praktikum*).
- **Andmebaas:** SQLite andmebaasist genereeritav optimeeritud JSON (`public/data/observations.json`).
- **Automaatne sünkroon:** GitHub Actions töövoog (`.github/workflows/sync_plutof.yml`) PlutoF andmete automaatseks eksportimiseks ja majutamiseks.

---

## 2. Kiire paigaldus ja seadistamine (Quick Start)

Kui soovid luua endale või sõbrale samasuguse PlutoF vaatluste veebiarhiivi:

### 1. Klooni repositoorium
```bash
git clone https://github.com/metrobee/fungib.git
cd fungib
```

### 2. Seadista PlutoF konto andmed
Lisa faili `~/.plutof_env`:
```bash
PLUTOF_CLIENT_ID="sinu_client_id"
PLUTOF_CLIENT_SECRET="sinu_client_secret"
PLUTOF_USERNAME="sinu_kasutajanimi"
PLUTOF_PASSWORD="sinu_parool"
```

### 3. Määra lubatud kasutaja (Auth Whitelist)
Failis `public/app.js` määra oma Google'i e-posti aadress:
```javascript
const ALLOWED_EMAILS = ["sinu_email@gmail.com"];
```

### 4. Ekspordi andmed veebilehe jaoks
Käivita andmete eksport:
```bash
python3 scripts/export_dashboard_data.py
```

### 5. Majuta veebileht (Tasuta)

- **Firebase Hosting (Soovitatav Google Auth toega):**
  ```bash
  npm install -g firebase-tools
  firebase login
  firebase init hosting   # Vali kaustaks 'public'
  firebase deploy --only hosting
  ```

- **GitHub Pages (Avalikuks versiooniks):**
  1. Lükka kood oma GitHubi repositooriumisse.
  2. Vali `Settings -> Pages -> Branch: main -> Folder: /public` ja salvesta.
  3. Leht on koheselt üleval aadressil `https://<kasutajanimi>.github.io/fungib/`.

---

## 3. Funktsionaalsus ja Kasutajaliides

1. **Turvaline sisselogimine (Auth Gate):**  
   Lehele minnes nõutakse Google'iga sisselogimist. Ainult määratud meiliaadressiga kasutajale avatakse arhiivi sisu.
2. **50-kirjeline lehekülgede süsteem:**  
   Suuremahulised vaatlusandmed on jagatud 50 kaupa lehekülgedeks, mis tagab ülikiire laadimise ja sujuva mobiilse kasutuskogemuse.
3. **Kinnituse staatused ja rollid:**
   - **`OOTEL`:** kuvatakse vaatlustel, mis ootavad eksperdi määramist.
   - **`Kinnitatud`:** kuvatakse eksperdi poolt kinnitatud vaatlustel.
   - **`KAASVAATLEJA`:** selge eristus kaasvaatlustele koos algse autori nimega.
4. **Sorteerimine ja reaalajas otsing:**  
   Sorteerimine sisestusaja, leiuaja ja tähestiku järgi. Reaalajas otsing (`/` kiirklahviga) taksoni, kaaslase, koha või substraadi järgi.
5. **Mobiilne optimeerimine:**  
   100% kohanduv ja testitud kitsastel ekraanidel (Pixel 9a portreevaade), vältides igasugust horisontaalset ülevoolu.


