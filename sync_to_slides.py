import os
import sys
from bs4 import BeautifulSoup
import google.auth
from googleapiclient.discovery import build

INDEX_HTML_PATH = "/Users/metrobee/Projects/fungib/public/index.html"
SLIDE_ID_FILE = "/Users/metrobee/Projects/fungib/.slides_id.txt"
BASE_IMAGE_URL = "https://fungib.web.app/"

# Dark mode colors
DARK_GREEN_BG = {'red': 0.055, 'green': 0.118, 'blue': 0.055} # #0e1f0e
LIGHT_GREEN_ACCENT = {'red': 0.435, 'green': 0.788, 'blue': 0.478} # #6fc97a
WHITE_COLOR = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
SUB_TEXT_COLOR = {'red': 0.7, 'green': 0.7, 'blue': 0.7}

def parse_html_slides():
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    slides_data = []
    slide_divs = soup.find_all('div', class_='slide')
    
    for i, div in enumerate(slide_divs):
        slide = {
            'is_title': 'slide-title-card' in div.get('class', []),
            'title': '',
            'subtitle': '',
            'meta': '',
            'bullets': [],
            'image': None
        }
        
        # Extract title
        h1 = div.find('h1')
        h2 = div.find('h2')
        if h1:
            slide['title'] = h1.get_text().strip()
        elif h2:
            slide['title'] = h2.get_text().strip()
            
        # Extract subtitle / meta / description
        if slide['is_title']:
            h2_sub = div.find('h2')
            if h2_sub and h1:
                slide['subtitle'] = h2_sub.get_text().strip()
            meta_p = div.find('div', class_='lecture-meta')
            if meta_p:
                slide['meta'] = meta_p.get_text(" | ").strip()
        else:
            p_desc = div.find('p')
            if p_desc:
                slide['subtitle'] = p_desc.get_text().strip()
                
            # Check for blockquote
            bq = div.find('blockquote')
            if bq:
                slide['bullets'].append(f'"{bq.get_text().strip()}"')
                
            # Check for list items
            lis = div.find_all('li')
            for li in lis:
                slide['bullets'].append(li.get_text().strip())
                
            # Check for image
            img = div.find('img')
            if img:
                src = img.get('src')
                if src and not src.startswith('http'):
                    slide['image'] = BASE_IMAGE_URL + src
                else:
                    slide['image'] = src
                    
        slides_data.append(slide)
    return slides_data

def sync_slides():
    print("Parsing slides from index.html...")
    slides_data = parse_html_slides()
    print(f"Parsed {len(slides_data)} slides.")
    
    # Authenticate
    try:
        credentials, _ = google.auth.default(scopes=[
            'https://www.googleapis.com/auth/presentations',
            'https://www.googleapis.com/auth/drive'
        ])
        slides_service = build('slides', 'v1', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"\n[VIGA] Autentimine ebaõnnestus: {e}")
        print("Palun käivita terminalis järgmine käsk ja logi oma Google kontoga sisse:")
        print("gcloud auth application-default login --scopes=https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform")
        return
        
    presentation_id = None
    if os.path.exists(SLIDE_ID_FILE):
        with open(SLIDE_ID_FILE, 'r') as f:
            presentation_id = f.read().strip()
            
    # Verify if existing presentation is still accessible
    if presentation_id:
        try:
            slides_service.presentations().get(presentationId=presentation_id).execute()
            print(f"Kasutan olemasolevat esitlust ID-ga: {presentation_id}")
        except Exception:
            print("Olemasolevat esitlust ei leitud või puudub ligipääs. Loon uue.")
            presentation_id = None
            
    if not presentation_id:
        body = {'title': 'Seeneriigi Nähtamatud Niidid'}
        pres = slides_service.presentations().create(body=body).execute()
        presentation_id = pres.get('presentationId')
        with open(SLIDE_ID_FILE, 'w') as f:
            f.write(presentation_id)
        print(f"Loodi uus esitlus ID-ga: {presentation_id}")
        
    # Get current presentation details to find slide IDs to delete later
    pres_info = slides_service.presentations().get(presentationId=presentation_id).execute()
    old_slide_ids = [s.get('objectId') for s in pres_info.get('slides', [])]
    
    # We will build new slides
    requests = []
    
    for idx, s in enumerate(slides_data):
        new_slide_id = f"slide_gen_{idx}"
        
        # 1. Create a blank slide
        requests.append({
            'createSlide': {
                'objectId': new_slide_id,
                'insertionIndex': idx,
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        })
        
        # 2. Set background color (Dark mode)
        requests.append({
            'updatePageProperties': {
                'objectId': new_slide_id,
                'pageProperties': {
                    'pageBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': DARK_GREEN_BG
                            }
                        }
                    }
                },
                'fields': 'pageBackgroundFill.solidFill.color'
            }
        })
        
        # 3. Add Title
        title_box_id = f"title_{idx}"
        requests.append({
            'createShape': {
                'objectId': title_box_id,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageId': new_slide_id,
                    'size': {
                        'width': {'magnitude': 8144000, 'unit': 'EMU'},
                        'height': {'magnitude': 700000, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': 500000, 'translateY': 400000,
                        'unit': 'EMU'
                    }
                }
            }
        })
        
        requests.append({
            'insertText': {
                'objectId': title_box_id,
                'text': s['title']
            }
        })
        
        # Format Title text
        requests.append({
            'updateTextStyle': {
                'objectId': title_box_id,
                'style': {
                    'fontFamily': 'Montserrat',
                    'fontSize': {'magnitude': 26 if not s['is_title'] else 36, 'unit': 'PT'},
                    'foregroundColor': {'solidFill': {'color': {'rgbColor': LIGHT_GREEN_ACCENT}}},
                    'bold': True
                },
                'fields': 'fontFamily,fontSize,foregroundColor,bold'
            }
        })
        
        # Clear shape borders
        requests.append({
            'updateShapeProperties': {
                'objectId': title_box_id,
                'shapeProperties': {
                    'outline': {'propertyState': 'INHERIT'}
                },
                'fields': 'outline'
            }
        })
        
        # 4. Handle Content
        if s['is_title']:
            # Subtitle and meta for title card
            sub_box_id = f"sub_{idx}"
            requests.append({
                'createShape': {
                    'objectId': sub_box_id,
                    'shapeType': 'RECTANGLE',
                    'elementProperties': {
                        'pageId': new_slide_id,
                        'size': {
                            'width': {'magnitude': 8144000, 'unit': 'EMU'},
                            'height': {'magnitude': 1200000, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1, 'scaleY': 1,
                            'translateX': 500000, 'translateY': 1600000,
                            'unit': 'EMU'
                        }
                    }
                }
            })
            
            sub_text = s['subtitle']
            if s['meta']:
                sub_text += "\n\n" + s['meta']
                
            requests.append({
                'insertText': {
                    'objectId': sub_box_id,
                    'text': sub_text
                }
            })
            
            requests.append({
                'updateTextStyle': {
                    'objectId': sub_box_id,
                    'style': {
                        'fontFamily': 'Montserrat',
                        'fontSize': {'magnitude': 18, 'unit': 'PT'},
                        'foregroundColor': {'solidFill': {'color': {'rgbColor': WHITE_COLOR}}}
                    },
                    'fields': 'fontFamily,fontSize,foregroundColor'
                }
            })
            
            requests.append({
                'updateShapeProperties': {
                    'objectId': sub_box_id,
                    'shapeProperties': {
                        'outline': {'propertyState': 'INHERIT'}
                    },
                    'fields': 'outline'
                }
            })
            
        else:
            # Regular slide content
            content_w = 4600000 if s['image'] else 8144000
            
            content_box_id = f"content_{idx}"
            requests.append({
                'createShape': {
                    'objectId': content_box_id,
                    'shapeType': 'RECTANGLE',
                    'elementProperties': {
                        'pageId': new_slide_id,
                        'size': {
                            'width': {'magnitude': content_w, 'unit': 'EMU'},
                            'height': {'magnitude': 3200000, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1, 'scaleY': 1,
                            'translateX': 500000, 'translateY': 1300000,
                            'unit': 'EMU'
                        }
                    }
                }
            })
            
            content_lines = []
            if s['subtitle']:
                content_lines.append(s['subtitle'])
                
            content_lines.extend(s['bullets'])
            full_content_text = "\n".join(content_lines)
            
            requests.append({
                'insertText': {
                    'objectId': content_box_id,
                    'text': full_content_text
                }
            })
            
            # Format body text
            requests.append({
                'updateTextStyle': {
                    'objectId': content_box_id,
                    'style': {
                        'fontFamily': 'Montserrat',
                        'fontSize': {'magnitude': 14 if s['image'] else 16, 'unit': 'PT'},
                        'foregroundColor': {'solidFill': {'color': {'rgbColor': WHITE_COLOR}}}
                    },
                    'fields': 'fontFamily,fontSize,foregroundColor'
                }
            })
            
            requests.append({
                'updateShapeProperties': {
                    'objectId': content_box_id,
                    'shapeProperties': {
                        'outline': {'propertyState': 'INHERIT'}
                    },
                    'fields': 'outline'
                }
            })
            
            # If bullets are present, apply bullet style
            if s['bullets']:
                start_index = len(s['subtitle']) + 1 if s['subtitle'] else 0
                requests.append({
                    'createParagraphBullets': {
                        'objectId': content_box_id,
                        'textRange': {
                            'type': 'FROM_START_INDEX',
                            'startIndex': start_index
                        },
                        'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                    }
                })
                
            # 5. Add Image if present
            if s['image']:
                image_element_id = f"img_{idx}"
                print(f"Adding image: {s['image']}")
                requests.append({
                    'createImage': {
                        'objectId': image_element_id,
                        'url': s['image'],
                        'elementProperties': {
                            'pageId': new_slide_id,
                            'size': {
                                'width': {'magnitude': 3200000, 'unit': 'EMU'},
                                'height': {'magnitude': 3000000, 'unit': 'EMU'}
                            },
                            'transform': {
                                'scaleX': 1, 'scaleY': 1,
                                'translateX': 5400000, 'translateY': 1300000,
                                'unit': 'EMU'
                            }
                        }
                    }
                })

    # Execute slide creations
    print("Sending update request to Google Slides API...")
    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    # Delete old slides
    if old_slide_ids:
        delete_requests = [{'deleteObject': {'objectId': oid}} for oid in old_slide_ids]
        try:
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': delete_requests}
            ).execute()
            print("Vana esitluse slaidid kustutatud/puhastatud.")
        except Exception as e:
            print(f"Märkus: Vanade slaidide puhastamisel tekkis tõrge: {e}")
            
    presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
    print(f"\n[OK] Esitlus on sünkroniseeritud Google Slides'iga!")
    print(f"Link esitlusele: {presentation_url}")

if __name__ == "__main__":
    sync_slides()
