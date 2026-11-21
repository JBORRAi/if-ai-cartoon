"""Version A2 : doodle illustré, plus vivant, selon BIBLE_ANIMATION.md (Williams) :
anticipations, takes, accents durs/doux, arcs, chevauchements, poses tenues, contraste de tempo.
Lisibilité : une idée à la fois au centre du regard, lecture gauche -> droite, chaque groupe sort avant le suivant.
Écran vierge au début et à la fin. Calé au mot (Whisper) sur EXPORTS/IF_EP01.mp3.
    uv run --with pillow --with imageio-ffmpeg python IF/EP01/MOTION_INTRO/scripts/intro_doodle_v2.py [apercu]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from doodle import *

V = dict(travers=0.24, ages=0.78, et1=1.20, epoques=1.48, homme=2.56, dans=3.44, immense=3.76, ingeniosite=4.20,
         a=5.70, evoluer=5.94, comportement=6.64, idees=7.78, ilsest=8.68, productif=9.44, fort=10.74, rapide=11.72,
         encore=12.82, reflechisse=13.94, prete=15.24, pret=15.72, etsi=17.16)
DUREE = 18.8
S = 2.5           # échelle du bonhomme
SOL = 330         # pieds

# ---------- bonhomme articulé (poses clés interpolées) ----------
def R(v, a):
    a = math.radians(a); return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))
def corps(p):
    c, l, h = p["c"], p["l"], p["h"]
    hip = (0.0, -60 + 28 * c)
    def add(a, b): return (a[0] + b[0], a[1] + b[1])
    neck = add(hip, R((0, -62), l)); head = add(neck, R((0, -30), l + h)); sh = add(hip, R((0, -50), l))
    st = [[hip, neck]]
    bl = p.get("bl", 34)
    for sgn, (a1, a2) in ((-1, p["aL"]), (1, p["aR"])):
        v1 = (sgn * math.sin(math.radians(a1)), math.cos(math.radians(a1)))
        v2 = (sgn * math.sin(math.radians(a1 + a2)), math.cos(math.radians(a1 + a2)))
        epaule = add(sh, (sgn * 14, 0))                      # largeur d'épaules : les bras ne partent pas du cou
        el = add(epaule, (bl * v1[0], bl * v1[1])); ha = add(el, (bl * v2[0], bl * v2[1]))
        st.append([sh, epaule, el, ha])
    for sgn, f in ((-1, p.get("fL")), (1, p.get("fR"))):
        foot = f or (sgn * 32 * p["sp"], 0.0)
        kd = p.get("kd")
        kxo = kd * (8 + 22 * max(c, 0)) if kd else sgn * 16 * max(c, 0)
        knee = ((hip[0] + foot[0]) / 2 + kxo, (hip[1] + foot[1]) / 2)
        st.append([hip, knee, foot])
    tete = [circle(head[0], head[1], 28, 40)]
    if p.get("bras_devant", 0) > 0.5: return tete + st   # bras levés : ils passent DEVANT la tête
    return st + tete                                     # sinon tête en dernier : son fond masque ce qui passe derrière

BASE = dict(c=0, l=0, h=0, aL=(22, 0), aR=(22, 0), sp=1, bras_devant=0, bl=34)
def P(**kw): d = dict(BASE); d.update(kw); return d
NEUTRE = P()
PENSE = P(h=-14, aR=(150, 95), aL=(25, 0))
ANTIC = P(c=0.7, h=10, aL=(30, 10), aR=(30, 10), sp=1.25)
TAKE = P(c=-0.2, h=-12, aL=(160, 10), aR=(160, 10), sp=0.9)
FIER = P(c=0, h=-8, aL=(65, -105), aR=(65, -105), sp=1.15)
GRATTE = P(h=8, aR=(165, 115), aL=(20, 0))
BOSSE1 = P(c=0.15, aL=(95, -70), aR=(35, 70))
BOSSE2 = P(c=0.15, aL=(35, 70), aR=(95, -70))
SQUAT = P(c=0.85, h=6, aL=(22, 0), aR=(22, 0), sp=1.4, bl=46)
HALT = P(c=-0.25, aL=(150, 0), aR=(150, 0), sp=1.3, bl=47)
RECUL = P(c=0.35, l=-16, h=-6, aL=(40, 70), aR=(-20, 40), fL=(-44, 0), fR=(30, 0))
COURSE = P(c=0.2, l=24, aL=(-40, 70), aR=(70, 60), fL=(-62, -22), fR=(36, 0))

def anim_poses(cles):
    """cles = [(t_debut, t_fin, pose, 'doux'|'back'), ...] ; la pose précédente glisse vers la nouvelle."""
    def f(t):
        cur = cles[0][2]
        for t0, t1, pose, mode in cles:
            if t < t0: break
            u = (t - t0) / max(t1 - t0, 1e-3)
            k = ease_back(u, 0.9) if mode == "back" else smooth(u)
            nxt = {}
            for key in set(cur) | set(pose):
                a, b = cur.get(key, BASE.get(key)), pose.get(key, BASE.get(key))
                if a is None: a = b
                if b is None: b = a
                if isinstance(a, tuple): nxt[key] = tuple(x + (y - x) * k for x, y in zip(a, b))
                else: nxt[key] = a + (b - a) * k
            cur = nxt
        return cur                       # pose (dict) ; Marcheur ajoute la marche puis dessine
    return f

import numpy as np
class Marcheur(El):
    """personnage qui MARCHE (Williams, p. 102-175) : pieds plantés au sol (aucun glissement), corps bas au contact
    et haut au passage, bras en opposition des jambes, buste penché dans le sens de la marche. base(t) = pose de jeu."""
    def __init__(s, base, Ls=70, courses=(), lean_dir=False, **kw):
        super().__init__(strokes=corps(base(0)), **kw)
        s.base, s.Ls, s.courses, s.lean_dir = base, Ls, courses, lean_dir
        ts = np.arange(0, DUREE + 0.5, 1 / 240)
        xs = np.array([El.pos(s, t)[0] for t in ts])
        dx = np.diff(xs, prepend=xs[0])
        s.ts, s.trav, s.vit = ts, np.cumsum(np.abs(dx)), dx * 240
        s.pose_fn = s.f
    def f(s, t):
        i = min(int(t * 240), len(s.ts) - 1)
        course = any(a <= t < b for a, b in s.courses)
        Ls = s.Ls * (1.5 if course else 1)
        v = s.vit[i] / S
        j = i
        while j > 0 and abs(s.vit[j]) < 1e-3: j -= 1
        dirn = 1 if s.vit[j] >= 0 else -1
        w = clamp01(abs(v) / (Ls * 1.6))
        phi = s.trav[i] / S / (2 * Ls)
        p = dict(s.base(t))
        if s.lean_dir: p["l"] = p["l"] * dirn
        pieds = []
        for sgn, ph in ((-1, phi % 1), (1, (phi + 0.5) % 1)):
            if ph < 0.5: o, lift = Ls / 2 - Ls * ph / 0.5, 0.0
            else:
                q = (ph - 0.5) / 0.5; o, lift = -Ls / 2 + Ls * smooth(q), (34 if course else 16) * math.sin(math.pi * q)
            repos = p.get("fL" if sgn < 0 else "fR") or (sgn * 32 * p["sp"], 0.0)
            pieds.append((repos[0] + (dirn * o - repos[0]) * w, repos[1] + (-lift - repos[1]) * w))
        p["fL"], p["fR"] = pieds
        p["kd"] = dirn if w > 0.05 else None
        p["c"] += w * ((0.22 if course else 0.12) + 0.12 * math.cos(4 * math.pi * phi))
        p["l"] += dirn * w * (24 if course else 7)
        sw = (42 if course else 28) * w * math.cos(2 * math.pi * phi)
        aL, aR = p["aL"], p["aR"]
        p["aL"] = (aL[0] + dirn * sw, aL[1] + (60 * w if course else 0))
        p["aR"] = (aR[0] + dirn * sw, aR[1] + (60 * w if course else 0))
        return corps(p)

E = []
# ================= 1. « À travers les âges et les époques » (lecture gauche -> droite) =================
E.append(El(frise(-620, 620), 0, 140, epais=1, t_in=0.05, draw=0.95, out=2.14, width=6))
for i, (forme, t) in enumerate([(grotte(), 0.20), (pyramide(), V["ages"]), (colonne(), V["et1"]),
                                (chateau(), V["epoques"]), (fusee(), V["epoques"] + 0.28)]):
    E.append(El(forme, -480 + 240 * i, 136, epais=1, t_in=t, pop=True, draw=0.22, scale=1.25, respire=0.015,
                out=2.00 + 0.03 * i, chute_dir=(-1) ** i))

# ================= 2. « L'homme, dans son immense ingéniosité » : un take sur « immense » =================
bon = anim_poses([
    (0.0, 0.0, NEUTRE, "doux"),
    (3.30, 3.62, PENSE, "doux"),                       # il réfléchit (temps de pensée avant l'action)
    (3.62, 3.74, ANTIC, "doux"),                       # anticipation vers le bas
    (3.74, 3.86, TAKE, "doux"),                        # accent : il jaillit vers le haut (2-3 images)
    (4.05, 4.45, FIER, "back"),                        # se pose, fier, sur « ingéniosité »
    (5.50, 5.70, NEUTRE, "doux"),
    (7.40, 7.70, GRATTE, "doux"),                      # se gratte la tête avant « idées »
    (8.10, 8.30, NEUTRE, "doux"),
    (9.30, 9.44, BOSSE1, "doux"), (9.55, 9.70, BOSSE2, "doux"), (9.80, 9.95, BOSSE1, "doux"),
    (10.05, 10.20, BOSSE2, "doux"), (10.30, 10.45, NEUTRE, "doux"),
    (10.52, 10.72, SQUAT, "doux"),                     # anticipation lourde du poids
    (10.72, 10.80, HALT, "doux"),                      # accent dur : il soulève
    (11.50, 11.70, RECUL, "doux"),                     # recule avant de foncer
    (11.70, 11.78, COURSE, "doux"),
])
E.append(Marcheur(bon, x=0, y=SOL, t_in=V["homme"] - 0.06, draw=0.45, scale=S,
            moves=[(5.40, 6.30, 360, SOL), (8.20, 9.10, 0, SOL), (V["rapide"] + 0.04, V["rapide"] + 0.62, 1500, SOL)],
            courses=[(V["rapide"], 12.6)]))
TETE = SOL - 200 * S
E.append(El(ampoule(), 0, TETE - 120, epais=1, t_in=V["immense"], pop=True, draw=0.2, scale=1.45, respire=0.03, out=5.02))
E.append(El(rayons(), 0, TETE - 120, epais=0, t_in=V["ingeniosite"], pop=True, scale=1.45, spin=12, out=5.05))
for k, (dx, dy) in enumerate([(-230, -60), (230, -110), (190, 90)]):
    E.append(El(etoile(), dx,  TETE - 120 + dy, epais=0, t_in=V["ingeniosite"] + 0.1 + 0.08 * k, pop=True, scale=1.2,
                rot_fn=lambda t, k=k: 20 * math.sin(5 * t + k), out=5.08 + 0.03 * k))

# ================= 3. « a fait évoluer son comportement et ses idées » (gauche -> droite) =================
SINGE = P(c=0.38, l=36, h=26, aL=(6, 18), aR=(6, 18), sp=0.9)
DEBOUT_MI = P(c=0.14, l=14, h=8)
def evo(t):                     # il se redresse en marchant : singe -> à moitié debout (sur « comportement »)
    k = smooth((t - 6.30) / 0.70); d = {}
    for key in SINGE:
        a, b = SINGE[key], DEBOUT_MI[key]
        d[key] = tuple(x + (y - x) * k for x, y in zip(a, b)) if isinstance(a, tuple) else a + (b - a) * k
    return d
SINGE_R = dict(evo(0)); MI_R = dict(evo(99))
E.append(Marcheur(lambda t: SINGE_R, Ls=55, lean_dir=True, x=-1150, y=SOL, t_in=5.40, scale=S,      # le singe
                  moves=[(5.45, 6.35, -430, SOL), (8.05, 8.95, -1250, SOL)]))
E.append(Marcheur(lambda t: MI_R, Ls=62, lean_dir=True, x=-1150, y=SOL, t_in=5.95, scale=S,         # l'homme à moitié redressé
                  moves=[(6.00, 6.95, -40, SOL), (8.10, 8.95, -1250, SOL)]))
E.append(El(bulle(), 360, TETE - 150, epais=1, t_in=V["idees"] - 0.12, pop=True, draw=0.3, scale=0.75, respire=0.02, out=7.92))
E.append(El(gribouillis(11, rx=100, ry=56), 360, TETE - 150, epais=0, t_in=V["idees"] + 0.05, draw=0.35, width=5, out=7.92))

# ================= 4. « plus productif, plus fort, plus rapide » =================
E.append(El(engrenage(85), -360, -60, epais=1, t_in=V["productif"] - 0.12, pop=True, spin=120, out=10.05, chute_dir=-1))
E.append(El(engrenage(60, 7), -230, -230, epais=1, t_in=V["productif"] - 0.02, pop=True, spin=-170, rot=12, out=10.09))
E.append(El(engrenage(70, 8), 360, -140, epais=1, t_in=V["productif"] + 0.08, pop=True, spin=140, out=10.13))
HY = SOL - 204 * S
E.append(El(halteres(), 0, HY, t_in=V["fort"] - 0.22, scale=1.25, moves=[(10.52, 10.72, 0, SOL - 30), (10.72, 10.80, 0, HY)],
            out=11.45))
E[-1].y = SOL - 30
E.append(El(impact(), -200, HY, epais=0, t_in=V["fort"] + 0.04, pop=True, scale=0.85, out=11.40))
E.append(El(impact(), 200, HY, epais=0, t_in=V["fort"] + 0.04, pop=True, scale=0.85, out=11.40))
E.append(El(vitesse(), -70, SOL - 180, epais=0, t_in=V["rapide"] + 0.08, draw=0.1, scale=1.5,
            moves=[(V["rapide"] + 0.1, V["rapide"] + 0.45, 1380, SOL - 180)], hide=V["rapide"] + 0.5))

# ================= 5. « Encore faut-il qu'il réfléchisse » : une grosse tête, les yeux roulent =================
T5, F5 = V["encore"], 14.98
E.append(El([circle(0, 0, 210, 70), [(206, 10), (240, 40), (206, 66)]], 0, 40, epais=2, t_in=T5, draw=0.5, respire=0.01, out=F5))
def yeux(t):
    u = smooth((t - V["reflechisse"]) / 0.18) - smooth((t - 14.7) / 0.15)
    dx, dy = 14 * u, -16 * u
    cl = 13.55 <= t < 13.62                             # clignement
    if cl: return [[(-80, -20), (-30, -20)], [(30, -20), (80, -20)], [(-50, 90), (50, 90)]]
    return [circle(-55, -20, 26, 24), circle(55, -20, 26, 24), [(-50, 90), (50, 90)]]
def pupilles(t):
    u = smooth((t - V["reflechisse"]) / 0.18) - smooth((t - 14.7) / 0.15)
    return [circle(-55 + 12 * u, -20 - 12 * u, 3, 8), circle(55 + 12 * u, -20 - 12 * u, 3, 8)]
E.append(El(pose_fn=yeux, strokes=yeux(13.3), x=0, y=40, epais=0, t_in=13.3, draw=0.25, out=F5 + 0.02))
E.append(El(pose_fn=pupilles, strokes=pupilles(13.3), x=0, y=40, t_in=13.42, dots=[], width=14, out=F5 + 0.02))
E.append(El(gribouillis(9, n=60, rx=110, ry=50), 120, -300, epais=0, t_in=V["reflechisse"] + 0.15, draw=0.45, width=5, out=F5 + 0.04))
E.append(El(interrogation(), 330, -230, t_in=14.30, pop=True, scale=1.7, dots=[(0, 14, 7)],
            rot_fn=lambda t: 14 * math.sin(7 * t), out=F5 + 0.06))

# ================= 6. « et qu'il soit prêt » : l'aiguille file puis claque sur « prêt » (accent dur) =================
F6 = 16.70
def aig(t):
    T = V["pret"]
    if t < T: return 1300 * (t - V["prete"])
    base = 1300 * (T - V["prete"]); cible = base + (360 - base % 360)
    return cible + 18 * math.exp(-12 * (t - T)) * math.sin(40 * (t - T))      # rebond de l'accent dur
E.append(El(horloge(), 0, 20, epais=1, t_in=V["prete"] - 0.06, pop=True, respire=0.01, out=F6))
E.append(El(aiguille(115), 0, 20, t_in=V["prete"] - 0.06, pop=True, rot_fn=aig, out=F6 + 0.02))
E.append(El(aiguille(70), 0, 20, epais=0, t_in=V["prete"] - 0.06, pop=True, rot=120, out=F6 + 0.02))
E.append(El(rayons(185, 232, 12, 0, 330), 0, 20, epais=0, t_in=V["pret"] + 0.02, pop=True, out=F6))

# ================= 7. « Et si… » : trois points tombent (accents durs), puis écran vierge =================
for k in range(3):
    E.append(El([circle(0, 0, 4, 12)], -70 + 70 * k, 20, t_in=V["etsi"] + 0.24 * k, drop=True, dots=[(0, 0, 15)],
                out=18.05 + 0.06 * k))

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "3_RESULTATS")
    if len(sys.argv) > 1:
        apercu(E, [0.02, 1.9, 3.5, 3.8, 4.6, 6.9, 8.0, 9.8, 10.8, 11.6, 13.0, 14.5, 16.0, 17.7, 18.75, 2.45], sys.argv[1])
    else:
        rendre(E, DUREE, "intro_doodle_v2_720p", out)
