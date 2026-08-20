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
