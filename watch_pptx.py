import os
import time
import subprocess

PPTX_PATH = "/Users/metrobee/Library/CloudStorage/GoogleDrive-borismeldre@gmail.com/My Drive/myGslides/fungib_hundiallika.pptx"
PULL_SCRIPT = "/Users/metrobee/Projects/fungib/pull.sh"

print(f"Alustan PowerPoint faili jälgimist: {PPTX_PATH}", flush=True)
last_mtime = None

if os.path.exists(PPTX_PATH):
    last_mtime = os.path.getmtime(PPTX_PATH)
    print(f"Esialgne muutmisaeg: {last_mtime}", flush=True)

try:
    while True:
        time.sleep(2)
        if os.path.exists(PPTX_PATH):
            current_mtime = os.path.getmtime(PPTX_PATH)
            if last_mtime is None:
                last_mtime = current_mtime
                print(f"Tuvastasin uue faili muutmise aja: {last_mtime}", flush=True)
            elif current_mtime > last_mtime:
                print(f"Tuvastasin muudatuse failis {PPTX_PATH}. Ootan sünkroniseerimise lõppu...", flush=True)
                time.sleep(3)
                
                print("Käivitan automaatse tõmbamise (pull.sh)...", flush=True)
                
                res = subprocess.run(["bash", PULL_SCRIPT], cwd="/Users/metrobee/Projects/fungib", capture_output=True, text=True)
                print("--- PULL.SH VÄLJUND ---", flush=True)
                print(res.stdout, flush=True)
                if res.stderr:
                    print("--- PULL.SH VEAD ---", flush=True)
                    print(res.stderr, flush=True)
                print("---------------------", flush=True)
                
                # Check for git modifications
                git_status = subprocess.run(["git", "status", "--porcelain", "public/index.html"], cwd="/Users/metrobee", capture_output=True, text=True)
                if git_status.stdout.strip():
                    print("Tuvastasin HTML-i muutuse. Teostan automaatse git commiti...", flush=True)
                    subprocess.run(["git", "add", "Projects/fungib/"], cwd="/Users/metrobee")
                    subprocess.run(["git", "commit", "-m", "feat: auto-sync updates from Google Slides PPTX"], cwd="/Users/metrobee")
                    print("[OK] Muudatused salvestatud Giti.", flush=True)
                
                last_mtime = os.path.getmtime(PPTX_PATH)
        else:
            if last_mtime is not None:
                print("Faili ei leitud enam. Ootan uuesti ilmnemist...", flush=True)
                last_mtime = None
except KeyboardInterrupt:
    print("Faili jälgimine lõpetatud kasutaja poolt.", flush=True)
