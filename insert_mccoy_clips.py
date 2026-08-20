#!/usr/bin/env python3
"""
insert_mccoy_clips.py — Loeb Firebase'ist McCoy loengu tsitaadid
ja lisab need esitlusse (index.html) uue slaidina.

Kasutamine:
    python3 insert_mccoy_clips.py

Nõuab: pip install firebase-admin (või kasutab firebase CLI-d)
"""
import json
import subprocess
import sys
from datetime import datetime

INDEX_HTML_PATH = "/Users/metrobee/Projects/fungib/public/index.html"
FIREBASE_PROJECT = "sittkeeb-dd91f"
CLIPS_PATH = "/fungib_annotations/boris/presentation_clips"

def fetch_clips():
    """Fetch clips from Firebase RTDB"""
    result = subprocess.run(
        ["firebase", "database:get", CLIPS_PATH, "--project", FIREBASE_PROJECT],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Viga Firebase'ist lugemisel: {result.stderr}")
        return []
    
    data = json.loads(result.stdout)
    if not data:
        print("Pole tsitaate Firebase'is.")
        return []
    
    clips = []
    for clip_id, clip in sorted(data.items(), key=lambda x: x[1].get('added', 0)):
        clips.append(clip)
    
    return clips


def generate_slide_html(clips):
    """Generate a slide HTML block with McCoy quotes"""
    quotes_html = ""
    for clip in clips:
        text = clip.get('text', '')
        slide_title = clip.get('slideTitle', '')
        timestamp = clip.get('timestamp', '')
        quotes_html += f'''
                <div class="quote-block" style="border-left: 3px solid var(--accent-color); padding: 10px 15px; margin: 12px 0; background: rgba(46, 196, 182, 0.05); border-radius: 4px;">
                    <p style="font-style: italic; font-size: 1rem; line-height: 1.6; color: var(--sub-color);">"{text}"</p>
                    <p style="font-size: 0.8rem; color: #64748b; margin-top: 5px;">— Peter McCoy ({slide_title}, {timestamp})</p>
                </div>'''
    
    slide_html = f'''
<!-- Slaid: Peter McCoy tsitaadid (automaatselt lisatud {datetime.now().strftime("%Y-%m-%d %H:%M")}) -->
<div class="slide slide-content-card">
    <div class="content-area" style="display: flex; flex-direction: column; gap: 10px; padding: 30px;">
        <h1 style="font-size: 1.8rem;">Peter McCoy mullaökoloogiast</h1>
        <h2 style="font-size: 1rem; color: var(--accent-color); margin-bottom: 10px;">Radical Mycology — Fungi in Soil Ecology</h2>
        {quotes_html}
        <p style="font-size: 0.75rem; color: #475569; margin-top: auto;">Allikas: youtube.com/watch?v=Tcy-KcMkhKU | Sustainable Design Master Class</p>
    </div>
</div>
'''
    return slide_html


def insert_slide(slide_html):
    """Insert the new slide before the last slide in index.html"""
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find the last </div> of slide-deck (before closing slide-deck div)
    # Insert before the last slide (which is usually credits/thank you)
    marker = '</div>\n<!-- END SLIDE DECK -->'
    
    if marker in html:
        html = html.replace(marker, slide_html + '\n' + marker)
        print(f"✅ Slaid lisatud (marker: END SLIDE DECK)")
    else:
        # Fallback: insert before </div></div> at end of slide-deck
        # Find last occurrence of closing slide div
        last_slide_end = html.rfind('</div>\n</div>\n</div>')
        if last_slide_end > 0:
            html = html[:last_slide_end] + slide_html + '\n' + html[last_slide_end:]
            print(f"✅ Slaid lisatud (fallback positsioon)")
        else:
            print("❌ Ei leidnud sobivat kohta slaidi lisamiseks!")
            print("   Lisa käsitsi index.html faili slide-deck sektsiooni.")
            print(f"\nGenereeritud HTML:\n{slide_html}")
            return False
    
    with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return True


def main():
    print("🍄 McCoy tsitaatide lisamine esitlusse")
    print("=" * 50)
    
    # 1. Fetch clips
    clips = fetch_clips()
    if not clips:
        return
    
    print(f"\n📋 {len(clips)} tsitaati leitud:")
    for i, c in enumerate(clips, 1):
        print(f"   {i}. \"{c.get('text', '')[:60]}...\"")
    
    # 2. Generate slide
    slide_html = generate_slide_html(clips)
    
    # 3. Ask confirmation
    print(f"\n📝 Genereerin uue slaidi {len(clips)} tsitaadiga.")
    answer = input("   Lisa see index.html-i? [y/N]: ").strip().lower()
    if answer != 'y':
        print("Katkestatud. Siin on genereeritud HTML:")
        print(slide_html)
        return
    
    # 4. Insert
    if insert_slide(slide_html):
        print(f"\n✅ Valmis! Slaid lisatud faili: {INDEX_HTML_PATH}")
        print("   Järgmised sammud:")
        print("   1. firebase deploy --only hosting   (deploy veebilehele)")
        print("   2. python3 sync_to_pptx.py          (sync PowerPointi)")
    

if __name__ == '__main__':
    main()
