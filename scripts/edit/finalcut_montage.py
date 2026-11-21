"""Convertit toutes les vidéos de MONTAGE/ (et sous-dossiers) en ProRes 422 HQ + PCM 48 kHz pour Final Cut.
Sortie : MONTAGE/FINALCUT/NN_<jour-heure>_<nom court>.mov, numérotées dans l'ordre de génération.
Les originaux ne sont pas touchés ; les fichiers déjà à jour sont sautés.
    uv run --with imageio-ffmpeg python IF/EP01/scripts/finalcut_montage.py"""
import glob, os, re, subprocess, time, imageio_ffmpeg

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTAGE = os.path.join(ICI, "MONTAGE")
OUT = os.path.join(MONTAGE, "FINALCUT")
ff = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs(OUT, exist_ok=True)

src = [p for p in glob.glob(os.path.join(MONTAGE, "**", "*"), recursive=True)
       if p.lower().endswith((".mov", ".mp4")) and os.sep + "FINALCUT" + os.sep not in p]
for n, p in enumerate(sorted(src, key=os.path.getmtime), 1):
    court = re.sub(r"^Seedance 2_5 - ", "", os.path.splitext(os.path.basename(p))[0])
    court = re.sub(r"[^A-Za-z0-9]+", "_", court).strip("_")[:40]
    nom = f"{n:02d}_{time.strftime('%m%d-%H%M', time.localtime(os.path.getmtime(p)))}_{court}.mov"
    dst = os.path.join(OUT, nom)
    if os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(p):
        continue
    r = subprocess.run([ff, "-y", "-v", "error", "-i", p, "-c:v", "prores_ks", "-profile:v", "3",
                        "-pix_fmt", "yuv422p10le", "-vendor", "apl0",
                        "-c:a", "pcm_s16le", "-ar", "48000", dst], capture_output=True, text=True)
    print(("OK    " if r.returncode == 0 else "ÉCHEC ") + nom, r.stderr[:200])
