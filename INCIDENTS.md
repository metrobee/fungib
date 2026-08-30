# INCIDENTS.md — PlutoFF Dashboard Süsteemsete Vigade Register

## Intsidentide Täielik Kroonika

### [INCIDENT-2026-08-20-HEIC-NATIVE-PILLOW-FAIL] iPhone HEIC Fotode Tugi ja Automaatne macOS SIPS Konverteerimine
- **Kuupäev**: 20. august 2026
- **Sümptom**: iPhone'i `.HEIC` foto edastamisel käsklusele `seen` tagastati viga: `cannot identify image file ... .HEIC` ning GPS metaandmeid ei tuvastatud.
- **Algpõhjus (RCA)**: Pythoni standardne `Pillow` teek ei toeta Apple'i HEIC-formaati ilma eraldi kompileeritud `pillow-heif` moodulita.
- **Püsiv lahendus**: Integreeritud macOS-i natiivne `sips` mootor (`sips -s format jpeg ...`), mis teisendab HEIC pildi taustal ajutiseks JPEG failiks ilma süsteemi lisapakette vajamata. Tulemusena säilivad 100% täpsed GPS koordinaadid, kõrgus ja kuupäev ning pilt laetakse PlutoF serverisse.

---

### [INCIDENT-2026-08-20-ZSH-BRACKETED-PASTE-ERROR] Terminali Bracketed Paste Märgendi [200~ Tekitatud Zsh Bad Pattern Tõrge
- **Kuupäev**: 20. august 2026
- **Sümptom**: Faili lohistamisel terminali tekkis viga: `zsh: bad pattern: [200~/Users/...`.
- **Algpõhjus (RCA)**: Terminali Bracketed Paste funktsioon lisas lohistatud tekstile ümber kontrollmärgid `[200~` ja `~`, mida Zsh tõlgendas regulaaravaldisena (*glob*).
- **Püsiv lahendus**: Koodi lisatud automaatne sisendi normaliseerimine (`.replace("[200~", "").replace("~", "")`), tagades lohistatud failiteede tõrgeteta töötlemise.

---

### [INCIDENT-2026-08-20-PLUTOFF-THUMBNAIL-404] Pisipiltide HTTP 404 Viga Tartu Ülikooli HPC S3 Serveris
- **Kuupäev**: 20. august 2026
- **Sümptom**: PlutoFF veebidashboardi (`fungib.web.app`) avavaates kuvati kaartide fotode asemel tühi ala või alt-tekst, kuigi modaalis pilt avanes.
- **Algpõhjus (RCA)**: Andmeeksport proovis tuletada pisipildi URL-i asendusega `/large/` -> `/thumbnail/`. TÜ HPC S3 serveris aga `/thumbnail/` alamkausta ei eksisteeri, mistõttu brauser sai staatilise HTTP 404 (Not Found) vastuse.
- **Püsiv lahendus**: Andmeekspordis ja esiosas seadistati piltide universaalseks allikaks otse ametlik ja toimiv `/large/` fotolink (`https://s3.hpc.ut.ee/plutof-public/large/...`).

---

### [INCIDENT-2026-08-20-LOCAL-FILEPATH-EXPOSURE] Kohalike Failiteede Asendamine Ametlike S3 Linkidega
- **Kuupäev**: 20. august 2026
- **Sümptom**: Viimati lisatud vaatluste fotod ei avanenud veebis.
- **Algpõhjus (RCA)**: `seen` CLI salvestas esialgu kohaliku arvuti failitee (`/Users/.../Downloads/...`), mida veebibrauser ei saa laadida.
- **Püsiv lahendus**: PlutoF API faili ID-de (`plutof_file_id`) kaudu tehti päringud, mis tuvastasid ja salvestasid avalikud S3 lingid `https://s3.hpc.ut.ee/plutof-public/large/...`.


## [INCIDENT-2026-08-20-CO-OBSERVATION-IMAGE-IMPORT]
- **Sümptom:** Kaasvaatluste (Allar Antson, Piret Lõhmus jt) kaartidel kuvati "Foto puudub", kuigi fotod olid PlutoF-is olemas.
- **Algpõhjus (RCA):** PlutoF standardne otsingueksport jättis vaikimisi veeru `Image URL` failist välja.
- **Lahendus:** Teostati täielik eksport 54 veeruga (sh `Image URL`), millest imporditi andmebaasi 432 uut S3 fotolinki. Nüüd omavad fotot 646 vaatlust 774-st.

## [INCIDENT-2026-08-20-DEFAULT-SORT-ORDER]
- **Sümptom:** Äsja terminalist sisestatud vaatlus (Aprikoosvöödik) ei ilmunud nimekirja algusesse.
- **Algpõhjus (RCA):** Nimekiri oli varem sorteeritud leiu kuupäeva järgi (`date_time DESC`), mistõttu 2021. aasta leiu foto paigutus 2021. aasta kirjete juurde.
- **Lahendus:** Muudeti vaikimisi sorteerimine sisestamise aja järgi (`created_at DESC`) ning lisati kasutajale sorteerimise rippmenüü.

## [INCIDENT-2026-08-20-PHOTOS-APP-CRASH-PREVENTION]
- **Süsteem:** `seen` CLI (`seen_cli.py`)
- **Sümptom:** Apple Photos rakendusest otse kopeeritud failide puhul tekkis Photos.app sulgumisviga.
- **Algpõhjus (RCA):** Skript liigutas Photos Library sisefaili prügikasti.
- **Püsiv Lahendus:** Lisatud `.photoslibrary` failikaitse `move_to_trash` funktsiooni.

## [INCIDENT-2026-08-20-HOMEBREW-RELEASE-V120]
- **Süsteem:** `plutoff` ja `homebrew-tap`
- **Tegevus:** Versioon uuendatud `v1.2.0` peale Homebrewis.

## [INCIDENT-2026-08-20-TAXON-MAPPING-AMBIGUITY]
- **Süsteem:** `seen` CLI
- **Sümptom:** `kahkjas mampel` valis vale sünonüümi/liigi.
- **Lahendus:** Eelistatakse alati kohalikku ClipSnippet teaduslikku nime. Välja antud `v1.2.1`.

## [INCIDENT-2026-08-20-TAIM-CLI-FORM-AND-AUTH-FIX]
- **Süsteem:** `taim` CLI
- **Sümptom:** Taimevormi viga lahendatud `Form 73` integratsiooniga. Välja antud `v1.3.1`.

## [INCIDENT-2026-08-20-TAIM-CLI-ISOLATION-AND-PRIVATE-REPO]
- **Arhitektuur:** `taim` CLI eraldatud privaatsesse repositooriumisse (`metrobee/taim`).

## [INCIDENT-2026-08-20-CLIPSNIPPET-BRACKETED-PASTE-CLEANUP]
- **Süsteem:** CLI ja Zsh
- **Lahendus:** Eemaldatud `^[[200~` koodid `clean_cli_arg` funktsiooniga ja `unset zle_bracketed_paste`.

## [INCIDENT-2026-08-20-KIVIPURAVIK-TAXON-MATCHING]
- **Süsteem:** `seen` CLI
- **Sümptom:** `kivipuravik` valis vale liigi (*Neoboletus*).
- **Lahendus:** Täiendatud sorteerimisloogikat ja lisatud sulgude tugi. Välja antud `v1.2.2`.

## [INCIDENT-2026-08-20-TAXA-CACHE-STALE-KIVIPURAVIK]
- **Süsteem:** `seen` CLI
- **Sümptom:** Vahemälust võeti vana vigane kirje.
- **Lahendus:** Vahemälu puhastatud ja parandatud vaatlus `#8318721`.

## [INCIDENT-2026-08-20-CO-OBSERVER-FLAG-SUPPORT]
- **Süsteem:** `seen` CLI
- **Funktsioon:** Lisatud `kaasv:aa` jms kaasvaatlejate lipud. Välja antud `v1.2.3`.

## [INCIDENT-2026-08-20-VELLO-LIIV-ALIAS-ADDED]
- **Süsteem:** `seen` CLI
- **Täiendus:** Lisatud `kaasv:vl` (*Vello Liiv* ID: 19681). Välja antud `v1.2.4`.

## [INCIDENT-2026-08-20-KV-PREFIX-AND-LEADING-COLONS]
- **Süsteem:** `seen` CLI
- **Täiendus:** Lisatud `kv:` ja `:kaasvaatleja:` formaatide tugi. Välja antud `v1.2.5`.

## [INCIDENT-2026-08-20-CO-OBSERVER-LIST-WHITESPACE-SPLIT]
- **Süsteem:** `seen` CLI
- **Lahendus:** Lubatud tühikud koma järel kaasvaatlejate loetelus (`kv:aa, vl`). Välja antud `v1.2.6`.

## [INCIDENT-2026-08-20-GENUS-LEVEL-OBSERVATIONS-SUPPORT]
- **Süsteem:** `seen` CLI
- **Täiendus:** Lisatud perekonna tasemel vaatluste tugi (`Ramaria sp.`, `ramaria`, `harik sp.`). Välja antud `v1.2.7`.

## [INCIDENT-2026-08-20-KIMP-SAMETKORGES-MAPPING]
- **Süsteem:** `seen` CLI
- **Lahendus:** Lisatud `kimp-sametkõrges` sidumine liigiga *Flammulina velutipes* (ID: 147778). Välja antud `v1.2.9`.

## [INCIDENT-2026-08-20-KIMP-METSKORGES-CONNOPUS]
- **Süsteem:** `seen` CLI
- **Lahendus:** `Kimp-metskõrges` seotud taksoniga *Connopus acervatus* (ID: 141001). Välja antud `v1.3.2`.

## [INCIDENT-2026-08-20-CSS-BRACE-SYNTAX-ERROR-AND-MOBILE-LAYOUT]
- **Süsteem:** `fungib.web.app` frontend
- **Sümptom:** Brauser kuvas unstyled HTML-i, kuna stiilifaili parsimine katkes.
- **Algpõhjus (RCA):** `[data-theme="dark"]` selektoril puudus sulgev loogeline sulg `}`, mistõttu CSS-parser luges terve faili vigaseks ja loobus stiilide rakendamisest.
- **Püsiv Lahendus:**
  1. Süntaks parandatud ja kontrollitud automaatse AST/braces parseriga.
  2. Versioon tõstetud `styles.css?v=4`.
  3. Juurutatud Firebase Hostingusse ja commititud GitHubi.

## [INCIDENT-2026-08-20-FIREBASE-AUTH-GATE-AND-DOCS-UPDATE]
- **Süsteem:** `fungib.web.app` frontend ja turvalisus
- **Funktsioon:** Lisatud Google Sign-In autentimisvärav (`ALLOWED_EMAILS = ['borismeldre@gmail.com']`), mis teeb arhiivi privaatseks.
- **Dokumentatsioon:** Uuendatud `README.md` koos täieliku paigaldus- ja seadistusjuhendiga uutele kasutajatele.

# INCIDENT LOGS & RCA (ROOT CAUSE ANALYSIS) - FUNGIB

## INCIDENT 004: Observations.json Payload Bloat & Lack of Herbarium Filtering
- **Kuupäev:** 2026-08-30
- **Sümptom:** `observations.json` faili suurus kasvas 9.4 MB-ni, kuna iga 2108 vaatluse juures dubleeriti 14 keele etümoloogilist sõnastikku (`vernacular_names`). Puudus spetsiaalne otsing ja filter teaduskollektsioonide (TU, TAA, DNA proovid, mikroskoopia) eristamiseks.
- **RCA:**
  1. Denormaliseeritud JSON struktuur tekitas ~4.5 MB tarbetut dubleerimist 680 liigi vahel.
  2. Herbaariumi ja DNA proovide metaandmed olid maetud vabatekstilistesse märkustesse ilma struktuurse tuvastuseta.
- **Püsiv Lahendus:**
  1. Normaliseeritud taksonite register `taxa`, vähendades failimahtu 48% (4.93 MB-ni).
  2. Implementeeritud `extract_specimen_info` mootor (tuvastab TU/TAA/KM koodid, DNA proovid, eosemõõdud).
  3. Lisatud kliendipoolne Web Worker välkotsing ja DOM virtualiseerimine (`content-visibility: auto`).
