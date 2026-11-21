"""Version B3 : typographie animée, police du titre (Annapurna SIL), minuscules discrètes + MOTS-CLÉS en capitales espacées,
mots affichés en entier (temps de lecture), composition resserrée au centre, flou de mouvement sur tout,
transitions par zoom arrière et balayages, mots animés selon leur sens (BIBLE_ANIMATION.md).
Calé au mot (Whisper) sur EXPORTS/IF_EP01.mp3. Écran vierge au début et à la fin.
    uv run --with pillow --with numpy --with imageio-ffmpeg python IF/EP01/MOTION_INTRO/scripts/intro_texte_v3.py [apercu]"""
import os, sys, math, random, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import doodle
from doodle import (W, H, CX, CY, INK, BEIGE, El, smooth, spring, ease_back, clamp01, textures, encrer,
                    souligne, bulle, gribouillis, engrenage, interrogation, horloge, aiguille, circle, FONT_PATH)
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

FPS, DUREE, ECH = 24, 18.8, 8          # ECH = sous-images par image pour le flou de mouvement (obturateur 180°)
PETIT, CAPS = 60, 92
_pol = {}
IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
def police(t, chemin=FONT_PATH):
    if (t, chemin) not in _pol: _pol[(t, chemin)] = ImageFont.truetype(chemin, t)
    return _pol[(t, chemin)]
def cap(s): return s.upper()

def image_texte(texte, taille, approche=0.0, couleur=INK, chemin=FONT_PATH):
    """texte -> (image, largeur, x de la ligne de base dans l'image, y de la ligne de base, positions des lettres)."""
    f = police(taille, chemin); asc, desc = f.getmetrics(); tr = approche * taille
    pos, x = [], 0.0
    for c in texte:
        pos.append(x); x += f.getlength(c) + tr
    w = int(x - tr) + 40
    im = Image.new("RGBA", (w, asc + desc + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for c, px in zip(texte, pos): d.text((20 + px, 20), c, font=f, fill=couleur)
    return im, x - tr, 20, 20 + asc, pos

class Mot:
    """un mot entier (ou une lettre) ; effet(t) -> dict(dx, dy, sx, sy, rot, a) ; pivot = 'centre' ou 'gauche'."""
    def __init__(s, texte, taille, x, base, effet, groupe, pivot="centre", approche=0.0, chemin=FONT_PATH):
        im, w, ox, oy, s.pos = image_texte(texte, taille, approche, chemin=chemin)
        s.w, s.taille, s.groupe, s.effet, s.x, s.base = w, taille, groupe, effet, x, base
        px, py = (x + w / 2, base - 0.33 * taille) if pivot == "centre" else (x, base)
        il, it = x - ox, base - oy                                    # coin haut-gauche de l'image (repère centré)
        cxp, cyp = px - il, py - it
        R = int(max(cxp, im.width - cxp, cyp, im.height - cyp)) + 4
        pad = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0)); pad.paste(im, (int(R - cxp), int(R - cyp)))
        s.img, s.px, s.py = pad, px, py
    def dessine(s, calque, t):
        if t < 0.05 or s.effet is None: return                    # écran vierge au départ
        e = s.effet(t)
        if not e or e.get("a", 1) <= 0.003: return
        g = s.img
        sx, sy = e.get("sx", 1.0), e.get("sy", 1.0)
        if abs(sx - 1) > 1e-3 or abs(sy - 1) > 1e-3:
            g = g.resize((max(2, int(g.width * sx)), max(2, int(g.height * sy))), Image.BILINEAR)
        if abs(e.get("rot", 0)) > 0.05: g = g.rotate(e["rot"], resample=Image.BICUBIC, expand=True)
        a = e.get("a", 1.0)
        if a < 0.999:
            al = g.getchannel("A").point(lambda v: int(v * a)); g = g.copy(); g.putalpha(al)
        calque.alpha_composite(g, (int(CX + s.px + e.get("dx", 0) - g.width / 2), int(CY + s.py + e.get("dy", 0) - g.height / 2)))

# ------------------------------------------------ effets ------------------------------------------------
def pose(t0, haut=-22):
    def f(t):
        u = t - (t0 - 0.07)
        if u < 0: return None
        k = ease_back(clamp01(u / 0.26), 0.9); s = 0.94 + 0.06 * smooth(u / 0.2)
        return dict(a=smooth(u / 0.14), dy=haut * (1 - k), sx=s, sy=s)
    return f
def lourd(t0):
    def f(t):
        u = t - t0
        if u < -0.16: return None
        if u < 0: return dict(a=smooth((u + 0.16) / 0.06), dy=-90 * (-u / 0.16) ** 2)
        q = math.exp(-11 * u) * math.cos(24 * u)
        return dict(sy=1 - 0.14 * q, sx=1 + 0.08 * q)
    return f
def debout(t0):
    def f(t):
        u = t - (t0 - 0.06)
        if u < 0: return None
        return dict(a=smooth(u / 0.1), rot=-90 * (1 - ease_back(clamp01(u / 0.42), 1.1)))
    return f
def enfle(t0):
    def f(t):
        u = t - (t0 - 0.12)
        if u < 0: return None
        if u < 0.1: return dict(a=smooth(u / 0.08), sx=0.55, sy=0.55)
        if u < 0.18: s = 0.55 - 0.08 * smooth((u - 0.1) / 0.08); return dict(sx=s, sy=s)          # anticipation
        v = u - 0.18; s = 1 - 0.53 * math.exp(-7 * v) * math.cos(15 * v)
        return dict(sx=s, sy=s)
    return f
def fort(t0):
    def f(t):
        u = t - t0
        if u < -0.16: return None
        if u < 0: k = (-u / 0.16) ** 2; s = 1 + 0.9 * k; return dict(a=smooth((u + 0.16) / 0.06), sx=s, sy=s)
        b = math.exp(-6.5 * u) * math.cos(17 * u)                     # accent dur : rebond élastique de l'échelle
        return dict(sx=1 + 0.22 * b, sy=1 + 0.30 * b)
    return f
def rapide(t0, dist=1400):
    def f(t):
        u = t - (t0 - 0.12)
        if u < 0: return None
        if u < 0.15: p = 1 - (1 - u / 0.15) ** 3; return dict(dx=-dist * (1 - p), sx=1 + 0.45 * (1 - p))
        v = u - 0.15
        return dict(dx=34 * math.exp(-8 * v) * math.sin(16 * v))     # accent doux : dépasse un peu et revient
    return f
def hesite(t0):
    def f(t):
        u = t - (t0 - 0.2)
        if u < 0: return None
        p = smooth(u / 0.5)
        return dict(a=p, dy=-26 * (1 - p), rot=3 * math.sin(11 * u) * (1 - p))
    return f
def reflechit(t0):
    g = pose(t0)
    def f(t):
        e = g(t)
        if e and t > t0 + 0.3: e["rot"] = 2.6 * math.sin(3.4 * (t - t0 - 0.3))
        return e
    return f
def pret(t0):
    def f(t):
        u = t - (t0 - 0.34)
        if u < 0: return None
        if t < t0: q = smooth(u / 0.3); return dict(a=smooth(u / 0.1), sy=1 - 0.3 * q, sx=1 + 0.12 * q)   # se tasse
        v = t - t0; b = math.exp(-10 * v) * math.cos(26 * v)
        return dict(sy=1 + 0.18 * b - 0.0, sx=1 - 0.07 * b)
    return f

# ------------------------------------------------ groupes / transitions ------------------------------------------------
GROUPES = {}      # id -> (debut, fin, transition, t_trans)
def groupe(i, debut, fin, sortie):
    GROUPES[i] = (debut, fin, sortie)
def etat_groupe(i, t):
    debut, fin, (mode, ts, te) = GROUPES[i]
    if t < debut or t > fin: return None
    k = smooth((t - ts) / (te - ts)) if t > ts else 0.0
    if mode == "zoom": return dict(s=1 - 0.5 * k, a=1 - k)
    if mode == "balayage": return dict(cut=-W / 2 - 200 + (W + 400) * k)
    if mode == "pousse": return dict(dx=2000 * k ** 2)
    return dict()

ITEMS = []        # (groupe, objet) — objet = Mot | El (doodle) | Ampoule
def compose(gid, lignes, interligne=1.32):
    """lignes = [[(texte, taille, effet, pivot, approche), ...], ...] -> mots centrés ; renvoie {texte: Mot}."""
    hs = [max(m[1] for m in l) * interligne for l in lignes]
    y = -sum(hs) / 2; out = {}
    for l, h in zip(lignes, hs):
        y += h; base = y - h * 0.24
        ims = [image_texte(m[0], m[1], m[4] if len(m) > 4 else 0) for m in l]
        esp = PETIT * 0.36
        x = -(sum(i[1] for i in ims) + esp * (len(l) - 1)) / 2
        for m, i in zip(l, ims):
            mot = Mot(m[0], m[1], x, base, m[2], gid, m[3] if len(m) > 3 else "centre", m[4] if len(m) > 4 else 0)
            ITEMS.append((gid, mot)); out[m[0]] = mot; x += i[1] + esp
    return out

# ---------- ampoules : bulbe en couleur, halo dégradé quand elles s'allument ----------
_halo = {}
def halo(r):
    if r not in _halo:
        R = int(r * 4.2); yy, xx = np.mgrid[-R:R, -R:R]; d = np.sqrt(xx ** 2 + yy ** 2) / R
        a = np.clip(1 - d, 0, 1) ** 2.2
        im = np.zeros((2 * R, 2 * R, 4), np.uint8); im[..., 0], im[..., 1], im[..., 2] = 255, 196, 70
        im[..., 3] = (a * 255).astype(np.uint8); _halo[r] = Image.fromarray(im, "RGBA")
    return _halo[r]
class Ampoule:
    def __init__(s, x, y, r, t_on, t_in, groupe):
        s.x, s.y, s.r, s.t_on, s.t_in, s.groupe = x, y, r, t_on, t_in, groupe
    def dessine(s, calque, t):
        if t < s.t_in: return
        a0 = smooth((t - s.t_in) / 0.15)
        u = t - s.t_on
        lum = 0.0 if u < 0 else min(1.0, u / 0.05) * (1 + 0.5 * math.exp(-8 * u)) * (0.92 + 0.08 * math.sin(23 * t + s.x))
        x, y, r = CX + s.x, CY + s.y, s.r
        if lum > 0:
            h = halo(int(r)); hh = h.copy(); hh.putalpha(h.getchannel("A").point(lambda v: int(v * min(1, 0.95 * lum))))
            calque.alpha_composite(hh, (int(x - hh.width / 2), int(y - hh.height / 2)))
        d = ImageDraw.Draw(calque)
        verre = (255, 244, 190, int(255 * a0 * min(1, lum))) if lum > 0 else (0, 0, 0, 0)
        d.ellipse((x - r, y - r, x + r, y + r), fill=verre)
        jaune = (226, 160, 40, int(255 * a0))
        d.arc((x - r, y - r, x + r, y + r), 120, 420, fill=jaune, width=max(3, int(r * 0.26)))
        enc = INK[:3] + (int(255 * a0),)
        for k, yy in enumerate((r * 0.95, r * 1.22, r * 1.48)):
            ww = r * (0.42 - 0.08 * k); d.line([(x - ww, y + yy), (x + ww, y + yy)], fill=enc, width=max(2, int(r * 0.14)))
        d.line([(x - r * .28, y + r * .2), (x - r * .12, y - r * .2), (x, y + r * .2), (x + r * .12, y - r * .2), (x + r * .28, y + r * .2)],
               fill=enc, width=max(1, int(r * 0.08)))

# =================================================== SCÈNES ===================================================
# 1. « À travers les âges et les époques »
groupe(1, 0.0, 2.50, ("zoom", 2.12, 2.48))
m = compose(1, [[("à", PETIT, pose(0.05)), ("travers", PETIT, rapide(0.30, 260)), ("les", PETIT, pose(0.54)), (cap("âges"), CAPS, lourd(0.78), "centre", 0.06)],
                [("et", PETIT, pose(1.20)), ("les", PETIT, pose(1.32)), (cap("époques"), CAPS, pose(1.48), "centre", 0.06)]])
ep = m["ÉPOQUES"]; ITEMS.append((1, El(souligne(ep.w + 10), ep.x + ep.w / 2, ep.base + 22, epais=0, t_in=1.72, draw=0.32, width=5)))

# 2. « L'homme, dans son immense ingéniosité » — les ampoules remplacent les points des « i »
groupe(2, 2.40, 5.70, ("balayage", 5.30, 5.66))
m = compose(2, [[(cap("l'homme,"), CAPS, debout(2.56), "gauche", 0.06)],
                [("dans", PETIT, pose(3.44)), ("son", PETIT, pose(3.54)), (cap("immense"), CAPS, enfle(3.76), "centre", 0.06)],
                [("ıngénıosıté,", 70, pose(4.20))]], interligne=1.45)
ing = m["ıngénıosıté,"]; f = police(70)
for j, (c, px) in enumerate(zip("ıngénıosıté,", ing.pos)):
    if c == "ı":
        ITEMS.append((2, Ampoule(ing.x + px + f.getlength(c) / 2, ing.base - 70 * 0.98, 18, 4.32 + 0.14 * j / 4, 4.18, 2)))

# 3. « a fait évoluer son comportement et ses idées »
groupe(3, 5.55, 8.55, ("zoom", 8.18, 8.52))
lignes3 = [[("a", PETIT, pose(5.70)), ("fait", PETIT, pose(5.82))], [("son", PETIT, pose(6.42)), ("comportement", PETIT, pose(6.64))],
           [("et", PETIT, pose(7.40)), ("ses", PETIT, pose(7.60)), (cap("idées."), CAPS, lourd(7.78), "centre", 0.06)]]
m = compose(3, lignes3)
# « ÉVOLUER » : lettre par lettre, elles se redressent (positions fixes : aucune superposition)
fa = m["fait"]; ft = police(CAPS); x0 = fa.x + fa.w + PETIT * 0.36; tr = 0.06 * CAPS
for k, c in enumerate(cap("évoluer")):
    def ev(t, k=k):
        u = t - (5.94 - 0.08)
        if u < 0: return None
        g = smooth((t - (5.96 + 0.07 * k)) / 0.24)
        return dict(a=smooth(u / 0.12), rot=-26 * (1 - g), sx=0.72 + 0.28 * g, sy=0.72 + 0.28 * g)
    lettre = Mot(c, CAPS, x0, fa.base, ev, 3); ITEMS.append((3, lettre)); x0 += ft.getlength(c) + tr
# recentre la 1re ligne (a fait + ÉVOLUER)
dx1 = -(x0 - tr - (m["a"].x)) / 2 - m["a"].x
for gid, it in ITEMS:
    if gid == 3 and isinstance(it, Mot) and abs(it.base - fa.base) < 1: it.px += dx1
co = m["comportement"]                                    # « comportement » se dandine doucement (mot entier, lisible)
_co = co.effet; co.effet = lambda t: (lambda e: e and dict(e, dy=e.get("dy", 0) + 5 * math.sin(9 * (t - 6.64)) * math.exp(-1.6 * max(0, t - 6.64)) * (t > 6.64), rot=2.2 * math.sin(7 * (t - 6.64)) * math.exp(-1.6 * max(0, t - 6.64)) * (t > 6.64)))(_co(t))
ide = m["IDÉES."]; ITEMS.append((3, El(bulle(), ide.x + ide.w + 120, ide.base - 120, epais=1, t_in=7.95, pop=True, draw=0.25, scale=0.42, width=5)))
ITEMS.append((3, El(gribouillis(4, rx=60, ry=30), ide.x + ide.w + 120, ide.base - 120, epais=0, t_in=8.02, draw=0.25, width=4)))

# 4a. « Il s'est rendu plus productif » — PRODUCTIF est un mécanisme à volets (split-flap)
groupe(4, 8.45, 10.62, ("zoom", 10.28, 10.6))
m = compose(4, [[("il", PETIT, pose(8.68)), ("s'est", PETIT, pose(8.76)), ("rendu", PETIT, pose(8.92))], [("plus", PETIT, pose(9.26))]])
pl = m["plus"]; x0 = pl.x + pl.w + PETIT * 0.36; tr = 0.07 * CAPS
ALPHA = "ABCDEFGHIJKLMNOPRSTUVZ"
largeurs = [ft.getlength(c) for c in "PRODUCTIF,"]
total = sum(largeurs) + tr * 9; dx2 = -(x0 + total - pl.x) / 2 - pl.x
for gid, it in ITEMS:
    if gid == 4 and it is pl: it.px += dx2
x0 += dx2
for k, c in enumerate("PRODUCTIF,"):
    cell = largeurs[k]; t_lock = 9.40 + 0.055 * k
    finale = Mot(c, CAPS, x0, pl.base, None, 4)
    volets = {}
    def flap(t, k=k, finale=finale, cell=cell, t_lock=t_lock, x=x0):
        u = t - 9.18
        if u < 0: return None
        if t >= t_lock:
            v = t - t_lock; return ("fin", dict(sy=1 - 0.22 * math.exp(-22 * v) * math.cos(40 * v)))
        ph = u / 0.055; n = int(ph); q = ph - n
        ch = random.Random(k * 977 + n).choice(ALPHA)
        return ("vol", ch, dict(sy=0.25 + 0.75 * abs(math.cos(math.pi * q)), a=smooth(u / 0.08)))
    class Volet:
        def __init__(s, k, finale, cell, flap, x): s.k, s.finale, s.cell, s.flap, s.x = k, finale, cell, flap, x
        def dessine(s, calque, t):
            r = s.flap(t)
            if r is None: return
            if r[0] == "fin": s.finale.effet = lambda tt, e=r[1]: e; s.finale.dessine(calque, t); return
            ch, e = r[1], r[2]
            key = (ch, s.k)
            if key not in volets: volets[key] = Mot(ch, CAPS, s.x + (s.cell - min(s.cell, ft.getlength(ch))) / 2, pl.base, None, 4)
            mm = volets[key]; sc = min(1.0, s.cell / max(ft.getlength(ch), 1))
            e = dict(e, sx=sc); mm.effet = lambda tt, e=e: e; mm.dessine(calque, t)
    ITEMS.append((4, Volet(k, finale, cell, flap, x0))); x0 += cell + tr
def cran(t, t1=9.2, t2=10.0, vit=200):                    # les engrenages tournent pendant le mécanisme puis s'arrêtent net
    return vit * (min(t, t2) - t1) + (6 * math.exp(-15 * (t - t2)) * math.sin(50 * (t - t2)) if t > t2 else 0)
gx = x0 + 70
ITEMS.append((4, El(engrenage(34, 9), gx, pl.base - 40, epais=1, t_in=9.18, pop=True, width=5, rot_fn=lambda t: cran(t))))
ITEMS.append((4, El(engrenage(22, 7), gx + 48, pl.base - 84, epais=1, t_in=9.24, pop=True, width=5, rot_fn=lambda t: -cran(t) * 34 / 22 + 14)))

# 4b. « plus fort » : l'échelle claque et rebondit
groupe(5, 10.40, 11.58, ("pousse", 11.40, 11.56))
m5 = compose(5, [[("plus", PETIT, pose(10.54)), ("fort,", 76, None, "gauche", 0.0)]])
_bas = m5["fort,"]; ITEMS.remove((5, _bas)); _pl = m5["plus"]
_impact = Mot("FORT,", 118, _bas.x, _bas.base, None, 5, "gauche", 0.02, chemin=IMPACT)
_dx = -(_impact.w - _bas.w) / 2                                       # recentre la ligne sur la version finale
for it_ in (_pl, _bas, _impact): it_.px += _dx
def _fort_bas(t):                                                     # « fort » arrive, puis se tasse (anticipation)
    u = t - (10.60 - 0.07)
    if u < 0 or t >= 10.74: return None
    e = pose(10.60)(t) or {}
    if t > 10.62: q = smooth((t - 10.62) / 0.12); e.update(sy=1 - 0.35 * q, sx=1 + 0.18 * q)
    return e
def _fort_impact(t):                                                  # ... et devient FORT (Impact) : l'échelle claque et rebondit
    v = t - 10.74
    if v < 0: return None
    b = math.exp(-6.5 * v) * math.cos(17 * v)
    return dict(sx=1 + 0.26 * b, sy=1 + 0.34 * b)
_bas.effet, _impact.effet = _fort_bas, _fort_impact
ITEMS += [(5, _bas), (5, _impact)]

# 4c. « plus rapide » : arrive en flèche (flou de mouvement)
groupe(6, 11.50, 12.62, ("zoom", 12.38, 12.60))   # « plus » reste visible pendant la fumée
T_GO = 12.20
def rapide_part(t):
    u = t - (11.72 - 0.10)
    if u < 0: return None
    if u < 0.14: p = 1 - (1 - u / 0.14) ** 3; return dict(dx=-320 * (1 - p), sx=1 + 0.25 * (1 - p), a=smooth(u / 0.06))
    if t < T_GO - 0.12: return dict(a=1.0)
    if t < T_GO: q = smooth((t - (T_GO - 0.12)) / 0.12); return dict(dx=-26 * q, sx=1 - 0.12 * q, sy=1 + 0.06 * q)   # anticipation
    v = t - T_GO
    return dict(dx=-26 + 2600 * (v / 0.24) ** 2, sx=1 + 0.7 * min(1, v / 0.12))   # démarrage en trombe (flou de mouvement)
groupe(10, 12.18, 12.76, ("aucun", 99, 100))
m6 = compose(6, [[("plus", PETIT, pose(11.62)), (cap("rapide."), 112, rapide_part, "centre", 0.05)]])
_R = m6["RAPIDE."]
class Fumee:
    """planche de 6 dessins (ASSETS/fumee), enchaînés « sur deux » (12 dessins/s), plantée derrière le R."""
    def __init__(s, x, base, t0, haut=118):
        d = os.path.join(os.path.dirname(__file__), "..", "ASSETS", "fumee")
        s.im = [Image.open(os.path.join(d, f"fumee_{i}.png")).convert("RGBA") for i in range(1, 7)]
        bb = s.im[0].getchannel("A").getbbox(); k = haut / (bb[3] - bb[1])
        s.im = [i.resize((int(i.width * k), int(i.height * k)), Image.LANCZOS) for i in s.im]
        s.ox, s.oy = bb[0] * k, bb[3] * k                              # coin bas-gauche du 1er nuage = point d'ancrage
        s.x, s.base, s.t0 = x, base, t0
        # les 2 derniers dessins viennent d'une autre rangée de la planche : on cale leur centre de masse
        # sur celui du 4e dessin (en le faisant monter un peu), sinon ils sautent de place
        def centre(im):
            a_ = np.array(im.getchannel("A"), np.float32); ys, xs = np.nonzero(a_ > 20)
            return xs.mean(), ys.mean()
        def bas(im): return im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()[3]
        c3 = centre(s.im[2]); c4 = centre(s.im[3])
        d4 = (c3[0] - c4[0] + 0.08 * haut, bas(s.im[2]) - bas(s.im[3]) - 0.06 * haut)   # le 4e se pose dans la continuité du 3e
        s.dec = [(0, 0)] * 3 + [d4]
        c4 = (c4[0] + d4[0], c4[1] + d4[1])
        for i, monte in ((4, 0.12), (5, 0.26)):
            ci = centre(s.im[i]); s.dec.append((c4[0] - ci[0] + 0.05 * haut * (i - 3), c4[1] - ci[1] - monte * haut))
    CADENCE = 28.8                                                     # dessins/s (24 + 20 %)
    def dessine(s, calque, t):
        u = (t - s.t0) * s.CADENCE; n = int(u)
        if n < 0 or n > 5: return
        p = u / 6                                                      # avancement 0 -> 1 de toute la séquence
        a = 1.0 if p < 0.35 else max(0.0, 1 - smooth((p - 0.35) / 0.65))   # disparition en opacité
        k = 1 + 0.02 * smooth(p)                                       # très léger agrandissement (2 %)…
        im = s.im[n]; dx, dy = s.dec[n]
        x0, y0 = CX + s.x - s.ox + dx, CY + s.base - s.oy + dy           # base du nuage = ligne de base du mot
        g = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        if a < 1: g.putalpha(g.getchannel("A").point(lambda v: int(v * a)))
        # …dont l'origine est le coin bas-droit de l'image
        calque.alpha_composite(g, (int(x0 + im.width - g.width), int(y0 + im.height - g.height)))
_fu = Fumee(0, _R.base, T_GO, haut=72)
_larg = _fu.im[0].getchannel("A").getbbox(); _larg = _larg[2] - _larg[0]
_bbR = police(112).getbbox("R")                                        # jambage avant du R = bord droit du glyphe
_pointe = _R.px - _R.w / 2 + _bbR[0] + 0.20 * (_bbR[2] - _bbR[0])     # pointe de la fumée : on voit 80 % du R
_fu.x = _pointe - _larg                                                # le nuage part de là vers la gauche, sur « plus »
ITEMS.append((10, _fu))

# 5. « Encore faut-il qu'il réfléchisse »
groupe(7, 12.55, 15.20, ("zoom", 14.86, 15.18))
m = compose(7, [[("encore", PETIT, hesite(12.82)), ("faut-il", PETIT, hesite(13.20))],
                [("qu'il", PETIT, pose(13.68)), (cap("réfléchisse,"), CAPS, reflechit(13.94), "centre", 0.05)]])
rf = m["RÉFLÉCHISSE,"]
ITEMS.append((7, El(interrogation(), rf.x + rf.w + 55, rf.base - 8, epais=0, t_in=14.30, pop=True, scale=1.0, dots=[(0, 14, 6)], width=6,
                    rot_fn=lambda t: 12 * math.sin(6 * t))))

# 6. « et qu'il soit prêt »
groupe(8, 15.0, 17.02, ("balayage", 16.62, 16.98))
m = compose(8, [[("et", PETIT, pose(15.24)), ("qu'il", PETIT, pose(15.32)), ("soit", PETIT, pose(15.48)), (cap("prêt."), 108, pret(15.72), "centre", 0.05)]])
pr = m["PRÊT."]
def aig(t):
    T = 15.72
    if t < T: return 1300 * (t - 15.3)
    b = 1300 * (T - 15.3); return b + (360 - b % 360) + 14 * math.exp(-12 * (t - T)) * math.sin(40 * (t - T))
cx_h = pr.x + pr.w + 80
ITEMS.append((8, El(horloge(44), cx_h, pr.base - 40, epais=1, t_in=15.3, pop=True, width=5)))
ITEMS.append((8, El(aiguille(34), cx_h, pr.base - 40, epais=0, t_in=15.3, pop=True, rot_fn=aig, width=5)))

# 7. « Et si… » puis écran vierge
groupe(9, 16.95, 18.62, ("zoom", 18.22, 18.58))
m = compose(9, [[("et si", 120, lourd(17.16))]])
es = m["et si"]
for k in range(3):
    ITEMS.append((9, El([circle(0, 0, 3, 10)], es.x + es.w + 34 + 44 * k, es.base - 6, t_in=17.55 + 0.2 * k, drop=True, dots=[(0, 0, 10)])))

# =================================================== RENDU ===================================================
def calque_a(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for gid in GROUPES:
        g = etat_groupe(gid, t)
        if g is None: continue
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        for gg, it in ITEMS:
            if gg != gid: continue
            if isinstance(it, El): it.rendu(c, d, t)
            else: it.dessine(c, t)
        if "s" in g and g["s"] < 0.999:
            s = max(g["s"], 0.05); cc = c.resize((int(W * s), int(H * s)), Image.BILINEAR)
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); c.alpha_composite(cc, (int((W - cc.width) / 2), int((H - cc.height) / 2)))
        if g.get("dx"):
            cc = c; c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); c.alpha_composite(cc, (int(g["dx"]), 0)) if g["dx"] < W else None
        a = np.array(c, np.float32)
        if "a" in g: a[..., 3] *= max(g["a"], 0)
        if "cut" in g:
            xs = np.arange(W) - W / 2; m_ = np.clip((xs - g["cut"]) / 140, 0, 1); a[..., 3] *= m_[None, :]
        img.alpha_composite(Image.fromarray(a.astype(np.uint8), "RGBA"))
    return img

def image(t):
    """flou de mouvement : moyenne prémultipliée de ECH sous-images sur un demi-intervalle."""
    acc = np.zeros((H, W, 4), np.float32)
    for j in range(ECH):
        a = np.array(calque_a(t + j / ECH * 0.5 / FPS), np.float32)
        acc[..., :3] += a[..., :3] * a[..., 3:4] / 255; acc[..., 3] += a[..., 3]
    acc /= ECH
    rgb = np.where(acc[..., 3:4] > 0, acc[..., :3] * 255 / np.maximum(acc[..., 3:4], 1e-3), 0)
    return np.dstack([np.clip(rgb, 0, 255), acc[..., 3]]).astype(np.uint8)

def sortie(nom, dossier, sortie_px=(1280, 720)):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    papier, encre = textures(); b = np.array(BEIGE, np.float32)
    fond = np.clip(b[None, None, :] * (0.93 + 0.12 * papier[..., None]), 0, 255)
    def pipe(f, opts):
        return subprocess.Popen([ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                 "-vf", f"scale={sortie_px[0]}:{sortie_px[1]}:flags=lanczos", *opts, os.path.join(dossier, f)], stdin=subprocess.PIPE)
    pa = pipe(nom + "_alpha.mov", ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le"])
    pf = pipe(nom + ".mov", ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"])
    for n in range(int(round(DUREE * FPS))):
        a = encrer(image(n / FPS), papier, encre)
        pa.stdin.write(a.tobytes())
        al = a[..., 3:4].astype(np.float32) / 255
        full = (fond * (1 - al) + a[..., :3] * al).astype(np.uint8)
        pf.stdin.write(np.dstack([full, np.full((H, W), 255, np.uint8)]).tobytes())
    for p in (pa, pf): p.stdin.close(); p.wait()
    print("ok", nom)

def apercu(temps, chemin, cols=6):
    papier, encre = textures(); b = np.array(BEIGE, np.float32)
    fond = np.clip(b[None, None, :] * (0.93 + 0.12 * papier[..., None]), 0, 255)
    ims = []
    for t in temps:
        a = encrer(image(t), papier, encre); al = a[..., 3:4].astype(np.float32) / 255
        im = Image.fromarray((fond * (1 - al) + a[..., :3] * al).astype(np.uint8))
        ImageDraw.Draw(im).text((20, 20), f"{t:.2f}s", fill=(200, 0, 0), font=police(50)); ims.append(im.resize((480, 270)))
    rows = (len(ims) + cols - 1) // cols; sh = Image.new("RGB", (480 * cols, 270 * rows))
    for i, im in enumerate(ims): sh.paste(im, ((i % cols) * 480, (i // cols) * 270))
    sh.save(chemin)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        apercu([0.02, 0.4, 1.0, 2.0, 2.3, 2.7, 3.86, 4.7, 5.45, 6.2, 7.0, 8.1, 9.3, 9.9, 10.66, 10.85, 11.66, 11.79, 12.1, 12.55, 14.5, 15.5, 15.9, 18.75],
               sys.argv[1])
    else:
        sortie("intro_texte_v3_24p", os.path.join(os.path.dirname(__file__), "..", "3_RESULTATS"))
