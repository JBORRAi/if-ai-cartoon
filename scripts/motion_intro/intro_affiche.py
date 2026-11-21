"""Version D : « affiche mid-century » en papier découpé (formes pleines, palette chaude, mots-clés Futura,
volets de couleur entre les idées), calée au mot près sur EXPORTS/IF_EP01.mp3.
    uv run --with pillow --with imageio-ffmpeg python IF/EP01/MOTION_INTRO/scripts/intro_affiche.py [apercu]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import doodle
from doodle import *

ENCRE, TERRE, MOUT, CANARD, CREME = (28, 24, 20, 255), (206, 92, 56, 255), (226, 168, 58, 255), (47, 120, 116, 255), (248, 241, 226, 255)
FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"
DUREE = 18.8

def secousse(t):
    u = t - 10.74
    if 0 <= u < 0.35: a = 26 * math.exp(-10 * u); return a * math.sin(70 * u), a * math.cos(53 * u)
    return 0.0, 0.0
_etat = El.etat
def etat_secoue(s, t):
    e = _etat(s, t)
    if e is None: return None
    dx, dy = secousse(t); x, y, sc, sx, rot = e
    return x + dx, y + dy, sc, sx, rot
El.etat = etat_secoue

class Forme(El):
    """formes pleines, nettes (pas de frémissement)."""
    def __init__(s, polys, couleur=ENCRE, **kw):
        kw.setdefault("boil", 0); super().__init__(strokes=polys, **kw); s.couleur = couleur
    def rendu(s, img, drw, t):
        e = s.etat(t)
        if e is None or e[2] < 0.01: return
        x, y, sc, sx, rot = e
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for p in s.strokes:
            q = [(CX + x + px * sc * sx * ca - py * sc * sa, CY + y + px * sc * sx * sa + py * sc * ca) for px, py in p]
            drw.polygon(q, fill=s.couleur)

def mot_f(texte, taille, couleur=ENCRE, style=2):
    f = ImageFont.truetype(FUTURA, taille, index=style)
    l, t, r, b = f.getbbox(texte)
    im = Image.new("RGBA", (r - l + 30, b + 30), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((15 - l, 15), texte, font=f, fill=couleur)
    return im

def Mot(texte, taille, x, y, t_in, couleur=ENCRE, style=2, **kw):
    kw.setdefault("drop", True)
    return El(img=mot_f(texte, taille, couleur, style), x=x, y=y, t_in=t_in - (0.2 if kw.get("drop") else 0), **kw)

VOLETS = []
def volet(t0, couleur):   # un aplat traverse l'écran ; l'écran est couvert à t0 + 0.17 (dessiné par-dessus tout)
    return Forme([rect(-W / 2, -H / 2, W / 2, H / 2)], couleur, x=-W - 200, y=0, t_in=t0, moves=[(t0, t0 + 0.34, W + 200, 0)])

def tri(cx, cy, r, a):    # rayon en triangle
    a = math.radians(a)
    return [(cx + r * math.cos(a - 0.12), cy + r * math.sin(a - 0.12)), (cx + r * 1.5 * math.cos(a), cy + r * 1.5 * math.sin(a)),
            (cx + r * math.cos(a + 0.12), cy + r * math.sin(a + 0.12))]

E = []
# --- 1. « À travers les âges et les époques » : un paysage découpé, les époques poussent ---
F1 = 2.31
E.append(Forme([rect(-W / 2, 0, W / 2, 300)], CANARD, x=0, y=250 + 300, t_in=0.0, moves=[(0.0, 0.35, 0, 250)], hide=F1))
E.append(Forme([circle(0, 0, 150, 60)], MOUT, x=470, y=-170, t_in=0.24, pop=True, hide=F1))
for k, (poly, coul, xx, t) in enumerate([
        ([[(-130, 0), (0, -230), (130, 0)]], TERRE, -470, 0.78),
        ([rect(-45, -260, 45, 0), rect(-75, -290, 75, -255)], ENCRE, -170, 1.32),
        ([[(-120, 0), (-120, -170), (-90, -170), (-90, -140), (-50, -140), (-50, -170), (-10, -170), (-10, -140), (30, -140), (30, -170),
           (70, -170), (70, -140), (120, -140), (120, 0)]], CREME, 140, 1.48),
        ([[(0, -300), (55, -200), (55, -40), (95, 0), (-95, 0), (-55, -40), (-55, -200)]], TERRE, 440, 1.75)]):
    E.append(Forme(poly, coul, x=xx, y=250, t_in=t, pop=True, hide=F1))
E.append(Mot("LES ÂGES", 130, 0, -300, 0.78, hide=1.47))
E.append(Mot("LES ÉPOQUES", 130, 0, -300, 1.48, hide=F1))
VOLETS.append(volet(2.14, ENCRE))

# --- 2. « L'homme, dans son immense ingéniosité » ---
F2 = 5.69
E.append(Forme([circle(0, -230, 70, 50), [(-110, -140), (110, -140), (80, 260), (-80, 260)]], ENCRE, x=-480, y=110, t_in=2.56, pop=True, hide=F2))
E.append(Mot("L'HOMME", 250, 300, 120, 2.56, style=4, hide=3.74))
E.append(Forme([circle(0, 0, 95, 60), rect(-40, 80, 40, 130)], MOUT, x=-480, y=-300, t_in=3.76, pop=True, hide=F2))
E.append(Mot("IMMENSE", 250, 300, 120, 3.76, style=4, couleur=TERRE, hide=4.18))
E.append(Forme([tri(0, 0, 120, a) for a in range(0, 360, 30) if not 60 < a < 120], TERRE, x=-480, y=-300, t_in=4.20, pop=True, spin=40, hide=F2))
E.append(Mot("INGÉNIOSITÉ", 175, 300, 100, 4.20, style=4, hide=F2))
VOLETS.append(volet(5.52, MOUT))

# --- 3. « a fait évoluer son comportement et ses idées » ---
F3 = 9.19
for k, (h, c) in enumerate([(160, CANARD), (300, TERRE), (450, ENCRE)]):
    E.append(Forme([rect(-70, -h, 70, 0)], c, x=-560 + 190 * k, y=320, t_in=5.94 + 0.16 * k, pop=True, hide=F3))
E.append(Mot("ÉVOLUER", 200, 380, 60, 5.94, style=4, hide=7.76))
for k, (dx, dy, r, c) in enumerate([(-200, -330, 40, MOUT), (-100, -420, 26, TERRE), (20, -360, 34, CANARD), (-300, -250, 22, TERRE), (80, -460, 20, MOUT)]):
    E.append(Forme([circle(0, 0, r, 30)], c, x=-180 + dx + 60, y=dy + 120, t_in=7.78 + 0.06 * k, pop=True, hide=F3))
E.append(Mot("IDÉES", 230, 380, 60, 7.78, style=4, couleur=TERRE, hide=F3))
VOLETS.append(volet(9.02, CANARD))

# --- 4. « plus productif, plus fort, plus rapide » ---
F4 = 12.57
E.append(Forme([engrenage(210, 11)[0]], TERRE, x=-430, y=40, t_in=9.44, pop=True, spin=90, hide=10.72))
E.append(Forme([circle(0, 0, 60, 40)], (238, 228, 208, 255), x=-430, y=40, t_in=9.44, pop=True, hide=10.72))
E.append(Forme([engrenage(120, 8)[0]], MOUT, x=-160, y=-190, t_in=9.56, pop=True, spin=-165, rot=10, hide=10.72))
E.append(Mot("PRODUCTIF", 190, 360, 80, 9.44, style=4, hide=10.72))
E.append(Forme([rect(-760, -300, 760, 300)], TERRE, x=0, y=0, t_in=10.74, pop=True, hide=11.70))
E.append(Mot("FORT", 380, 0, 250, 10.74, style=4, couleur=CREME, hide=11.70))
for k, c in enumerate((MOUT, TERRE, CANARD)):
    E.append(Forme([rect(-900, -40, 0, 40)], c, x=-1800, y=-140 + 140 * k, t_in=11.62, moves=[(11.62 + 0.05 * k, 11.95 + 0.05 * k, 2400, -140 + 140 * k)], hide=F4))
E.append(Mot("RAPIDE", 300, -1500, 160, 11.72, style=4, drop=False, moves=[(11.72, 11.9, 0, 160)], hide=F4))
VOLETS.append(volet(12.40, TERRE))

# --- 5. « Encore faut-il qu'il réfléchisse » ---
F5 = 15.17
E.append(Forme([circle(0, 0, 270, 70)], CANARD, x=-300, y=20, t_in=12.82, pop=True, hide=F5))
E.append(Mot("ENCORE FAUT-IL...", 110, 380, -40, 12.82, hide=13.92))
E.append(El(img=mot_f("?", 420, MOUT), x=-300, y=230, t_in=13.94, pop=True, rot_fn=lambda t: 10 * math.sin(6 * t), hide=F5))
E.append(Mot("RÉFLÉCHIR", 170, 400, 70, 13.94, style=4, hide=F5))
VOLETS.append(volet(15.00, ENCRE))

# --- 6. « et qu'il soit prêt » ---
F6 = 16.91
def aig(t):
    T = 15.72
    return 1440 * (t - 15.24) if t < T else 1440 * (T - 15.24) + (360 - (1440 * (T - 15.24)) % 360) * spring(t - T, 18, 7)
E.append(Forme([circle(0, 0, 250, 70)], ENCRE, x=-330, y=20, t_in=15.24, pop=True, hide=F6))
E.append(Forme([circle(0, 0, 225, 70)], CREME, x=-330, y=20, t_in=15.24, pop=True, hide=F6))
E.append(Forme([rect(-9, -180, 9, 14)], ENCRE, x=-330, y=20, t_in=15.24, pop=True, rot_fn=aig, hide=F6))
E.append(Forme([rect(-11, -110, 11, 14)], ENCRE, x=-330, y=20, t_in=15.24, pop=True, rot=0, hide=F6))
E.append(Forme([tri(0, 0, 270, a) for a in range(0, 360, 30)], MOUT, x=-330, y=20, t_in=15.72, pop=True, hide=F6))
E.append(Mot("PRÊT.", 330, 380, 160, 15.72, style=4, couleur=TERRE, hide=F6))
VOLETS.append(volet(16.74, MOUT))

# --- 7. « Et si… » ---
E.append(Mot("ET SI", 330, -60, 170, 17.16, style=4, out=18.25))
for k in range(3):
    E.append(Forme([circle(0, 0, 26, 30)], ENCRE, x=270 + 75 * k, y=118, t_in=17.45 + 0.2 * k, drop=True, out=18.3 + 0.05 * k))

E += VOLETS

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "3_RESULTATS")
    if len(sys.argv) > 1:
        apercu(E, [1.9, 2.45, 3.2, 4.6, 6.5, 8.1, 9.9, 10.8, 12.0, 14.4, 16.0, 17.9], sys.argv[1])
    else:
        rendre(E, DUREE, "intro_affiche_720p", out)
