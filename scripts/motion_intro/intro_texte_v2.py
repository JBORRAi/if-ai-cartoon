"""Version B2 : typographie animée « doodle » — chaque mot bouge selon ce qu'il exprime (BIBLE_ANIMATION.md) :
« travers » traverse en sautillant, « âges » tombe lourd, « L'homme » se relève, « immense » enfle (take),
les « i » d'« ingéniosité » s'allument, « évoluer » se redresse lettre par lettre, « fort » écrase et fait sursauter
les autres mots, « rapide » file et dépasse, « réfléchisse » se gratte la tête, « prêt » se tasse puis claque.
Écran vierge au début et à la fin ; une phrase à la fois ; calé au mot (Whisper) sur EXPORTS/IF_EP01.mp3.
    uv run --with pillow --with numpy --with imageio-ffmpeg python IF/EP01/MOTION_INTRO/scripts/intro_texte_v2.py [apercu]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from doodle import *

POLICE = "/System/Library/Fonts/Supplemental/Noteworthy.ttc"
BASE = 112
DUREE = 18.8
_cache = {}
def glyphe(c, taille):
    k = (c, taille)
    if k not in _cache:
        f = ImageFont.truetype(POLICE, taille, index=1)
        asc, desc = f.getmetrics(); l, t, r, b = f.getbbox(c)
        w = max(r - l, 4) + 24
        im = Image.new("RGBA", (w, asc + desc + 16), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((12 - l, 4), c, font=f, fill=INK)
        _cache[k] = (im, desc + 12)
    return _cache[k]

def chute(u, h=520, d=0.2):                     # tombe en accélérant, atterrit à u = 0
    return 0.0 if u >= 0 else (h if u < -d else h * (u / -d) ** 2)

class Lettre(El):
    """une lettre : comportement = fonction(t, lettre) -> dict(dx, dy, sc, sx, rot) ; frémissement « boil » 12 i/s."""
    def __init__(s, c, taille, x, base_y, t_in, comp, out, k=0, ecran=0):
        im, d = glyphe(c, taille)
        super().__init__(img=im, x=x, y=base_y + d, t_in=t_in, out=out, chute_dir=(-1) ** k)
        s.c, s.comp, s.k, s.ecran, s.taille = c, comp, k, ecran, taille
    def etat(s, t):
        if t < s.t_in or t < 0.05: return None                 # écran vierge au départ
        e = s.comp(t, s)
        if e is None: return None
        x, y = s.x + e.get("dx", 0), s.y - e.get("dy", 0)
        sc, sx, rot = e.get("sc", 1.0), e.get("sx", 1.0), e.get("rot", 0.0)
        for t0, amp in SURSAUTS:                      # réaction : les mots déjà posés sursautent (chevauchement)
            u = t - t0 - 0.03 * s.k
            if s.ecran == ECRAN_FORT and 0 < u < 0.4 and not e.get("source"): y -= amp * math.sin(math.pi * u / 0.4) * math.exp(-3 * u)
        r = random.Random(s.seed * 31 + int(t * 12))
        x += r.uniform(-1.3, 1.3); y += r.uniform(-1.3, 1.3); rot += r.uniform(-0.8, 0.8)
        if s.out is not None and s.out - 0.12 < t <= s.out:
            q = smooth((t - (s.out - 0.12)) / 0.12); sc *= 1 - 0.12 * q; sx *= 1 + 0.14 * q
        if s.out is not None and t > s.out:
            v = t - s.out; y += 4200 * v * v - 420 * v; rot += s.chute_dir * 80 * v
            if y > H / 2 + 260: return None
        return x, y, sc, sx, rot

# ---------- comportements (u = temps depuis le mot dit) ----------
def tombe(t0, k, pas=0.022):
    def f(t, L):
        u = t - (t0 - 0.05 + pas * k)
        if u < -0.2: return None
        if u < 0: return dict(dy=chute(u, 140, 0.16), sc=0.6 + 0.4 * smooth((u + 0.2) / 0.2))
        q = math.exp(-14 * u) * math.cos(30 * u) * 0.08         # objet dur : petit écrasement, retour très vite
        return dict(sc=1 - q, sx=1 + q)
    return f
def traverse(t0, k, n):
    def f(t, L):
        t_arr = t0 + 0.28 + 0.03 * k; u = (t - (t_arr - 0.75)) / 0.75
        if u < 0: return None
        if u >= 1: return dict(dy=12 * math.exp(-10 * (t - t_arr)) * abs(math.sin(25 * (t - t_arr))))
        x = -1200 * (1 - smooth(u)); pas = abs(math.sin(math.pi * 4 * u))
        return dict(dx=x, dy=40 * pas, rot=-8 * math.cos(math.pi * 4 * u))
    return f
def lourd(t0, k, poussiere=False):
    def f(t, L):
        u = t - (t0 - 0.02 + 0.03 * k)
        if u < -0.16: return None
        if u < 0: return dict(dy=chute(u, 260, 0.16), sc=0.7 + 0.3 * smooth((u + 0.16) / 0.16))
        q = math.exp(-11 * u) * math.cos(26 * u) * 0.22
        return dict(sc=1 - q, sx=1 + q * 0.8)
    return f
def debout(t0, k):
    def f(t, L):
        u = t - (t0 - 0.0 + 0.05 * k)
        if u < -0.15: return None
        if u < 0: return dict(rot=-90, sc=smooth((u + 0.15) / 0.15))
        return dict(rot=-90 * (1 - ease_back(u / 0.32, 1.2)))
    return f
def enfle(t0, k, n):
    def f(t, L):
        c = abs(k - (n - 1) / 2); u = t - (t0 - 0.12 + 0.03 * c)
        if u < 0: return None
        if u < 0.12: return dict(sc=0.3 + 0.1 * smooth(u / 0.12))           # pousse
        if u < 0.2: return dict(sc=0.4 - 0.1 * smooth((u - 0.12) / 0.08))   # anticipation : se rétracte
        v = u - 0.2
        return dict(sc=1 + 0.3 * math.exp(-6 * v) * math.cos(16 * v) * (v > 0) - 0.7 * math.exp(-40 * v))
    return f
def evolue(t0, k, n):
    def f(t, L):
        u0 = t - (t0 - 0.15 + 0.012 * k)
        if u0 < -0.2: return None
        base = dict(dy=chute(u0)) if u0 < 0 else {}
        g = smooth((t - (t0 + 0.05 + 0.07 * k)) / 0.25)                     # se redresse lettre après lettre
        base.update(rot=32 * (1 - g), sc=0.55 + 0.45 * g, dx=-8 * (1 - g))
        return base
    return f
def danse(t0, k):
    g = tombe(t0, k)
    def f(t, L):
        e = g(t, L)
        if e is None: return None
        u = t - (t0 + 0.15)
        if u > 0: e["rot"] = 9 * math.sin(14 * u + k * 1.3) * math.exp(-2.2 * u)
        return e
    return f
def machine(t0, k):
    def f(t, L):
        tk = t0 - 0.1 + 0.06 * k; u = t - tk
        if u < -0.24: return None
        if u < 0: return dict(dy=45 * math.ceil(-u / 0.06))                  # descend par crans, comme une presse
        return dict(sc=1 - 0.08 * math.exp(-20 * u))
    return f
def fort(t0, k):
    def f(t, L):
        u = t - t0
        if u < -0.32: return None
        if u < -0.12: return dict(dy=240, sc=0.9 + 0.1 * smooth((u + 0.32) / 0.2), rot=0)     # en l'air : se prépare
        if u < 0: return dict(dy=240 * (-u / 0.12) ** 2, source=1)
        q = math.exp(-9 * u) * math.cos(24 * u) * 0.3                      # accent dur : écrase et rebondit
        return dict(sc=1 - q, sx=1 + q, source=1)
    return f
def rapide(t0, k, n):
    def f(t, L):
        u = t - (t0 - 0.08 + 0.015 * k)
        if u < 0: return None
        if u < 0.16: p = smooth(u / 0.16); return dict(dx=-1500 * (1 - p), sx=1 + 1.4 * (1 - p))
        v = u - 0.16
        return dict(dx=40 * math.exp(-7 * v) * math.sin(14 * v), sx=1 - 0.12 * math.exp(-12 * v))   # accent doux : continue puis revient
    return f
def hesite(t0, k):
    def f(t, L):
        u = t - (t0 - 0.35 + 0.05 * k)
        if u < 0: return None
        p = smooth(u / 0.45)
        return dict(dy=160 * (1 - p), rot=6 * math.sin(9 * u) * (1 - p))
    return f
def gratte(t0, k):
    g = tombe(t0, k)
    def f(t, L):
        e = g(t, L)
        if e is None: return None
        u = t - (t0 + 0.25)
        if u > 0: e["rot"] = 7 * math.sin(4.5 * u) ; e["dx"] = 3 * math.sin(9 * u)
        return e
    return f
def pret(t0, k):
    def f(t, L):
        u = t - (t0 - 0.30 + 0.02 * k)
        if u < -0.2: return None
        if u < 0: return dict(dy=chute(u))
        if t < t0: q = smooth(u / 0.25); return dict(sc=1 - 0.28 * q, sx=1 + 0.22 * q)        # se tasse (anticipation)
        v = t - t0
        return dict(sc=1 + 0.18 * math.exp(-10 * v) * math.cos(26 * v) * (1 if v > 0 else 0) + 0.0, sx=1)
    return f

# ---------- écrans ----------
SURSAUTS = [(10.74, 34)]
ECRAN_FORT = 3
ECRANS = [
    ([[("À", 0.05, 1, "tombe"), ("travers", 0.24, 1, "traverse"), ("les", 0.54, 1, "tombe"), ("âges", 0.78, 1.3, "lourd")],
      [("et", 1.20, 1, "tombe"), ("les", 1.32, 1, "tombe"), ("époques", 1.48, 1.3, "tombe")]], 2.05),
    ([[("L'homme,", 2.56, 1.35, "debout")], [("dans", 3.44, 0.9, "tombe"), ("son", 3.54, 0.9, "tombe"), ("immense", 3.76, 1.45, "enfle")],
      [("ingéniosité,", 4.20, 1.15, "tombe")]], 5.15),
    ([[("a", 5.70, 1, "tombe"), ("fait", 5.82, 1, "tombe"), ("évoluer", 5.94, 1.35, "evolue")],
      [("son", 6.42, 1, "tombe"), ("comportement", 6.64, 1.05, "danse")], [("et", 7.40, 1, "tombe"), ("ses", 7.60, 1, "tombe"), ("idées.", 7.78, 1.3, "lourd")]], 8.10),
    ([[("Il", 8.68, .85, "tombe"), ("s'est", 8.76, .85, "tombe"), ("rendu", 8.92, .85, "tombe")], [("plus", 9.26, .85, "tombe"), ("productif,", 9.44, 1.1, "machine")],
      [("plus", 10.54, .85, "tombe"), ("fort,", 10.74, 1.45, "fort")], [("plus", 11.62, .85, "tombe"), ("rapide.", 11.72, 1.15, "rapide")]], 12.20),
    ([[("Encore", 12.82, 1, "hesite"), ("faut-il", 13.20, 1, "hesite")], [("qu'il", 13.68, 1, "tombe"), ("réfléchisse,", 13.94, 1.3, "gratte")]], 14.75),
    ([[("et", 15.24, 1, "tombe"), ("qu'il", 15.32, 1, "tombe"), ("soit", 15.48, 1, "tombe"), ("prêt.", 15.72, 1.55, "pret")]], 16.65),
    ([[("Et", 17.16, 1.8, "lourd"), ("si", 17.34, 1.8, "lourd")]], 18.20),
]
E, MOTS = [], {}
for n_e, (lignes, sortie) in enumerate(ECRANS):
    hs = [max(int(BASE * w[2]) for w in l) * 1.22 for l in lignes]
    y = -sum(hs) / 2; kg = 0
    for ligne, h in zip(lignes, hs):
        y += h; base_y = y - h * 0.22
        f_esp = [ImageFont.truetype(POLICE, int(BASE * w[2]), index=1) for w in ligne]
        largeurs = [f.getlength(w[0]) for f, w in zip(f_esp, ligne)]
        esp = BASE * 0.32
        x = -(sum(largeurs) + esp * (len(ligne) - 1)) / 2
        for (mot, t0, kk, comp), f, lw in zip(ligne, f_esp, largeurs):
            taille = int(BASE * kk); MOTS[(n_e, mot)] = (x, base_y, lw, taille)
            n = len(mot)
            for k, c in enumerate(mot):
                if c == " ": continue
                cx = x + f.getlength(mot[:k]) + f.getlength(c) / 2
                fn = dict(tombe=lambda: tombe(t0, k), traverse=lambda: traverse(t0, k, n), lourd=lambda: lourd(t0, k),
                          debout=lambda: debout(t0, k), enfle=lambda: enfle(t0, k, n), evolue=lambda: evolue(t0, k, n),
                          danse=lambda: danse(t0, k), machine=lambda: machine(t0, k), fort=lambda: fort(t0, k),
                          rapide=lambda: rapide(t0, k, n), hesite=lambda: hesite(t0, k), gratte=lambda: gratte(t0, k),
                          pret=lambda: pret(t0, k))[comp]()
                E.append(Lettre(c, taille, cx, base_y, t0 - 1.0, fn, sortie + 0.005 * kg, k=kg, ecran=n_e)); kg += 1
            x += lw + esp

def M(e, m): return MOTS[(e, m)]
# ---------- graphismes doodle, au service des mots ----------
x, y, w, t = M(0, "âges")
for d in (-1, 1): E.append(El([[(0, 0), (d * 40, -14)], [(d * 12, 6), (d * 52, 4)]], x + w / 2 + d * (w / 2 + 6), y, epais=0, t_in=0.8, draw=0.08, hide=1.3))
x, y, w, t = M(0, "époques"); E.append(El(souligne(w + 20), x + w / 2, y + 24, epais=0, t_in=1.75, draw=0.3, out=2.08))
x, y, w, t = M(1, "ingéniosité,")
f = ImageFont.truetype(POLICE, t, index=1)
for j, c in enumerate("ingéniosité,"):
    if c == "i":
        cx = x + f.getlength("ingéniosité,"[:j]) + f.getlength("i") / 2
        E.append(El(ampoule(), cx, y - t * 0.95, epais=1, t_in=4.3 + 0.12 * j / 3, pop=True, scale=0.42, out=5.16))
        E.append(El(rayons(), cx, y - t * 0.95, epais=0, t_in=4.45 + 0.12 * j / 3, pop=True, scale=0.42, out=5.18))
x, y, w, t = M(2, "idées."); E.append(El(bulle(), x + w + 150, y - t * 0.9, epais=1, t_in=7.95, pop=True, draw=0.25, scale=0.55, out=8.12))
E.append(El(gribouillis(4, rx=80, ry=40), x + w + 150, y - t * 0.9, epais=0, t_in=8.05, draw=0.3, width=5, out=8.12))
x, y, w, t = M(3, "productif,"); E.append(El(engrenage(40), x + w + 70, y - t * 0.38, epais=1, t_in=9.4, pop=True, spin=160, out=12.22))
E.append(El(engrenage(26, 7), x + w + 122, y - t * 0.78, epais=1, t_in=9.5, pop=True, spin=-240, out=12.24))
x, y, w, t = M(3, "fort,"); E.append(El(rayons(w * 0.62, w * 0.62 + 40, 7, -170, -10), x + w / 2, y - t * 0.3, epais=0, t_in=10.76, pop=True, out=11.3))
x, y, w, t = M(3, "rapide."); E.append(El([[(-260 + 40 * i, -t * 0.14 * i), (-40, -t * 0.14 * i)] for i in range(3)], x - 20, y - t * 0.22,
                                          epais=0, t_in=11.64, draw=0.06, hide=11.86))
x, y, w, t = M(4, "réfléchisse,"); E.append(El(interrogation(), x + w + 60, y - t * 0.1, t_in=14.25, pop=True, scale=1.25, dots=[(0, 14, 7)],
                                               rot_fn=lambda tt: 14 * math.sin(7 * tt), out=14.78))
x, y, w, t = M(5, "prêt."); cxh, cyh = x + w + 100, y - t * 0.4
def aig(tt):
    T = 15.72
    if tt < T: return 1300 * (tt - 15.3)
    b = 1300 * (T - 15.3); return b + (360 - b % 360) + 16 * math.exp(-12 * (tt - T)) * math.sin(40 * (tt - T))
E.append(El(horloge(60), cxh, cyh, epais=1, t_in=15.3, pop=True, out=16.66, width=5))
E.append(El(aiguille(46), cxh, cyh, epais=0, t_in=15.3, pop=True, rot_fn=aig, out=16.68, width=5))
x, y, w, t = M(6, "si")
for k in range(3):
    E.append(El([circle(0, 0, 4, 12)], x + w + 40 + 52 * k, y - 6, t_in=17.55 + 0.2 * k, drop=True, dots=[(0, 0, 13)], out=18.24 + 0.04 * k))

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "3_RESULTATS")
    if len(sys.argv) > 1:
        apercu(E, [0.02, 0.15, 1.0, 2.0, 2.6, 3.95, 4.8, 6.1, 7.2, 8.1, 10.0, 10.8, 11.9, 14.6, 15.6, 15.95, 17.9, 18.75], sys.argv[1], cols=6)
    else:
        rendre(E, DUREE, "intro_texte_v2_720p", out)
