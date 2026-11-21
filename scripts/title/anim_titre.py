"""Motion d'apparition du titre « if — the art of timing... » depuis le PSD.
Usage : uv run --with psd-tools --with imageio-ffmpeg python scripts/anim_titre.py
Sorties (3_RESULTATS) : titre_if_anim.mov (ProRes 422 HQ, fond) + titre_if_anim_alpha.mov (ProRes 4444, alpha)."""
import math, os, subprocess, numpy as np, imageio_ffmpeg
from PIL import Image
from psd_tools import PSDImage

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSD = os.path.join(ICI, "2_A_ENVOYER", "Nouveau projet.psd")
OUT = os.path.join(ICI, "3_RESULTATS")
FPS, DUREE = 24, 7.0           # 24p (montage cinéma)
SORTIE = (1280, 720)   # 720p
BEIGE = (238, 228, 208)   # fond uni
ENCRE = (28, 24, 20)      # couleur de tout le titre

psd = PSDImage.open(PSD)
W, H = psd.size
L = {l.name: l for l in psd.descendants()}
def calque(n):
    l = L[n]; im = l.composite().convert("RGBA")
    if n != "BACKGROUND":   # passe le calque en encre noire, garde l'alpha
        a = im.getchannel("A"); im = Image.new("RGBA", im.size, ENCRE + (255,)); im.putalpha(a)
    return im, l.bbox
fond, _ = calque("BACKGROUND")
fond = Image.new("RGBA", (W, H), BEIGE + (255,))
i_im, i_bb = calque("if")          # le calque « if » contient le i
f_im, f_bb = calque("f")
t_im, t_bb = calque("TRAIT")
s_im, s_bb = calque("sous titre")
# i + f fusionnés à leur place exacte (version au repos)
if_bb = (min(i_bb[0], f_bb[0]), min(i_bb[1], f_bb[1]), max(i_bb[2], f_bb[2]), max(i_bb[3], f_bb[3]))
if_im = Image.new("RGBA", (if_bb[2] - if_bb[0], if_bb[3] - if_bb[1]), (0, 0, 0, 0))
if_im.alpha_composite(i_im, (i_bb[0] - if_bb[0], i_bb[1] - if_bb[1]))
if_im.alpha_composite(f_im, (f_bb[0] - if_bb[0], f_bb[1] - if_bb[1]))

# repère des 3 points de suspension : dernières colonnes pleines du sous-titre
a = np.array(s_im)[:, :, 3].max(axis=0) > 20
runs, x = [], 0
while x < len(a):
    if a[x]:
        d = x
        while x < len(a) and a[x]: x += 1
        runs.append((d, x))
    x += 1
points = runs[-3:]
# mots : les 3 plus grands écarts avant les points séparent the / art / of / timing
lettres = runs[:-3]
ecarts = sorted(range(1, len(lettres)), key=lambda k: lettres[k][0] - lettres[k - 1][1])[-3:]
mots, d = [], 0
for k in sorted(ecarts) + [len(lettres)]:
    mots.append((lettres[d][0], lettres[k - 1][1])); d = k

def ressort(t, f=11.0, amort=5.0):
    return 0.0 if t <= 0 else 1 - math.exp(-amort * t) * math.cos(f * t)
def lisse(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)

def pose(canvas, im, bb, sy, sx=None, ancre="centre"):
    """colle im mis à l'échelle, ancré en bas au centre."""
    if sy <= 0.01: return
    sx = sx if sx is not None else sy
    if abs(sy - 1) < 0.004 and abs(sx - 1) < 0.004:   # au repos : position exacte du PSD, pas de jonction
        canvas.alpha_composite(im, (bb[0], bb[3] - im.height)); return
    w, h = im.size
    nw, nh = max(1, int(w * sx)), max(1, int(h * sy))
    r = im.resize((nw, nh), Image.LANCZOS)
    # ancre au point de jonction i/f pour qu'elle ne bouge jamais
    x = {"droite": bb[2] - nw, "gauche": bb[0]}.get(ancre, int((bb[0] + bb[2]) / 2 - nw / 2))
    canvas.alpha_composite(r, (int(x), int(bb[3] - nh)))

def alpha(im, k):
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * k))); return im

def chute(u, hauteur, duree=0.36, rebond=0.38, n=3):
    """lâcher physique : renvoie (décalage vers le haut en px, écrasement 0..1)."""
    if u < 0: return None
    g = 2 * hauteur / duree ** 2
    if u < duree: return hauteur - 0.5 * g * u * u, 0.0
    u -= duree; v = g * duree; choc = 1.0
    for _ in range(n):
        v *= rebond; T = 2 * v / g; choc *= rebond
        if u < T: return v * u - 0.5 * g * u * u, (1.0 if u < 0.05 else 0) * choc / rebond
        u -= T
    return 0.0, 0.0

def ecrase(u, duree=0.36, rebond=0.38):
    """squash qui s'amortit après le premier impact."""
    if u < duree: return 1.0, 1.0
    k = math.exp(-9 * (u - duree)) * math.cos(22 * (u - duree)) * 0.27
    return 1 - k, 1 + k * 0.7

def lettre(c, im, bb, u, ancre):
    r = chute(u, bb[3] + 60)
    if r is None: return False
    dy, _ = r
    sy, sx = ecrase(u)
    pose(c, im, (bb[0], bb[1], bb[2], bb[3] - int(dy)), sy, sx, ancre)
    return abs(dy) < 0.5 and abs(sy - 1) < 0.004

T_I, T_F = 0.6, 0.68      # lâcher du i puis du f
def image_nette(t, avec_fond):
    c = fond.copy() if avec_fond else Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # trait : se dessine de gauche à droite 0.15 → 0.65 s
    k = lisse((t - 0.1) / 0.4)
    if k > 0:
        w = max(1, int(t_im.width * k)); c.alpha_composite(t_im.crop((0, 0, w, t_im.height)), (t_bb[0], t_bb[1]))
    if t > T_I + 2.0:
        c.alpha_composite(if_im, (if_bb[0], if_bb[1]))
    else:
        lettre(c, i_im, i_bb, t - T_I, "droite")
        lettre(c, f_im, f_bb, t - T_F, "gauche")
    _suite(c, t)
    return c

def image(t, avec_fond, ech=10):
    """flou de mouvement : moyenne de sous-images sur un demi-intervalle (obturateur 180°)."""
    if not (T_I - 0.05 < t < T_F + 0.9):
        return image_nette(t, avec_fond)
    acc = np.zeros((H, W, 4), np.float32)
    for j in range(ech):
        acc += np.asarray(image_nette(t + j / ech * 0.5 / FPS, avec_fond), np.float32)
    return Image.fromarray((acc / ech).astype(np.uint8), "RGBA")

def _suite(c, t):
    # sous-titre : un mot à la fois, qui tombe et rebondit
    for n, (d, e) in enumerate(mots):
        u = t - (1.65 + 0.22 * n)
        if u <= 0: continue
        r = ressort(u, 16, 6.5)
        m = s_im.crop((max(d - 4, 0), 0, e + 4, s_im.height))
        pose(c, alpha(m, min(1, u / 0.08)), (s_bb[0] + d - 4, s_bb[1], s_bb[0] + e + 4,
             s_bb[3] - int((1 - r) * 40)), r, 1 + (1 - r) * 0.5)
    for n, (d, e) in enumerate(points):
        k = lisse((t - (2.9 + 0.32 * n)) / 0.12)
        if k > 0: c.alpha_composite(alpha(s_im.crop((d, 0, e, s_im.height)), k), (s_bb[0] + d, s_bb[1]))

# même traitement que l'intro : grain de papier + encre « imprimée » (moteur doodle de MOTION_INTRO)
import sys
sys.path.insert(0, os.path.join(ICI, "..", "..", "EP01", "MOTION_INTRO", "scripts"))
from doodle import textures, encrer
papier, encre = textures()
fond_np = np.clip(np.array(BEIGE, np.float32)[None, None, :] * (0.93 + 0.12 * papier[..., None]), 0, 255)
ff = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs(OUT, exist_ok=True)
def pipe(nom, opts):
    return subprocess.Popen([ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-vf", f"scale={SORTIE[0]}:{SORTIE[1]}:flags=lanczos", *opts,
                             "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-vendor", "apl0",
                             os.path.join(OUT, "FINALCUT", nom)], stdin=subprocess.PIPE)
os.makedirs(os.path.join(OUT, "FINALCUT"), exist_ok=True)
pf = pipe("TITRE_FINAL_24p.mov", ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"])
pa = pipe("TITRE_FINAL_24p_alpha.mov", ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16"])
for f in range(int(DUREE * FPS)):
    a = encrer(np.array(image(f / FPS, False)), papier, encre)
    pa.stdin.write(a.tobytes())
    al = a[..., 3:4].astype(np.float32) / 255
    pf.stdin.write(np.dstack([(fond_np * (1 - al) + a[..., :3] * al).astype(np.uint8), np.full((H, W), 255, np.uint8)]).tobytes())
for p_ in (pf, pa): p_.stdin.close(); p_.wait()
print("ok TITRE_FINAL_24p (papier)")
