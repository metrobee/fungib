#!/usr/bin/env python3
"""
create_slides_presentation.py — Loob Google Slides esitluse McCoy tsitaatide põhjal.
"""
import os
import json
import subprocess
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive']
CLIENT_SECRET = '/Users/metrobee/Projects/realtime-veebis/client_secret_903136773415-32vkc2o5482in9r5nabq4gd1c6podceg.apps.googleusercontent.com.json'
TOKEN_FILE = '/Users/metrobee/Projects/fungib/.slides_token.json'

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds

def fetch_clips():
    result = subprocess.run(
        ["firebase", "database:get", "/fungib_annotations/boris/presentation_clips", "--project", "sittkeeb-dd91f"],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    if not data:
        return []
    return [v for v in sorted(data.values(), key=lambda x: x.get('added', 0))]

def create_presentation(service, clips):
    """Create a new Google Slides presentation with the lecture outline"""
    
    # Create presentation
    presentation = service.presentations().create(body={
        'title': 'Seeneriigi Nähtamatud Niidid — Boris Meldre'
    }).execute()
    pres_id = presentation['presentationId']
    print(f"✅ Esitlus loodud: https://docs.google.com/presentation/d/{pres_id}")
    
    # Define slides structure
    slides_content = [
        {"title": "Seeneriigi Nähtamatud Niidid", "subtitle": "Müstika, pärimus ja maa-alune võrgustik\n\nLektor: Boris Meldre"},
        {"title": "Kuidas olla rohkem nagu seen?", "body": "• Sügav kuulamine, infomürast vabanemine\n• Mütseeli vaikus — ühendused nähtamatul tasandil\n• Teiste organismide toetamine\n• Koostöö, mitte konkurents"},
        {"title": "Mis on seen tegelikult?", "body": "• Mütseel on seene keha, viljakeha on vaid \"õis\"\n• 1.5–6 miljonit liiki, nimetatud vaid 75,000 (1-5%)\n• Eukarüoot: kitiinist rakusein, väline seedimine\n• \"Neglected mega science\" — unustatud megateadus"},
        {"title": "Samblikud ja mulla sünd", "body": "• Samblikud = 95% seenekude\n• Esimesed mullad Maal — 551-635 miljonit aastat tagasi\n• Seente happed lagundavad kivimeid → mineraalid → muld\n• Tänaseni esimesed laavavoolul ja maalihetel"},
        {"title": "Mükoriisa — Seene ja taime liit", "body": "• 90-95% taimedest moodustavad selle suhte\n• 450 miljonit aastat vana partnerlus\n• 1 gramm mulda = 1 miil mütseeli\n• 1 m² mullas seente pindala = 90 m²\n• Taimed ei elaks ilma seenteta looduses"},
        {"title": "\"Wood Wide Web\" — Metsa internet", "body": "• Ühine mütseeli võrgustik (CMN) — sajad taimed ühendatud\n• Emataimelt beebitaimele suhkruid\n• Lehetäi rünnak → signaal → naabertaimed kaitsevad end\n• Toitainete intelligentne jagamine"},
        {"title": "Glomaliin — Mulla superliim", "body": "• Kleepuv valk AM seente mütseeli pinnal\n• Kestab 50+ aastat mullas (rauasisaldus)\n• Loob makroagregaate → mulla struktuur, vee hoidmine\n• ~1/3 kogu mulla süsinikust (humiinhapped vaid 8%)\n• Vähendab erosiooni, pärsib tulekahjusid"},
        {"title": "Seened — Looduse suurimad keemikud", "body": "• 90% kogu lagunemisest planeedil — seened\n• Ainult seened lagundavad ligniini (~2000 liiki)\n• Biomineralisatsioon: loovad mineraale mullas\n• Oksaal-, õun-, sidrunhape — vabastavad mineraalid kivist"},
        {"title": "Toitainete ringlus", "body": "• Fosfor: seened vabastavad looduslikult (peak P ~2033!)\n• Süsinik: seened annavad 98% CO₂-st mida taimed vajavad\n• Lämmastik: Laccaria sööb putukaid → 25% puu N-st\n• AM + Rhizobium = kolmepoolne sümbioos"},
        {"title": "Põimunud Elu — Merlin Sheldrake", "body": "• Intelligentsus ilma ajuta — otsuste langetamine, navigeerimine\n• Radikaalne sümbioos — indiviidi mõiste küsimärgi all\n• Elu kui protsess, mitte staatiline asi\n• \"Entangled Life\" — soovituslik lugemine"},
        {"title": "Mükoremediatsioon", "body": "• Trichoderma lagundab glüfosaati (Roundup) ja DDT-d\n• Iga plastiku matmiskatse — seened lagundavad alati!\n• Raskemetallide akumulatsioon (Cs-137 Tšernobõlis)\n• Isegi puhtast loodusest pärit seened lagundavad herbitsiide"},
        {"title": "Tšernobõli kiiritusseened", "body": "• Radiosüntees — seened kasutavad kiirgust energiaks\n• Melaniini-rikkad seened ISS-i katses\n• 40 aastat hiljem — Leccinum akumuleerib endiselt Cs-137\n• NASA uurib kiirguskaitseks kosmoses"},
        {"title": "Nõiaringid — Pärimus ja bioloogia", "body": "• Haldjate tantsuplatsid (pärimus) vs\n• Ringikujuline mütseeli kasv → N vabanemine (bioloogia)\n• Hiiu park, Nõmme — siniroheline rohurõngas\n• Inimene küsib: \"Mis kemikaal tapab?\" vs teadus: \"Kasulik!\""},
        {"title": "Puuseente vägi", "body": "• Must pässik (Chaga) — elujõud ja tuletael\n• Reishi vs Jänesvaabik — sama perekond, sarnane toime\n• Puuseente vaim saunarituaalides\n• Adaptogeensed seened stressi vastu"},
        {"title": "Praktiline mükoloogia sinu aias", "body": "• Trichoderma kompostikiirendajana (lihtne kasvatada)\n• Rodale protokoll: AM seente kasvatamine kodus\n• Kohalikud seened > imporditud (kohanemise eelis)\n• Ektomükoriisa puudele: Pisolithus, Laccaria"},
        {"title": "Müstika ja teadvus", "body": "• Kärbseseen pärimuses\n• Korilus kui meditatsioon ja ühendus loodusega\n• Seeneriik kui teadvuse lävepakk\n• Vaikus ja tähelepanu — seene õpetus"},
        {"title": "Lugemissoovitused", "body": "• Merlin Sheldrake — Entangled Life (Põimunud Elu)\n• Peter McCoy — Radical Mycology\n• Sandor Katz — The Art of Fermentation\n• René Redzepi — The Noma Guide to Fermentation\n• radicalmycology.com"},
        {"title": "Aitäh kuulamast! 🍄", "subtitle": "\"Fungi sort of sculpt our environments — they fundamentally\ndetermine what plants and animals can live there.\"\n— Peter McCoy\n\nKüsimused?"},
    ]
    
    # Build batch requests
    requests = []
    
    for i, slide_data in enumerate(slides_content):
        if i == 0:
            # First slide already exists, just update it
            first_slide_id = presentation['slides'][0]['objectId']
            # Update title
            for element in presentation['slides'][0]['pageElements']:
                if 'shape' in element and element['shape'].get('shapeType') == 'TEXT_BOX':
                    pass  # We'll handle the first slide separately
            continue
        
        # Create new slide
        slide_id = f'slide_{i:03d}'
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'insertionIndex': i,
                'slideLayoutReference': {'predefinedLayout': 'TITLE_AND_BODY' if 'body' in slide_data else 'TITLE_ONLY'}
            }
        })
    
    # Execute slide creation
    if requests:
        service.presentations().batchUpdate(presentationId=pres_id, body={'requests': requests}).execute()
    
    # Now add text content to each slide
    presentation = service.presentations().get(presentationId=pres_id).execute()
    
    text_requests = []
    for i, slide in enumerate(presentation['slides']):
        if i >= len(slides_content):
            break
        content = slides_content[i]
        
        for element in slide['pageElements']:
            if 'shape' not in element:
                continue
            shape = element['shape']
            placeholder = shape.get('placeholder', {})
            ph_type = placeholder.get('type', '')
            obj_id = element['objectId']
            
            if ph_type in ('TITLE', 'CENTERED_TITLE'):
                text_requests.append({
                    'insertText': {'objectId': obj_id, 'text': content.get('title', ''), 'insertionIndex': 0}
                })
            elif ph_type in ('SUBTITLE', 'BODY'):
                body_text = content.get('body', content.get('subtitle', ''))
                if body_text:
                    text_requests.append({
                        'insertText': {'objectId': obj_id, 'text': body_text, 'insertionIndex': 0}
                    })
    
    if text_requests:
        service.presentations().batchUpdate(presentationId=pres_id, body={'requests': text_requests}).execute()
    
    return pres_id


def main():
    print("🍄 Seeneriigi esitluse loomine Google Slides'is")
    print("=" * 50)
    
    # Auth
    print("\n1. Autoriseerime Google Slides API...")
    creds = get_credentials()
    service = build('slides', 'v1', credentials=creds)
    
    # Fetch clips for reference
    clips = fetch_clips()
    print(f"   {len(clips)} tsitaati Firebase'is")
    
    # Create
    print("\n2. Loon esitluse...")
    pres_id = create_presentation(service, clips)
    
    print(f"\n🎉 Valmis!")
    print(f"   Ava: https://docs.google.com/presentation/d/{pres_id}/edit")


if __name__ == '__main__':
    main()
