"""Générique de fin IF EP01 (≈ 39 s) : zone gauche = polaroïds de production jetés sur la table (ils s'entassent,
positions / angles aléatoires, ombre portée, flou de mouvement) ; zone droite = crédits façon cinéma en fondu.
Même papier et même encre que l'intro.
    uv run --with pillow --with numpy --with imageio-ffmpeg python IF/EP01/GENERIQUE/scripts/generique.py [apercu]"""
import os, sys, glob, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # IF/EP01/GENERIQUE
EP = os.path.dirname(ICI); IF = os.path.dirname(EP)
sys.path.insert(0, os.path.join(EP, "MOTION_INTRO", "scripts"))
from doodle import W, H, BEIGE, INK, textures, encrer, smooth, clamp01, FONT_PATH

FPS, ECH = 24, 6
BLOC = 3.3               # temps de lecture de chaque carton
CAPT = os.path.join(ICI, "CAPTURES_A_DEPOSER")
TMP = os.path.join(ICI, "_images"); os.makedirs(TMP, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()

def image_video(chemin, t, nom):
    out = os.path.join(TMP, nom)
    if not os.path.exists(out):
        subprocess.run([ff, "-y", "-v", "error", "-ss", str(t), "-i", chemin, "-frames:v", "1", out])
    return out
def onde(mp3, nom, t0=0, t1=18):
    """forme d'onde de la voix off, dessinée à l'encre sur papier (pour la carte ElevenLabs)."""
    out = os.path.join(TMP, nom)
    if os.path.exists(out): return out
    raw = subprocess.run([ff, "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", mp3, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = np.abs(np.frombuffer(raw, np.int16).astype(np.float32)); n = 300
    env = np.array([a[i * len(a) // n:(i + 1) * len(a) // n].max() for i in range(n)]); env /= env.max()
    im = Image.new("RGB", (900, 900), (246, 238, 222)); d = ImageDraw.Draw(im)
    for i, v in enumerate(env):
        x = 30 + i * 840 / n; h = 6 + v * 330; d.line([(x, 450 - h), (x, 450 + h)], fill=(70, 50, 38), width=2)
    im.save(out); return out
def captures(*mots):
    fs = [f for f in sorted(glob.glob(os.path.join(CAPT, "*"))) if any(m.lower() in os.path.basename(f).lower() for m in mots)]
    return fs

B = os.path.join(IF, "BIBLE"); P = os.path.join(EP, "PLANS")
croquis = sorted(glob.glob(os.path.join(B, "STYLE", "croquis", "*", "*.*")))
rnd = random.Random(4)
bib_caps = sorted(glob.glob(os.path.join(B, "Capture*.png")))
FC = os.path.join(EP, "MONTAGE", "FINALCUT")
def fc(n): return sorted(glob.glob(os.path.join(FC, f"{n:02d}_*.mov")))[0]

def cap(h): return glob.glob(os.path.join(CAPT, f"*{h}*"))[0]
FR = os.path.join(P, "P02_test_runway", "1_BLENDER", "frames")
# (rôle, lignes, [(image, cadrage)]) — cadrage : "auto" (sujet détecté), ou (x0, y0, x1, y1) en fractions de l'image
BLOCS = [
    ("ÉCRIT ET RÉALISÉ PAR", ["Jérémie Borrotzu"],
     [(glob.glob(os.path.join(EP, "MAKING-OF", "grok-image-*.jpg"))[0], (0.02, 0.0, 0.385, 1.0))]),
    ("DESIGN DU PERSONNAGE", ["Jérémie Borrotzu"],
     [(os.path.join(B, "TURNAROUND", "3_RESULTATS", "planche_v2_caricature.png"), (0.0, 0.0, 0.5, 1.0))]),
    ("DÉCORS", ["du croquis au plan", "Blender · GPT Image 2 · Astra"],
     [(os.path.join(TMP, "decor_croquis_papier.jpg"), "auto"),
      (os.path.join(P, "P01_plan_fixe", "3_RESULTATS", "P01_plan_fixe_v2.png"), (0.35, 0.0, 0.95, 1.0))]),
    ("MODÉLISATION 3D", ["Hyper3D Rodin · Blender"],
     [(cap("16.52.10"), (0.0, 0.06, 0.64, 1.0)), (cap("16.33.08"), "auto"), (cap("16.35.02"), "auto")]),
    ("SEGMENTATION ET RIG", ["Blender"],
     [(cap("16.52.52"), "auto"), (cap("16.53.18"), "auto"), (cap("16.53.07"), "auto")]),
    ("MISE EN PLACE ET CAMÉRA", ["Blender (via MCP)"],
     [(cap("19.08.54"), "auto"), (os.path.join(FR, sorted(os.listdir(FR))[-1]), (0.52, 0.30, 0.86, 0.98))]),
    ("CONCEPT ART", ["GPT Image 2 · Astra", "Grok Imagine · Nano Banana"],
     [(os.path.join(B, "LA_MAIN", "3_RESULTATS", "la_main_ref_v1.jpg"), "auto"),
      (glob.glob(os.path.join(B, "TITRE", "3_RESULTATS", "Gemini_*"))[0], (0.2, 0.0, 0.8, 1.0))]),
    ("VIDÉO", ["Runway · Seedance 2.5"],
     [(image_video(fc(5), 3.0, "rw1.png"), (0.05, 0.0, 0.55, 1.0)), (image_video(fc(9), 8.0, "rw2.png"), (0.45, 0.0, 0.90, 1.0)),
      (image_video(fc(2), 8.5, "rw3_nuit.png"), (0.40, 0.0, 0.92, 1.0))]),
    ("MUSIQUE", ["Suno"], [(f, "auto") for f in captures("suno")]),
    ("VOIX OFF", ["ElevenLabs v4"], [(f, "auto") for f in captures("eleven")] or [(onde(os.path.join(EP, "MONTAGE", "EXPORTS", "IF_EP01.mp3"), "voix.png"), "auto")]),
    ("MOTION DESIGN", ["Python · Claude Code"],
     [(image_video(os.path.join(EP, "MOTION_INTRO", "3_RESULTATS", "intro_doodle_v2_720p.mov"), 4.6, "md1.png"), (0.30, 0.0, 0.70, 1.0)),
      (image_video(os.path.join(EP, "MOTION_INTRO", "3_RESULTATS", "intro_texte_v3_720p.mov"), 10.95, "md2.png"), (0.30, 0.15, 0.70, 0.85))]),
    ("COORDINATION AGENTIQUE · MONTAGE", ["Claude Opus 5.5 · Claude Code", "Final Cut Pro · Topaz"], []),
    ("", ["3 jours de production"], []),
    ("", ["if", "the art of timing…"], []),
]
# jamais deux fois la même image (même contenu, même sous un autre nom)
import hashlib
_vus = set()
for _r, _l, _imgs in BLOCS:
    garde = []
    for f, cad in _imgs:
        if not os.path.exists(f): continue
        h = hashlib.md5(open(f, "rb").read()).hexdigest()
        if h in _vus: continue
        _vus.add(h); garde.append((f, cad))
    _imgs[:] = garde

# ---------------- polaroïds ----------------
PW = 360; MARGE, BAS = 18, 66
def cadre_auto(im):
    """boîte du sujet : pixels qui s'écartent nettement de la couleur des bords (fond de viewport, papier, studio)."""
    a = np.asarray(im.convert("RGB"), np.float32); h, w = a.shape[:2]
    bord = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    fond = np.median(bord, axis=0)
    m = np.abs(a - fond).sum(axis=2) > 60
    ys, xs = np.nonzero(m)
    if len(xs) < 0.01 * w * h: return (0, 0, w, h)
    x0, x1 = np.percentile(xs, [1, 99]); y0, y1 = np.percentile(ys, [1, 99])
    return (x0, y0, x1, y1)
def polaroid(chemin, cad="auto"):
    im = Image.open(chemin).convert("RGB"); w, h = im.size
    if cad == "auto": x0, y0, x1, y1 = cadre_auto(im)
    else: x0, y0, x1, y1 = cad[0] * w, cad[1] * h, cad[2] * w, cad[3] * h
    asp = (x1 - x0) / max(y1 - y0, 1)
    ratio = 1.0 if asp >= 0.8 else max(asp, 0.62)                  # sujet vertical (perso en pied) : photo portrait
    ch = min(max(y1 - y0, (x1 - x0) / ratio) * 1.06, h); cw = ch * ratio
    if cw > w: cw = w; ch = cw / ratio
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    X0 = int(min(max(cx - cw / 2, 0), w - cw)); Y0 = int(min(max(cy - ch / 2, 0), h - ch))
    pw = PW - 2 * MARGE; ph = int(pw / ratio)
    im = im.crop((X0, Y0, X0 + int(cw), Y0 + int(ch))).resize((pw, ph), Image.LANCZOS)
    p = Image.new("RGBA", (PW, ph + MARGE + BAS), (250, 247, 240, 255)); p.paste(im, (MARGE, MARGE))
    a = np.array(p); a[..., :3] = np.clip(a[..., :3].astype(np.float32) * 0.97 + 4, 0, 255)
    return Image.fromarray(a, "RGBA")
POLAS = []        # (image, t_arrivée, x, y, angle, départ_dx, départ_dy, angle_départ)
T0 = 0.6
for i, (role, lignes, imgs) in enumerate(BLOCS):
    tb = T0 + i * BLOC
    for k, (f, cad) in enumerate(imgs[:3]):
        r = random.Random(i * 31 + k)
        x = -480 + r.uniform(-230, 230); y = r.uniform(-230, 210); ang = r.uniform(-13, 13)
        dep = r.choice([(-1500, r.uniform(-500, 500)), (r.uniform(-1200, -300), -900), (r.uniform(-1200, -300), 900)])
        POLAS.append((polaroid(f, cad), tb + 0.15 + 0.45 * k, x, y, ang, dep[0], dep[1], ang + r.choice((-1, 1)) * r.uniform(40, 80)))

_ombre = {}
def ombre(img, flou):
    k = (id(img), int(flou))
    if k not in _ombre:
        a = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0))
        a.paste(Image.new("RGBA", img.size, (40, 28, 18, 120)), (40, 40))
        _ombre[k] = a.filter(ImageFilter.GaussianBlur(flou))
    return _ombre[k]
VOL = 0.5
def couche_polas(t):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for img, ta, x, y, ang, ddx, ddy, ang0 in POLAS:
        u = t - (ta - VOL)
        if u < 0: continue
        p = clamp01(u / VOL); e = 1 - (1 - p) ** 3                     # glisse et freine (frottement)
        px, py = x + ddx * (1 - e), y + ddy * (1 - e)
        a = ang0 + (ang - ang0) * e
        haut = 1 - e                                                    # hauteur au-dessus de la table
        if p >= 1: v = u - VOL; a += 1.6 * math.exp(-9 * v) * math.sin(22 * v)       # petit rebond au contact
        s = 1 + 0.07 * haut
        g = img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR) if s > 1.001 else img
        g = g.rotate(a, resample=Image.BICUBIC, expand=True)
        o = ombre(img, 6 + 14 * haut).rotate(a, resample=Image.BICUBIC, expand=True)
        cx, cy = W / 2 + px, H / 2 + py
        c.alpha_composite(o, (int(cx - o.width / 2 + 10 + 40 * haut), int(cy - o.height / 2 + 14 + 50 * haut)))
        c.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
    return c

# ---------------- crédits (fondu) ----------------
def police(t): return ImageFont.truetype(FONT_PATH, t)
def bloc_texte(role, lignes, final=False):
    im = Image.new("RGBA", (900, 500), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 250 - (len(lignes) * 66 + (50 if role else 0)) / 2
    if role:
        f = police(32); x = 450 - (sum(f.getlength(ch) for ch in role) + 5.5 * (len(role) - 1)) / 2
        for ch in role: d.text((x, y), ch, font=f, fill=(96, 72, 52, 255)); x += f.getlength(ch) + 5.5
        y += 62
    for k, l in enumerate(lignes):
        taille = (170 if k == 0 else 52) if final else (78 if role == "" else 62)
        f = police(taille); d.text((450 - f.getlength(l) / 2, y), l, font=f, fill=INK); y += taille * 1.3
    return im
TEXTES = [(bloc_texte(r, l, final=(i == len(BLOCS) - 1)), T0 + i * BLOC) for i, (r, l, _) in enumerate(BLOCS)]
DUREE = T0 + len(BLOCS) * BLOC + 0.8
def couche_texte(t):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i, (im, tb) in enumerate(TEXTES):
        fin = tb + BLOC - 0.1 if i < len(TEXTES) - 1 else DUREE - 0.5
        a = smooth((t - (tb + 0.15)) / 0.45) * (1 - smooth((t - (fin - 0.45)) / 0.45))
        if a <= 0: continue
        g = im.copy(); g.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        dx = 0 if i < len(TEXTES) - 1 else -480                       # le titre final se centre
        c.alpha_composite(g, (int(W / 2 + 480 + dx - 450), int(H / 2 - 250)))
    return c

def image(t, papier, encre, fond):
    acc = np.zeros((H, W, 4), np.float32)
    bouge = any(0 < t - (ta - VOL) < VOL + 0.3 for _, ta, *_ in POLAS)
    n = ECH if bouge else 1
    for j in range(n):
        a = np.array(couche_polas(t + j / n * 0.5 / FPS), np.float32)
        acc[..., :3] += a[..., :3] * a[..., 3:4] / 255; acc[..., 3] += a[..., 3]
    acc /= n
    al = acc[..., 3:4] / 255
    rgb = fond * (1 - al) + np.where(al > 0, acc[..., :3] / np.maximum(al, 1e-3), 0) * al
    if t > DUREE - 1.0: k = smooth((t - (DUREE - 1.0)) / 0.7); rgb = rgb * (1 - k) + fond * k      # tout s'efface : papier vierge
    tx = encrer(np.array(couche_texte(t)), papier, encre).astype(np.float32); ta_ = tx[..., 3:4] / 255
    rgb = rgb * (1 - ta_) + tx[..., :3] * ta_
    return np.clip(rgb, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    papier, encre = textures(); b = np.array(BEIGE, np.float32)
    fond = np.clip(b[None, None, :] * (0.93 + 0.12 * papier[..., None]), 0, 255)
    if len(sys.argv) > 1:
        ts = [0.3, 2.0, 5.0, 9.0, 12.0, 14.5, 18.5, 22.0, 27.0, 31.0, 34.5, DUREE - 0.2]
        ims = [Image.fromarray(image(t, papier, encre, fond)).resize((480, 270)) for t in ts]
        sh = Image.new("RGB", (480 * 4, 270 * 3))
        for i, im in enumerate(ims): ImageDraw.Draw(im).text((8, 8), f"{ts[i]:.1f}s", fill=(200, 0, 0)); sh.paste(im, ((i % 4) * 480, (i // 4) * 270))
        sh.save(sys.argv[1]); print("duree", DUREE, "polas", len(POLAS))
    else:
        out = os.path.join(ICI, "3_RESULTATS", "generique_IF_24p.mov")
        p = subprocess.Popen([ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-vf", "scale=1280:720:flags=lanczos", "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le",
                              "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-vendor", "apl0", out], stdin=subprocess.PIPE)
        for n in range(int(DUREE * FPS)): p.stdin.write(image(n / FPS, papier, encre, fond).tobytes())
        p.stdin.close(); p.wait(); print("ok", out)
