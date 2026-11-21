"""Version C : « une seule ligne ». Un unique trait d'encre qui ne se coupe jamais et se métamorphose
au rythme de la voix (morphing avec dépassement élastique), du premier mot jusqu'aux trois points d'« Et si… ».
    uv run --with pillow --with imageio-ffmpeg python IF/EP01/MOTION_INTRO/scripts/intro_ligne.py [apercu]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from doodle import *

N = 500          # points par forme
DUREE = 18.8

def joindre(strokes): return [p for s in strokes for p in s]
def place(strokes, dx=0, dy=0, k=1.0): return [[(dx + x * k, dy + y * k) for x, y in s] for s in strokes]
def reech(p, n=N):
    L = [0.0]
    for i in range(len(p) - 1): L.append(L[-1] + math.dist(p[i], p[i + 1]))
    tot, out, j = L[-1] or 1, [], 0
    for i in range(n):
        d = tot * i / (n - 1)
        while j < len(L) - 2 and L[j + 1] < d: j += 1
        seg = (L[j + 1] - L[j]) or 1; u = (d - L[j]) / seg
        out.append((p[j][0] + (p[j + 1][0] - p[j][0]) * u, p[j][1] + (p[j + 1][1] - p[j][1]) * u))
    return out
def forme(strokes, dx=0, dy=0, k=1.0): return reech(joindre(place(strokes, dx, dy, k)))

SOL = 300
def bonhomme(pose="debout", dx=0, k=1.7):
    s = stick(pose)                       # ordre : jambe G, corps, tête, bras, jambe D -> un seul trait
    legs, body, head, arms = [s[2][::-1]], [s[1][::-1]], [s[0]], s[4:6]
    return forme([legs[0], body[0], head[0], [body[0][-1]], arms[0][::-1], arms[0], arms[1], arms[1][::-1], body[0], s[3]], dx, SOL, k)

ligne_plate = forme([[(-700, 0), (700, 0)]], 0, 150)
vague = forme([[(x, 25 * math.sin(x / 60)) for x in range(-700, 701, 10)]], 0, 150)
def horizon(sil): return forme([[(-700, 0)] + sil + [(700, 0)]], 0, 150)
pyr = horizon([(-120, 0), (0, -200), (120, 0)])
col = horizon([(-160, 0), (-50, 0), (-50, -220), (-80, -220), (-80, -240), (80, -240), (80, -220), (50, -220), (50, 0), (160, 0)])
cha = horizon([(-220, 0)] + [p for i, x in enumerate(range(-220, 221, 44)) for p in ((x, -170 if i % 2 == 0 else -140), (x + 44, -170 if i % 2 == 0 else -140))][:-1] + [(220, 0)])
fus = horizon([(-60, 0), (-60, -180), (0, -300), (60, -180), (60, 0)])
point = forme([circle(0, 0, 6, 20)], 0, 150)
homme = bonhomme()
homme_ampoule = reech(joindre(place(stick(), 0, SOL, 1.7)) + joindre(place(ampoule(), 0, -110, 1.3)))
homme_idee = reech(joindre(place(stick(), 0, SOL, 1.7)) + joindre(place(ampoule() + rayons(), 0, -110, 1.3)))
singe = bonhomme("singe"); mi = bonhomme("mi")
idee = reech(joindre(place(stick(), -250, SOL, 1.7)) + joindre(place(bulle(), 250, -120, 1.1)))
gear = forme(engrenage(150, 10))
halt = reech(joindre(place(stick("bras_haut"), 0, SOL, 1.7)) + joindre(place(halteres(), 0, SOL - 370, 1.1)))
trait = forme([[(-900, 0), (900, 0)]], 0, 100)
tete = forme([circle(0, 0, 220, 80), [(215, 20), (250, 50), (215, 75)]], 0, 40)
spirale = forme([circle(0, 0, 220, 80)] + [[(r * math.cos(a) * 0.7, r * math.sin(a) * 0.5) for a, r in ((i * 0.35, 150 - i * 1.6) for i in range(90))]], 0, 40)
quest = forme(place(interrogation(), 0, 0, 3.2), 0, 120)
horl = forme(horloge(170) + [[(0, 0), (0, -120)], [(0, 0), (80, 30)]], 0, 20)
horl_pret = forme(horloge(170) + [[(0, 0), (0, -130)], [(0, 0), (0, -90)]], 0, 20)
mini = forme([circle(0, 0, 14, 30)], 0, 40)

# (instant du mot, forme)  — instants Whisper sur EXPORTS/IF_EP01.mp3
CLES = [(0.24, vague), (0.78, pyr), (1.32, col), (1.48, cha), (1.85, fus), (2.30, point),
        (2.56, homme), (3.76, homme_ampoule), (4.20, homme_idee), (5.94, singe), (6.64, mi), (7.40, homme),
        (7.78, idee), (9.44, gear), (10.74, halt), (11.72, trait), (12.82, tete), (13.94, spirale), (14.40, quest),
        (15.24, horl), (15.72, horl_pret), (16.70, mini)]
MORPH = 0.30

def back(x, s=1.9): x = clamp01(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

def forme_a(t):
    if t < CLES[0][0]: return ligne_plate
    for i in range(len(CLES) - 1, -1, -1):
        t0, f = CLES[i]
        if t >= t0:
            prec = CLES[i - 1][1] if i else ligne_plate
            k = back((t - t0) / MORPH)
            return [(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k) for a, b in zip(prec, f)]

class Ligne(El):
    def __init__(s): super().__init__(strokes=[[(0, 0), (1, 0)]], seed=42)
    def rendu(s, img, drw, t):
        if t >= 17.16: return
        p = forme_a(t)
        if 9.44 <= t < 10.74:                                   # l'engrenage tourne
            a = math.radians(150 * (t - 9.44)); c, sn = math.cos(a), math.sin(a)
            p = [(x * c - y * sn, x * sn + y * c) for x, y in p]
        if 11.72 <= t < 12.82:                                  # « rapide » : le trait file à droite puis revient
            u = t - 11.72; dx = 2400 * smooth(u / 0.45) if u < 0.6 else -2400 + 2400 * smooth((u - 0.6) / 0.25)
            p = [(x + dx, y) for x, y in p]
        if t < 0.6: p = p[:max(2, int(len(p) * smooth(t / 0.6)))]   # le trait se dessine au départ
        rnd = random.Random(int(t * 12) * 7 + 1)
        q = [(CX + x + rnd.uniform(-1.4, 1.4), CY + y + rnd.uniform(-1.4, 1.4)) for x, y in p]
        drw.line(q, fill=INK, width=8, joint="curve")
        for a in (q[0], q[-1]): drw.ellipse((a[0] - 4, a[1] - 4, a[0] + 4, a[1] + 4), fill=INK)

E = [Ligne()]
# « Et si… » : le petit rond se scinde en trois points qui sautent à leur place, puis tout tombe
for k, dx in enumerate((-70, 0, 70)):
    t0 = 17.16 + 0.18 * k
    E.append(El([circle(0, 0, 3, 10)], 0, 40, t_in=17.16, dots=[(0, 0, 14)], moves=[(t0, t0 + 0.22, dx, 40)],
                rot_fn=None, out=18.25 + 0.05 * k))
    E[-1].hop = (t0, dx)
_pos = El.pos
def pos_saut(s, t):
    x, y = _pos(s, t)
    if hasattr(s, "hop"):
        t0, dx = s.hop; u = (t - t0) / 0.22
        if 0 < u < 1: y -= 90 * 4 * u * (1 - u)
    return x, y
El.pos = pos_saut

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "3_RESULTATS")
    if len(sys.argv) > 1:
        apercu(E, [0.4, 1.0, 1.7, 2.9, 4.5, 6.2, 8.2, 9.9, 11.2, 14.2, 16.0, 17.7], sys.argv[1])
    else:
        rendre(E, DUREE, "intro_ligne_720p", out)
