"""Petit moteur de motion design « doodle » pour IF : traits encrés qui frémissent (boil 12 i/s),
tracé progressif, pops élastiques, déplacements lissés, chutes physiques (même physique que le titre).
Coordonnées : origine au centre de l'écran 1920x1080, y vers le bas."""
import math, os, random, subprocess, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
CX, CY = W // 2, H // 2
INK = (28, 24, 20, 255)
BEIGE = (238, 228, 208)
LW = 7
FONT_PATH = os.path.join(os.path.dirname(__file__), "../../../BIBLE/TITRE/fonts/AnnapurnaSIL-Regular.ttf")

def clamp01(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def smooth(x): x = clamp01(x); return x * x * (3 - 2 * x)
def spring(u, f=13.0, a=6.0): return 0.0 if u <= 0 else 1 - math.exp(-a * u) * math.cos(f * u)
def ease_back(u, a=1.0):
    """ease in-out « back » : petit recul (anticipation) puis dépassement et retour. a = intensité."""
    u = clamp01(u); c2 = 1.70158 * a * 1.525
    if u < 0.5: return ((2 * u) ** 2 * ((c2 + 1) * 2 * u - c2)) / 2
    return ((2 * u - 2) ** 2 * ((c2 + 1) * (u * 2 - 2) + c2) + 2) / 2

# ---------- formes (coordonnées locales, origine = point d'ancrage) ----------
def arc(cx, cy, r, a0, a1, n=40, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
def circle(cx, cy, r, n=48): return arc(cx, cy, r, -90, 270, n)
def rect(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]

def stick(pose="debout"):
    if pose == "singe":
        return [circle(38, -118, 24), [(28, -98), (8, -78), (-8, -52)], [(-8, -52), (-34, 0)], [(-8, -52), (16, 0)],
                [(18, -90), (40, -50), (44, -14)], [(14, -88), (-10, -50), (-4, -18)]]
    if pose == "mi":
        return [circle(14, -152, 26), [(10, -126), (0, -60)], [(0, -60), (-30, 0)], [(0, -60), (30, 0)],
                [(6, -110), (34, -66)], [(6, -110), (-26, -72)]]
    if pose == "bras_haut":
        return [circle(0, -170, 28), [(0, -142), (0, -60)], [(0, -60), (-32, 0)], [(0, -60), (32, 0)],
                [(0, -122), (-40, -160), (-52, -212)], [(0, -122), (40, -160), (52, -212)]]
    if pose == "course":
        return [circle(16, -166, 28), [(10, -138), (-4, -62)], [(-4, -62), (-40, -32), (-66, -14)],
                [(-4, -62), (30, -24), (36, 0)], [(6, -120), (44, -98), (58, -112)], [(6, -120), (-30, -96), (-50, -108)]]
    return [circle(0, -170, 28), [(0, -142), (0, -60)], [(0, -60), (-32, 0)], [(0, -60), (32, 0)],
            [(0, -122), (-44, -82)], [(0, -122), (44, -82)]]

def ampoule():
    s = [arc(0, 0, 46, 125, 415), [(-22, 38), (-20, 52), (20, 52), (22, 38)], [(-18, 62), (18, 62)], [(-10, 72), (10, 72)],
         [(-14, 14), (-7, -8), (0, 14), (7, -8), (14, 14)]]
    return s
def rayons(r0=66, r1=96, n=9, a0=-200, a1=20):
    return [[(r0 * math.cos(math.radians(a)), r0 * math.sin(math.radians(a))),
             (r1 * math.cos(math.radians(a)), r1 * math.sin(math.radians(a)))]
            for a in [a0 + (a1 - a0) * i / (n - 1) for i in range(n)]]
def pyramide(): return [[(-80, 0), (0, -120), (80, 0), (-80, 0)], [(-40, -60), (40, -60)], [(0, -120), (14, 0)]]
def colonne(): return [rect(-24, -126, 24, 0), [(-40, -126), (40, -126)], [(-44, -138), (44, -138)], [(-8, -120), (-8, -6)], [(8, -120), (8, -6)]]
def chateau():
    o = [(-70, 0), (-70, -90)]
    for i, x in enumerate(range(-70, 71, 20)):
        y = -90 if i % 2 == 0 else -76
        o += [(x, y), (x + 20, y)] if x < 70 else [(x, -90)]
    o += [(70, 0)]
    return [o, arc(0, 0, 18, 180, 360, 16) + [(18, 0)]]
def grotte(): return [arc(0, 0, 80, 180, 360, 30, ry=95), arc(0, 0, 40, 180, 360, 20, ry=55)]
def fusee():
    return [[(0, -160), (26, -110), (26, -36), (-26, -36), (-26, -110), (0, -160)], circle(0, -96, 11, 20),
            [(-26, -60), (-46, -30), (-26, -36)], [(26, -60), (46, -30), (26, -36)], [(-12, -34), (-6, -8), (0, -26), (6, -8), (12, -34)]]
def engrenage(r=70, dents=9):
    p = []
    for i in range(dents * 4 + 1):
        a = 2 * math.pi * i / (dents * 4)
        rr = r if (i % 4) in (1, 2) else r * 0.78
        p.append((rr * math.cos(a), rr * math.sin(a)))
    return [p, circle(0, 0, r * 0.28, 24)]
def halteres():
    return [[(-120, 0), (120, 0)], rect(-150, -34, -124, 34), rect(-176, -24, -152, 24), rect(124, -34, 150, 34), rect(152, -24, 176, 24)]
def impact(r0=60, r1=95, n=8): return rayons(r0, r1, n, 0, 360 - 360 / n)
def vitesse(): return [[(-260 + 40 * (i % 2), -60 + 40 * i), (-60, -60 + 40 * i)] for i in range(4)]
def bulle(seed=3):
    R = 120; p = []
    for i in range(121):
        a = 2 * math.pi * i / 120
        r = R * (1 + 0.13 * abs(math.sin(4 * a)))
        p.append((r * 1.35 * math.cos(a), r * 0.8 * math.sin(a)))
    return [p, circle(-120, 120, 16, 20), circle(-160, 160, 9, 16)]
def gribouillis(seed, n=70, rx=90, ry=50, cx=0, cy=0):
    rnd = random.Random(seed); x, y, p = 0.0, 0.0, []
    for i in range(n):
        a = i * 0.9 + rnd.uniform(-0.6, 0.6); r = 0.55 + 0.45 * rnd.random()
        p.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return [p]
def interrogation():
    return [arc(0, -70, 38, 200, 450, 30) + [(0, -22), (0, -8)]]
def horloge(r=150):
    s = [circle(0, 0, r, 60)]
    for i in range(12):
        a = math.radians(i * 30); r0 = r - (26 if i % 3 == 0 else 14)
        s.append([(r0 * math.cos(a), r0 * math.sin(a)), ((r - 4) * math.cos(a), (r - 4) * math.sin(a))])
    s.append([(-14, -r - 4), (-14, -r - 26), (14, -r - 26), (14, -r - 4)])
    return s
def aiguille(l): return [[(0, 12), (0, -l)]]
def etoile(r=18): return [[(-r, 0), (r, 0)], [(0, -r), (0, r)], [(-r * .6, -r * .6), (r * .6, r * .6)], [(-r * .6, r * .6), (r * .6, -r * .6)]]
def frise(x0=-680, x1=680): return [[(x0, 0), (x1, 0)]] + [[(x, -10), (x, 10)] for x in range(x0 + 60, x1, 140)]
def souligne(w, seed=1):
    rnd = random.Random(seed)
    return [[(-w / 2 + w * i / 20, 6 * math.sin(i * 0.9) + rnd.uniform(-2, 2)) for i in range(21)]]

# ---------- éléments ----------
def _len(p): return sum(math.dist(p[i], p[i + 1]) for i in range(len(p) - 1))
def _partial(p, L):
    out = [p[0]]
    for i in range(len(p) - 1):
        d = math.dist(p[i], p[i + 1])
        if L <= d:
            if d > 0: out.append((p[i][0] + (p[i + 1][0] - p[i][0]) * L / d, p[i][1] + (p[i + 1][1] - p[i][1]) * L / d))
            return out
        L -= d; out.append(p[i + 1])
    return out

def arrondi(p, n=2):
    """lissage de Chaikin (coins arrondis), extrémités conservées."""
    if len(p) <= 6: n = 1                       # formes à peu de points : arrondir sans les déformer
    for _ in range(n):
        if len(p) < 3: return p
        q = [p[0]]
        for a, b in zip(p[:-1], p[1:]):
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        q.append(p[-1]); p = q
    return p

def trait(drw, p, w, col=INK):
    """trait à pression variable : fin aux extrémités, plein au milieu, jointures rondes."""
    L = [0.0]
    for a, b in zip(p[:-1], p[1:]): L.append(L[-1] + math.dist(a, b))
    tot = L[-1] or 1
    for i in range(len(p) - 1):
        u = (L[i] + L[i + 1]) / 2 / tot
        wi = w * (0.45 + 0.55 * min(1.0, 4 * u * (1 - u) * 1.6))
        drw.line([p[i], p[i + 1]], fill=col, width=max(1, int(round(wi))))
        r = wi / 2; x, y = p[i + 1]
        drw.ellipse((x - r, y - r, x + r, y + r), fill=col)

def textures(seed=7):
    """grain de papier (fond) et grain d'encre (modulation de l'alpha du trait)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    def bruit(echelle):
        small = rng.random((H // echelle + 2, W // echelle + 2)).astype(np.float32)
        return np.array(Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    fin = rng.random((H, W)).astype(np.float32)
    papier = 0.55 * bruit(3) + 0.3 * bruit(18) + 0.15 * fin
    fibres = np.array(Image.fromarray((rng.random((H // 2, W // 40)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    papier = papier * 0.8 + fibres * 0.2
    # l'encre se dépose dans les creux du papier : moins dense sur les reliefs (effet incrusté / imprimé)
    encre = (0.84 + 0.16 * (1 - papier) ** 1.3) * (0.90 + 0.10 * (0.6 * bruit(2) + 0.4 * fin))
    return papier, np.clip(encre / encre.max() * 1.05, 0, 1)

def encrer(a, papier, encre):
    """densité d'encre variable + encre un peu plus claire sur les reliefs du papier (trait « imprimé »)."""
    import numpy as np
    a[..., 3] = (a[..., 3] * encre).astype(np.uint8)
    rgb = a[..., :3].astype(np.float32); b = np.array(BEIGE, np.float32)
    a[..., :3] = np.clip(rgb + (b - rgb) * (0.06 * papier[..., None]), 0, 255).astype(np.uint8)
    return a

class El:
    """Élément dessiné. moves = [(t0, t1, x, y), ...] ; out = instant de chute ; rot_fn(t) en degrés."""
    def __init__(s, strokes=None, x=0, y=0, t_in=0.0, draw=0.0, pop=False, out=None, scale=1.0, rot=0.0,
                 spin=0.0, moves=None, rot_fn=None, width=LW, dots=(), hide=None, seed=None, boil=1.6, img=None,
                 drop=False, chute_dir=1, fill=False, antic=0.0, arc=0.0, respire=0.0, pose_fn=None, sortie_antic=True, epais=None):
        s.__dict__.update(locals()); del s.__dict__["s"]
        s.seed = seed if seed is not None else random.randint(0, 10 ** 6)
        s.creux = True
        s.col = INK[:3] + (int(255 * (0.93 + 0.07 * random.Random(s.seed).random())),)   # densité d'encre propre au trait
        if strokes: s.lens = [_len(p) for p in strokes]; s.total = sum(s.lens)

    def pos(s, t):
        """déplacements : anticipation + dépassement (Williams p. 273-284) et trajectoire en arc (p. 90)."""
        x, y = s.x, s.y
        for t0, t1, x1, y1 in (s.moves or []):
            u = (t - t0) / (t1 - t0) if t1 > t0 else (1.0 if t >= t0 else 0.0)
            k = ease_back(u, s.antic) if s.antic else smooth(u)
            kk = clamp01(u)
            x, y = x + (x1 - x) * k, y + (y1 - y) * k - s.arc * 4 * kk * (1 - kk)
        return x, y

    def etat(s, t):
        if t < s.t_in or (s.hide is not None and t >= s.hide): return None
        x, y = s.pos(t)
        sc, sx = s.scale, 1.0
        rot = s.rot + s.spin * (t - s.t_in) + (s.rot_fn(t) if s.rot_fn else 0)
        if s.pop:
            k = spring(t - s.t_in); sc *= k; sx = 1 + (1 - k) * 0.35
        if s.drop:   # tombe d'en haut et atterrit à t_in + 0.2 avec écrasement
            u = t - s.t_in; T = 0.2
            if u < T: y -= 700 * (1 - (u / T) ** 2)
            else:
                v = u - T; k = math.exp(-9 * v) * math.cos(24 * v) * 0.25
                sx, sc = 1 + k * 0.7, sc * (1 - k)
        if s.respire and t > s.t_in + 0.4:          # vie au repos : respiration
            sc *= 1 + s.respire * math.sin(2 * math.pi * 0.9 * t + s.seed % 7)
        if s.out is not None and s.sortie_antic and s.out - 0.12 < t <= s.out:   # anticipation de la sortie
            k = smooth((t - (s.out - 0.12)) / 0.12); sc *= 1 - 0.14 * k; sx *= 1 + 0.16 * k
        if s.out is not None and t > s.out:
            v = t - s.out; y += 4200 * v * v - 420 * v; rot += s.chute_dir * 70 * v
            if y > H / 2 + 600: return None
        return x, y, max(sc, 0.0), sx, rot

    def rendu(s, img, drw, t):
        e = s.etat(t)
        if e is None or e[2] < 0.01: return
        x, y, sc, sx, rot = e
        if s.img is not None:
            g = s.img
            gi = g.resize((max(1, int(g.width * sc * sx)), max(1, int(g.height * sc))), Image.LANCZOS)
            if rot: gi = gi.rotate(-rot, resample=Image.BICUBIC, expand=True)
            img.alpha_composite(gi, (int(CX + x - gi.width / 2), int(CY + y - gi.height)))
            return
        if s.pose_fn:                              # traits recalculés à chaque image (personnage articulé)
            s.strokes = s.pose_fn(t); s.lens = [_len(q) for q in s.strokes]; s.total = sum(s.lens)
        p = 1.0 if s.draw <= 0 else smooth((t - s.t_in) / s.draw)
        reste = s.total * p
        rnd = random.Random(s.seed * 7919 + int(t * 12))
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        def tr(px, py):
            px, py = px * sc * sx, py * sc
            return (CX + x + px * ca - py * sa + rnd.uniform(-s.boil, s.boil),
                    CY + y + px * sa + py * ca + rnd.uniform(-s.boil, s.boil))
        w = max(2, s.width * min(1.0, 0.4 + 0.6 * sc))
        n_ext = len(s.strokes) if s.epais is None else s.epais
        for i, (pts, L) in enumerate(zip(s.strokes, s.lens)):
            if reste <= 0: break
            q = pts if reste >= L else _partial(pts, reste)
            reste -= L
            if len(q) < 2: continue
            tq = arrondi([tr(*a) for a in q])
            ferme = q is pts and len(pts) > 8 and math.dist(pts[0], pts[-1]) < 2
            if ferme and s.creux: drw.polygon(tq, fill=(0, 0, 0, 0))     # forme fermée : efface ce qu'il y a dessous
            if s.fill and q is pts: drw.polygon(tq, fill=INK)
            trait(drw, tq, w * (1.35 if i < n_ext else 0.55), s.col)
        if p >= 1:
            for dx, dy, r in s.dots:
                a = tr(dx, dy); rr = r * sc
                drw.ellipse((a[0] - rr, a[1] - rr, a[0] + rr, a[1] + rr), fill=INK)

def mot(texte, taille):
    """image du mot (hauteur = ascent + descent + 10) ; renvoie (image, largeur, descent) pour aligner les lignes de base."""
    f = ImageFont.truetype(FONT_PATH, taille)
    asc, desc = f.getmetrics()
    l, t, r, b = f.getbbox(texte)
    im = Image.new("RGBA", (r - l + 20, asc + desc + 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - l, 0), texte, font=f, fill=INK)
    return im, r - l, desc + 10

def rendre(elements, duree, nom, out_dir, fps=60, sortie=(1280, 720)):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    def pipe(f, opts):
        return subprocess.Popen([ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps),
                                 "-i", "-", "-vf", f"scale={sortie[0]}:{sortie[1]}:flags=lanczos", *opts,
                                 os.path.join(out_dir, f)], stdin=subprocess.PIPE)
    pa = pipe(nom + "_alpha.mov", ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le"])
    pf = pipe(nom + ".mov", ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"])
    import numpy as np
    papier, encre = textures()
    b = np.array(BEIGE, np.float32)
    fond_np = np.clip(b[None, None, :] * (0.93 + 0.12 * papier[..., None]), 0, 255).astype(np.uint8)
    fond = Image.fromarray(np.dstack([fond_np, np.full((H, W), 255, np.uint8)]), "RGBA")
    for n in range(int(round(duree * fps))):
        t = n / fps
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); drw = ImageDraw.Draw(img)
        for e in elements: e.rendu(img, drw, t)
        a = encrer(np.array(img), papier, encre); img = Image.fromarray(a, "RGBA")
        pa.stdin.write(img.tobytes())
        f = fond.copy(); f.alpha_composite(img); pf.stdin.write(f.tobytes())
    for p in (pa, pf): p.stdin.close(); p.wait()
    print("ok", nom)

def apercu(elements, temps, chemin, cols=4):
    import numpy as np
    papier, encre = textures(); b = np.array(BEIGE, np.float32)
    fond = np.clip(b[None, None, :] * (0.93 + 0.12 * papier[..., None]), 0, 255).astype(np.uint8)
    ims = []
    for t in temps:
        calque = Image.new("RGBA", (W, H), (0, 0, 0, 0)); drw = ImageDraw.Draw(calque)
        for e in elements: e.rendu(calque, drw, t)
        a = encrer(np.array(calque), papier, encre)
        img = Image.fromarray(np.dstack([fond, np.full((H, W), 255, np.uint8)]), "RGBA"); img.alpha_composite(Image.fromarray(a, "RGBA"))
        d = ImageDraw.Draw(img); d.text((20, 20), f"{t:.2f}s", fill=(200, 0, 0, 255), font=ImageFont.truetype(FONT_PATH, 60))
        ims.append(img.resize((480, 270)))
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (480 * cols, 270 * rows), (0, 0, 0))
    for i, im in enumerate(ims): sheet.paste(im.convert("RGB"), ((i % cols) * 480, (i // cols) * 270))
    sheet.save(chemin)
