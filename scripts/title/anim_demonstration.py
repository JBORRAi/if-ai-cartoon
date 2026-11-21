"""Panneau « démonstration... » (2,75 s), même esprit que le titre « if » :
les lettres tombent une par une à intervalle régulier avec un petit rebond ; la dernière lettre tombe sur
l'avant-dernière et rebondit jusqu'à sa place ; les 3 points tombent sur la dernière lettre et rebondissent
jusqu'à leur place. Flou de mouvement.
    uv run --with pillow --with numpy --with imageio-ffmpeg python scripts/anim_demonstration.py"""
import math, os, subprocess, numpy as np, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = ImageFont.truetype(os.path.join(ICI, "fonts", "AnnapurnaSIL-Regular.ttf"), 150)
W, H, FPS, DUREE = 1920, 1080, 24, 2.75          # 24p
SORTIE = (1280, 720)
BEIGE, ENCRE = (238, 228, 208), (28, 24, 20)
MOT, POINTS = "démonstration", "..."
T0, PAS = 0.10, 0.075          # première lettre, intervalle entre lettres
CHUTE = 0.28                   # durée de chute
T_POINTS, PAS_POINTS = 1.45, 0.22
HAUT = 900                     # hauteur de départ (hors champ)

texte = MOT + POINTS
l, t, r, b = FONT.getbbox(texte)
X0 = (W - (r - l)) // 2 - l
Y0 = (H - (b - t)) // 2 - t           # position du haut de ligne
BASE = FONT.getbbox("n")[3]           # ligne de base (bas du n), en coordonnées glyphe
HG = b + 30

def glyphe(c):
    im = Image.new("RGBA", (int(FONT.getlength(c)) + 40, HG), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, 0), c, font=FONT, fill=ENCRE + (255,))
    return im

lettres = []   # (image, x final)
for k, c in enumerate(texte):
    lettres.append((glyphe(c), X0 + FONT.getlength(texte[:k]) - 20))

def haut_de(c):           # hauteur de la lettre au-dessus de la ligne de base
    return BASE - FONT.getbbox(c)[1]

def rebond(u, amp=22, k=9, w=26):
    """petit rebond après contact (décalage vers le haut, ≥ 0)."""
    return 0 if u < 0 else amp * math.exp(-k * u) * abs(math.sin(w * u))

def chute(u, dur=CHUTE):
    """décalage vers le haut pendant la chute : HAUT → 0 en dur (accélération)."""
    return HAUT * (1 - (u / dur) ** 2)

def position(n, t):
    """(dx, dy) de la pièce n à l'instant t, ou None si pas encore entrée. dy > 0 = vers le haut."""
    der = len(MOT) - 1
    if n < der:                                    # lettres normales
        u = t - (T0 + PAS * n)
        if u < 0: return None
        return (0, chute(u)) if u < CHUTE else (0, rebond(u - CHUTE))
    if n == der:                                   # dernière lettre : tombe sur l'avant-dernière
        u = t - (T0 + PAS * n + 0.12)
        support, sx = der - 1, lettres[der - 1][1] - lettres[der][1]
    else:                                          # points : tombent sur la dernière lettre
        u = t - (T_POINTS + PAS_POINTS * (n - len(MOT)))
        support, sx = der, lettres[der][1] + FONT.getlength(MOT[der]) * 0.35 - lettres[n][1]
    if u < 0: return None
    sy = haut_de(texte[support])
    if u < CHUTE: return (sx, sy + chute(u) - 0)   # chute jusqu'au sommet du support
    v = u - CHUTE; saut = 0.26                    # saut en arc vers sa place
    if v < saut:
        p = v / saut
        return (sx * (1 - p), sy * (1 - p) + 70 * 4 * p * (1 - p))
    return (0, rebond(v - saut))

def image_nette(t, fond):
    c = Image.new("RGBA", (W, H), BEIGE + (255,) if fond else (0, 0, 0, 0))
    for n, (g, x) in enumerate(lettres):
        p = position(n, t)
        if p is None: continue
        dx, dy = p
        c.alpha_composite(g, (int(x + dx), int(Y0 - dy)))
    return c

def image(t, fond, ech=5):
    acc = np.zeros((H, W, 4), np.float32)
    for j in range(ech):
        acc += np.asarray(image_nette(t + j / ech * 0.5 / FPS, fond), np.float32)
    return Image.fromarray((acc / ech).astype(np.uint8), "RGBA")

# même traitement que l'intro : grain de papier + encre « imprimée » (moteur doodle de MOTION_INTRO)
import sys
sys.path.insert(0, os.path.join(ICI, "..", "..", "EP01", "MOTION_INTRO", "scripts"))
from doodle import textures, encrer, BEIGE as PAPIER
papier, encre = textures()
fond_np = np.clip(np.array(PAPIER, np.float32)[None, None, :] * (0.93 + 0.12 * papier[..., None]), 0, 255)
ff = imageio_ffmpeg.get_ffmpeg_exe()
def pipe(nom, opts):
    return subprocess.Popen([ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-vf", f"scale={SORTIE[0]}:{SORTIE[1]}:flags=lanczos", *opts,
                             "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-vendor", "apl0",
                             os.path.join(ICI, "3_RESULTATS", nom)], stdin=subprocess.PIPE)
pf = pipe("transition_demonstration_24p.mov", ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"])
pa = pipe("transition_demonstration_24p_alpha.mov", ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16"])
for f in range(int(round(DUREE * FPS))):
    a = encrer(np.array(image(f / FPS, False, ech=10)), papier, encre)
    pa.stdin.write(a.tobytes())
    al = a[..., 3:4].astype(np.float32) / 255
    full = (fond_np * (1 - al) + a[..., :3] * al).astype(np.uint8)
    pf.stdin.write(np.dstack([full, np.full((H, W), 255, np.uint8)]).tobytes())
for p_ in (pf, pa): p_.stdin.close(); p_.wait()
print("ok transition_demonstration_24p")
