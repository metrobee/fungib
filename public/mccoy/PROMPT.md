# McCoy Lecture Annotate Tool – PROMPT

## Mis see on?

Interaktiivne õppetööriist Peter McCoy "Fungi in Soil Ecology" loengu jaoks. Võimaldab teksti markeerida, märkmeid lisada ja AI abil teaduslikku tõendust leida.

**Live:** https://fungib.web.app/mccoy/annotate

## Arhitektuur

- **Frontend:** Single HTML file (`public/mccoy/annotate.html`) + eraldatud slaidide andmed (`slides_data.js`)
- **Hosting:** Firebase Hosting (projekt: `fungib`)
- **Andmebaas:** Firebase Realtime Database (projekt: `sittkeeb-dd91f`, tee: `/fungib_annotations/{userId}/mccoy`)
- **Auth:** Google Sign-In (Firebase Auth, sittkeeb-dd91f)
- **AI:** Gemini 2.5 Flash API (võti hardcoded — hiljem peaks liikuma serverile)

## Funktsioonid

### 1. Teksti markeerimine (Highlighting)
- Selekteeri tekst → ilmub popup
- 4 värvi: kollane, roheline, sinine, roosa
- Salvestub Firebase RTDB-sse reaalajas

### 2. Märkmete lisamine (Notes)
- Selekteeri tekst → "📝 Add Note"
- Prompt küsib märkme teksti
- Highlight saab `title` atribuudi (hover tooltip)
- Salvestub RTDB-sse

### 3. Teadusliku tõenduse otsing (Find Evidence)
- Selekteeri väide → "🔬 Find Scientific Evidence"
- Gemini 2.5 Flash otsib 3-5 peer-reviewed artiklit
- Kuvab tsitaadid, kokkuvõtted, DOI lingid
- Salvestub RTDB-sse annotation'i juurde

## Firebase RTDB struktuur

```json
{
  "fungib_annotations": {
    "USER_UID": {
      "mccoy": {
        "ann_1720000000000": {
          "text": "highlighted text",
          "color": "yellow",
          "slideIdx": "5",
          "created": 1720000000000,
          "note": "minu märge",
          "evidence": [
            {
              "citation": "Author et al. (2020). Title. Journal.",
              "summary": "Supports the claim because...",
              "doi": "10.1234/..."
            }
          ]
        }
      }
    }
  }
}
```

## RTDB reeglid

Tee `/fungib_annotations` on sittkeeb-dd91f `database.rules.json`-is:
```json
"fungib_annotations": {
  "$userId": {
    ".read": "$userId === auth.uid",
    ".write": "$userId === auth.uid"
  }
}
```

## Failide struktuur

```
public/mccoy/
├── annotate.html          ← Interaktiivne õppetööriist
├── index.html             ← Eesti kokkuvõte + slaidid
├── index_en.html          ← Inglise täistekst + slaidid
├── slides_data.js         ← 27 slaidi andmed (JS array)
├── transcript_en.md       ← Markdown transkriptsioon
├── peter_mccoy_fungi_soil_ecology.pdf  ← PDF NotebookLM jaoks
├── 01_title.jpg           ← Slaidipildid (27 tk)
├── 02_soil_builders_of_old.jpg
├── ...
└── 27_radical_mycology_book.jpg
```

## Teadaolevad piirangud

1. **Highlight'ide taastamine** pärast lehe uuesti laadimist ei tööta (teksti positsioonide salvestamine vajab keerukamat lahendust — nt XPath-based range serialization)
2. **Gemini API võti** on kliendipoolses koodis (turvarisk) — tootmises peaks olema Firebase Cloud Function proxy
3. **Ühe kasutaja** andmed — ei ole jagamisvõimalust teiste kasutajatega

## Deploy

```bash
cd /Users/metrobee/Projects/fungib
firebase deploy --only hosting
```

## Gemini API

- Mudel: `gemini-2.5-flash`
- `thinkingBudget: 0` (vajalik et väljundit ei lõigataks)
- `maxOutputTokens: 4096`
- Vastuse formaat: JSON array, puhastatud ` ```json ` wrappingust

## Allikas

- Video: https://www.youtube.com/watch?v=Tcy-KcMkhKU
- Esineja: Peter McCoy (Radical Mycology)
- Raamat: "Radical Mycology: A Treatise on Seeing & Working With Fungi"
- Veebileht: radicalmycology.com
