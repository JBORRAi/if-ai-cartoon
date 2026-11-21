"""Écran de transition « What if?... », même style que le titre (beige, encre, police Annapurna SIL).
Calé sur la voix off : « Et si maintenant... ......... Constatons... »
    uv run --with pillow --with numpy --with imageio-ffmpeg python scripts/anim_whatif.py
Sortie : 3_RESULTATS/transition_whatif_720p.mov (+ _alpha)."""
import math, os, subprocess, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = ImageFont.truetype(os.path.join(ICI, "fonts", "AnnapurnaSIL-Regular.ttf"), 150)
W, H, FPS, DUREE = 1920, 1080, 60, 5.5
SORTIE = (1280, 720)
BEIGE, ENCRE = (238, 228, 208), (28, 24, 20)

# Rythme de la voix : « Et si » -> What, if ; « maintenant » -> ? ; longue pause -> les 3 points tombent
# lentement ; « Constatons... » -> tout tombe hors champ (retour à la scène).
PIECES = [("What", 0.25), (" if", 0.55), ("?", 1.0), (".", 1.8), (".", 2.4), (".", 3.0)]
SORTIE_T = 4.3

HG = FONT.getbbox("What if?...")[3] + 20
def glyphe(txt):
    l, t, r, b = FONT.getbbox(txt)
    im = Image.new("RGBA", (r - l + 40, HG), (0, 0, 0, 0))   # hauteur commune : même ligne de base
    ImageDraw.Draw(im).text((20 - l, 0), txt, font=FONT, fill=ENCRE + (255,))
    return im

texte = "".join(p for p, _ in PIECES)
l, t, r, b = FONT.getbbox(texte)
x0, base = (W - (r - l)) // 2 - l, (H - (b - t)) // 2 - t
pieces, x = [], x0
for txt, t0 in PIECES:
    pieces.append((glyphe(txt), x - 20, t0, txt))
    x += FONT.getlength(txt)

def ressort(u, f=14.0, a=6.0):
    return 0.0 if u <= 0 else 1 - math.exp(-a * u) * math.cos(f * u)

def image(t, fond):
    c = Image.new("RGBA", (W, H), BEIGE + (255,) if fond else (0, 0, 0, 0))
    for n, (g, gx, t0, txt) in enumerate(pieces):
        u = t - t0
        if u <= 0: continue
        r = ressort(u, 11 if txt == "." else 14, 5 if txt == "." else 6)
        dy = -(1 - r) * (60 if txt != "." else 120)
        sy, sx = r, 1 + (1 - r) * 0.5
        ang = 0
        if txt == "?":   # intonation de question : petit hochement
            ang = math.exp(-4 * u) * math.sin(10 * u) * 18
        # sortie : chaque pièce tombe hors champ, en cascade
        v = t - (SORTIE_T + 0.06 * n)
        if v > 0: dy += 2600 * v * v; ang += v * (25 if n % 2 else -25)
        if sy < 0.02: continue
        gi = g.resize((max(1, int(g.width * sx)), max(1, int(g.height * sy))), Image.LANCZOS)
        if ang: gi = gi.rotate(ang, resample=Image.BICUBIC, expand=False, center=(gi.width / 2, gi.height * 0.85))
        px = int(gx + (g.width - gi.width) / 2)
        py = int(base + g.height * (1 - sy) * 0.8 + dy)   # ancré vers la ligne de base
        c.alpha_composite(gi, (px, py)) if -H < py < H else None
    return c

ff = imageio_ffmpeg.get_ffmpeg_exe()
for fond, nom, opts in [(True, "transition_whatif_720p.mov", ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"]),
                        (False, "transition_whatif_720p_alpha.mov", ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le"])]:
    p = subprocess.Popen([ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-vf", f"scale={SORTIE[0]}:{SORTIE[1]}:flags=lanczos", *opts,
                          os.path.join(ICI, "3_RESULTATS", nom)], stdin=subprocess.PIPE)
    for f in range(int(DUREE * FPS)):
        p.stdin.write(image(f / FPS, fond).tobytes())
    p.stdin.close(); p.wait(); print("ok", nom)
