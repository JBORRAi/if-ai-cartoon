"""Version B : typographie animée de la voix off, mot par mot (chaque mot atterrit pile quand il est dit),
même physique que le titre (chute + écrasement), avec des petits graphismes doodle animés.
    uv run --with pillow --with imageio-ffmpeg python IF/EP01/MOTION_INTRO/scripts/intro_texte.py [apercu]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from doodle import *

BASE = 128
# écrans : (lignes, sortie) ; ligne = [(mot, début_parole, taille_relative), ...]
ECRANS = [
    ([[("À", 0.05, 1), ("travers", 0.24, 1), ("les", 0.54, 1), ("âges", 0.78, 1.3)],
      [("et", 1.20, 1), ("les", 1.32, 1), ("époques", 1.48, 1.3)]], 2.30),
    ([[("L'homme,", 2.56, 1.35)], [("dans", 3.44, 1), ("son", 3.54, 1), ("immense", 3.76, 1.5)],
      [("ingéniosité,", 4.20, 1.2)]], 5.50),
    ([[("a", 5.70, 1), ("fait", 5.82, 1), ("évoluer", 5.94, 1.3)], [("son", 6.42, 1), ("comportement", 6.64, 1)],
      [("et", 7.40, 1), ("ses", 7.60, 1), ("idées.", 7.78, 1.3)]], 8.36),
    ([[("Il", 8.68, .9), ("s'est", 8.76, .9), ("rendu", 8.92, .9)], [("plus", 9.26, .9), ("productif,", 9.44, 1.15)],
      [("plus", 10.54, .9), ("fort,", 10.74, 1.3)], [("plus", 11.62, .9), ("rapide.", 11.72, 1.15)]], 12.45),
    ([[("Encore", 12.82, 1), ("faut-il", 13.20, 1)], [("qu'il", 13.68, 1), ("réfléchisse,", 13.94, 1.3)]], 15.05),
    ([[("et", 15.24, 1), ("qu'il", 15.32, 1), ("soit", 15.48, 1), ("prêt.", 15.72, 1.5)]], 16.80),
    ([[("Et", 17.16, 1.8), ("si", 17.34, 1.8)]], 18.30),
]
DUREE = 18.8
E, POS = [], {}

for n_ecran, (lignes, sortie) in enumerate(ECRANS):
    tailles = [[int(BASE * k) for _, _, k in l] for l in lignes]
    hauteurs = [max(t) * 1.18 for t in tailles]
    y = -sum(hauteurs) / 2
    k_mot = 0
    for ligne, ts, h in zip(lignes, tailles, hauteurs):
        y += h
        imgs = [mot(m, t) for (m, _, _), t in zip(ligne, ts)]
        esp = [t * 0.28 for t in ts]
        largeur = sum(w for _, w, _ in imgs) + sum(esp[:-1])
        x = -largeur / 2
        for (m, t0, k), (im, w, desc), e in zip(ligne, imgs, esp):
            cx, by = x + w / 2, y - h * 0.18 + desc
            POS[(n_ecran, m)] = (cx, y - h * 0.18, w, int(BASE * k))
            special = dict(drop=True, t_in=t0 - 0.2)
            if m == "immense": special = dict(pop=True, t_in=t0 - 0.05)
            if m == "rapide.": special = dict(t_in=t0 - 0.12, moves=[(t0 - 0.12, t0 + 0.06, cx, by)], x0=-1500)
            x0 = special.pop("x0", cx)
            E.append(El(img=im, x=x0, y=by, out=sortie + 0.035 * k_mot, chute_dir=(-1) ** k_mot, **special))
            x += w + e; k_mot += 1

def P(e, m): return POS[(e, m)]
# graphismes doodle
x, y, w, t = P(0, "époques"); E.append(El(souligne(w + 20), x, y + 22, t_in=1.75, draw=0.35, out=2.42, width=6))
x, y, w, t = P(1, "immense")
for k, (dx, dy) in enumerate([(-w / 2 - 40, -t * 0.7), (w / 2 + 40, -t * 0.8), (w / 2 + 20, -t * 0.1)]):
    E.append(El(etoile(), x + dx, y + dy, t_in=3.9 + 0.12 * k, pop=True, out=5.55))
x, y, w, t = P(1, "ingéniosité,"); E.append(El(ampoule(), x + w / 2 + 70, y - t * 0.55, t_in=4.6, pop=True, draw=0.3, scale=0.8, out=5.6))
E.append(El(rayons(), x + w / 2 + 70, y - t * 0.55, t_in=4.75, pop=True, scale=0.8, out=5.6))
x, y, w, t = P(2, "évoluer"); E.append(El([[(-w / 2, 0), (w / 2, 0), (w / 2 - 22, -14)], [(w / 2, 0), (w / 2 - 22, 14)]], x, y + 24, t_in=6.1, draw=0.3, out=8.4, width=6))
x, y, w, t = P(2, "idées."); E.append(El(ampoule(), x + w / 2 + 60, y - t * 0.6, t_in=7.95, pop=True, draw=0.3, scale=0.7, out=8.45))
x, y, w, t = P(3, "productif,"); E.append(El(engrenage(42), x + w / 2 + 70, y - t * 0.35, t_in=9.5, pop=True, spin=150, out=12.5))
E.append(El(engrenage(28, 7), x + w / 2 + 128, y - t * 0.75, t_in=9.6, pop=True, spin=-220, out=12.52))
x, y, w, t = P(3, "fort,"); E.append(El(rayons(w * 0.62, w * 0.62 + 34, 5, -160, -20), x, y - t * 0.3, t_in=10.9, pop=True, out=12.5, width=5))
xp, yp, wp, tp = P(3, "plus"); E.append(El([[(-230 + 30 * i, -tp * 0.18 * i), (-30, -tp * 0.18 * i)] for i in range(3)],
                                          xp - wp / 2, yp - tp * 0.12, t_in=11.62, draw=0.1, hide=12.2, width=5))
x, y, w, t = P(4, "réfléchisse,"); E.append(El(interrogation(), x + w / 2 + 70, y - t * 0.2, t_in=14.25, pop=True, scale=1.3,
                                               dots=[(0, 14, 7)], rot_fn=lambda tt: 14 * math.sin(7 * tt), out=15.1))
x, y, w, t = P(5, "prêt.")
def aig(tt): return 1440 * min(tt, 15.72) + (360 - (1440 * 15.72) % 360) * spring(tt - 15.72, 18, 7) if tt > 15.72 else 1440 * tt
cxh, cyh = x + w / 2 + 110, y - t * 0.35
E.append(El(horloge(60), cxh, cyh, t_in=15.3, pop=True, out=16.85, width=5))
E.append(El(aiguille(46), cxh, cyh, t_in=15.3, pop=True, rot_fn=aig, out=16.88, width=5))
E.append(El(rayons(80, 104, 10, 0, 324), cxh, cyh, t_in=15.72, pop=True, out=16.85, width=5))
x, y, w, t = P(6, "si")
for k in range(3):
    E.append(El([circle(0, 0, 3, 10)], x + w / 2 + 36 + 46 * k, y - 4, t_in=17.55 + 0.2 * k, drop=True, dots=[(0, 0, 12)], out=18.35 + 0.04 * k))

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "3_RESULTATS")
    if len(sys.argv) > 1:
        apercu(E, [0.9, 2.0, 4.0, 4.9, 7.0, 8.1, 9.8, 11.0, 11.9, 14.5, 15.9, 18.0], sys.argv[1])
    else:
        rendre(E, DUREE, "intro_texte_720p", out)
