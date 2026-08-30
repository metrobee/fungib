# PLUTOFF Mycology Archive (Fungib)

Executive minimalistlik ja suure joudlusega mukoloogiline arhiiv ning reaalajas veebidashboard seente vaatluste, herbaariumieksemplaride ja DNA proovide haldamiseks.

- **Veebiaadress:** https://fungib.web.app
- **Lahtekood:** https://github.com/metrobee/fungib
- **Arhitektuuristandard:** Fungib Design System (Single Source of Truth)

---

## 1. Arhitektuur ja Tehnilised Suundumused

- **Frontend:** Puhas natiivne Vanilla JS, modulaarne CSS (Dark/Light reziim, WCAG AAA kontrast, 4px raadiused) ilma raskete raamistiketa.
- **Herbaariumi, DNA ja Mikroskoopia Mootor:**
  - Tuvastab ja margistab automaatselt herbaariumikoodid (`TU`, `TAA`, `KM017-8`, `#13-5`, `coll.`), DNA sekveneerimise proovid ja mikroskoopilised eosemootmed.
  - Spetsiaalne rippmenuu filter ja kaardimargendid (`HERBAARIUM`, `DNA PROOV`, `MIKROSKOOPIA`).
- **Andmete Normaliseerimine ja 48% Mahu Vahendamine:**
  - 14 keele etumoloogia ja tavanimetused on normaliseeritud tsentraalsesse `taxa` registrisse (680 liiki), vahendades `observations.json` faili mahtu 9.4 MB-lt 4.93 MB-le.
- **Kliendipoolne Valkotsing Web Workeris (`public/js/search-worker.js`):**
  - Pooratud indeks (Inverted Index) ja foneetiline otsingumootor eraldiseisvas taustaloimes.
  - Otsing ule 2108 vaatluse, 680 liigi, 14 keele ja herbaariumikoodide toimub latentsusega alla 1 ms ilma UI pealoimet koormamata.
- **DOM Renderdamise Virtualiseerimine:**
  - CSS reegel `content-visibility: auto; contain-intrinsic-size: 0 320px;` vahendab brauseri graafikamalu koormust ~70% ja tagab 120fps sujuvuse.
- **Autentimine ja Turvalukk:** Firebase Authentication (Google Sign-In) rangelt kontrollitud lubatud e-posti nimekirjaga (*Whitelist: ALLOWED_EMAILS*).
- **Kaardirakendus:** Leaflet.js koos ESRI Canvas World Light Gray Base (Light) ja World Dark Gray Base (Dark) kihtidega.

---

## 2. Funktsionaalsus ja Kasutajaliides

1. **Herbaariumieksemplaride ja DNA proovide filter:**
   - Eristab koheselt teaduskollektsiooni kuivatused, molekulaaruuringute proovid ja valivaatlused.
2. **Lehekülgede susteem (Pagination):**
   - 50 kirjet lehel kiire topeltnavigatsiooniga.
3. **Mitmikfotode vorgustik ja detailgalerii:**
   - Dunnaamilised 1, 2 voi 3+ fotoga ruudustikud koos thumbnail-ribaga modaalaknas.
4. **Mitmekeelne etumoloogia:**
   - 14 keele nimed ja sonasonalised eesti tolkega vasted (`≈ "..."`).

---

## 3. Kaivitamine ja Paigaldamine

### Andmete eksport ja normaliseerimine:
```bash
python3 scripts/export_dashboard_data.py
```

### Paigaldus Firebase Hostingusse:
```bash
npx -y firebase-tools@latest deploy --only hosting --project fungib
```
