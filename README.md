# PLUTOFF Mycology Archive (Fungib)

Executive minimalistlik ja suure jõudlusega mükoloogiline arhiiv ja reaalajas veebidashboard.

- **Veebiaadress:** https://fungib.web.app
- **Lähtekood:** https://github.com/metrobee/fungib

---

## 1. Arhitektuur ja Komponendid

- **Frontend:** Puhas natiivne Vanilla JS, modulaarne CSS (Dark/Light mode, 50-kirjeline lehekülgede süsteem ja mobiilitugi) ilma väliste raamistiketa.
- **Kaardirakendus:** Leaflet.js koos CartoDB Positron ja Dark Matter kihtidega.
- **Andmebaas:** SQLite andmebaasist eksporditav staatiline JSON (`public/data/observations.json`).
- **Automaatne sünkroon:** GitHub Actions töövoog (`.github/workflows/sync_plutof.yml`) PlutoF andmete automaatseks eksportimiseks ja majutamiseks.

---

## 2. Kiire paigaldus ja seadistamine (Quick Start)

Kui soovid luua endale samasuguse PlutoF vaatluste veebiarhiivi:

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

### 3. Ekspordi andmed veebilehe jaoks
Käivita ekspordiskript, mis genereerib faili `public/data/observations.json`:
```bash
python3 scripts/export_dashboard_data.py
```

### 4. Majuta veebileht (Tasuta)

- **GitHub Pages (Soovitatav):**
  1. Lükka kood oma GitHubi repositooriumisse.
  2. Mine `Settings -> Pages -> Branch: main -> Folder: /public` ja salvesta.
  3. Leht on koheselt üleval aadressil `https://<kasutajanimi>.github.io/fungib/`.

- **Firebase Hosting:**
  ```bash
  firebase init hosting   # Vali kaustaks 'public'
  firebase deploy --only hosting
  ```

---

## 3. Funktsionaalsus ja Kasutajaliides

1. **50-kirjeline lehekülgede süsteem (Pagination):** Vaatlused on jaotatud mugavateks lehekülgedeks koos kiire navigatsiooniga.
2. **Kinnituse staatused:**
   - **`OOTEL`:** kuvatakse vaatlustel, mis ootavad eksperdi kinnitust.
   - **`Kinnitatud`:** kuvatakse eksperdi poolt määratud ja kinnitatud vaatlustel.
3. **Sorteerimine:** Viimati lisatud (`created_at DESC`), Leiu kuupäev (`date DESC`) ja Liiginimi (A-Z).
4. **Reaalajas otsing ja filtrid:** Otsing kiirklahviga `/`, filtrid rolli (*Kõik / Minu / Kaasvaatleja*), staatuse, autori, maakonna ja substraadi järgi.
5. **Mobiilne optimeerimine:** Täielikult kohanduv disain (Pixel 9a ja nutiseadmete portreevaade).

