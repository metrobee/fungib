# INCIDENTS.md — PlutoFF Dashboard Süsteemsete Vigade Register

## Intsidentide Kroonika

### [INCIDENT-2026-08-20-PLUTOFF-THUMBNAIL-404] Pisipiltide HTTP 404 Viga Tartu Ülikooli HPC S3 Serveris
- **Kuupäev**: 20. august 2026
- **Sümptom**: PlutoFF veebidashboardi (`fungib.web.app`) avavaates kuvati kaartide fotode asemel tühi ala või alt-tekst, kuigi modaalis pilt avanes.
- **Algpõhjus (RCA)**: Andmeeksport proovis tuletada pisipildi URL-i asendusega `/large/` -> `/thumbnail/`. TÜ HPC S3 serveris aga `/thumbnail/` alamkausta ei eksisteeri, mistõttu brauser sai staatilise HTTP 404 (Not Found) vastuse.
- **Püsiv lahendus**: Andmeekspordis ja esiosas seadistati piltide universaalseks allikaks otse ametlik ja toimiv `/large/` fotolink (`https://s3.hpc.ut.ee/plutof-public/large/...`).

---

### [INCIDENT-2026-08-20-LOCAL-FILEPATH-EXPOSURE] Kohalike Failiteede Asendamine Ametlike S3 Linkidega
- **Kuupäev**: 20. august 2026
- **Sümptom**: Viimati lisatud 33 vaatluse fotod ei avanenud veebis.
- **Algpõhjus (RCA)**: `seen` CLI salvestas esialgu kohaliku arvuti failitee (`/Users/.../Downloads/...`), mida veebibrauser ei saa laadida.
- **Püsiv lahendus**: PlutoF API faili ID-de (`plutof_file_id`) kaudu tehti päringud, mis tuvastasid ja salvestasid avalikud S3 lingid `https://s3.hpc.ut.ee/plutof-public/large/...`.
