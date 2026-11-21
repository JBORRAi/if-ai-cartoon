"""Version A : motion design doodle illustré, calé au mot près sur la voix off (EXPORTS/IF_EP01.mp3, t=0 = début).
    uv run --with pillow --with imageio-ffmpeg python IF/EP01/MOTION_INTRO/scripts/intro_doodle.py [apercu]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from doodle import *

# timecodes Whisper (mot -> début, s)
V = dict(travers=0.24, ages=0.78, et1=1.20, epoques=1.48, homme=2.56, immense=3.76, ingeniosite=4.20, evoluer=5.94,
         comportement=6.64, idees=7.78, ilsest=8.68, productif=9.44, fort=10.74, rapide=11.72, encore=12.82,
         reflechisse=13.94, prete=15.24, pret=15.72, etsi=17.16)
DUREE = 18.8
SOL = 300      # y des pieds du bonhomme
E = []

# 1. « À travers les âges et les époques » : une frise se dessine, les époques poussent dessus
E.append(El(frise(), 0, 150, t_in=0.02, draw=1.3, out=2.36, width=6))
for i, (forme, t) in enumerate([(grotte(), V["travers"]), (pyramide(), V["ages"]), (colonne(), V["et1"]),
                                (chateau(), V["epoques"]), (fusee(), V["epoques"] + 0.3)]):
    E.append(El(forme, -560 + 280 * i, 140, t_in=t, pop=True, draw=0.25, out=2.36 + 0.05 * i, chute_dir=(-1) ** i))

# 2. « L'homme, dans son immense ingéniosité » : le bonhomme se dessine, une ampoule s'allume
E.append(El(stick(), 0, SOL, t_in=V["homme"] - 0.05, draw=0.55, scale=1.6, hide=V["fort"] - 0.02,
            moves=[(5.75, 6.15, 260, SOL), (8.35, 8.75, 0, SOL)]))
E.append(El(ampoule(), 0, -110, t_in=V["immense"], pop=True, draw=0.35, scale=1.25, out=5.55))
E.append(El(rayons(), 0, -110, t_in=V["ingeniosite"], pop=True, scale=1.25, out=5.6))
for k, (dx, dy) in enumerate([(-150, -190), (160, -170), (120, -40)]):
    E.append(El(etoile(), dx, dy, t_in=V["ingeniosite"] + 0.15 * k, pop=True, out=5.6, scale=1.1))

# 3. « a fait évoluer son comportement et ses idées » : la marche de l'évolution, puis une bulle d'idée
E.append(El(stick("singe"), -360, SOL, t_in=V["evoluer"], pop=True, draw=0.3, scale=1.6, out=8.3, chute_dir=-1))
E.append(El(stick("mi"), -60, SOL, t_in=V["comportement"] - 0.1, pop=True, draw=0.3, scale=1.6, out=8.36, chute_dir=-1))
E.append(El(bulle(), 470, -150, t_in=V["idees"] - 0.25, pop=True, draw=0.4, scale=0.9, out=8.4))
E.append(El(gribouillis(11, rx=110, ry=60), 470, -150, t_in=V["idees"], draw=0.4, width=5, out=8.4))

# 4. « Il s'est rendu plus productif » : des engrenages se mettent à tourner
E.append(El(engrenage(80), -260, 0, t_in=V["productif"] - 0.2, pop=True, spin=110, out=10.45, chute_dir=-1))
E.append(El(engrenage(55, 7), -150, -110, t_in=V["productif"], pop=True, spin=-160, rot=12, out=10.5))
E.append(El(engrenage(65, 8), 250, -60, t_in=V["productif"] + 0.15, pop=True, spin=130, out=10.55))

# 5. « plus fort » : bras levés, haltères ; « plus rapide » : il file à droite
E.append(El(stick("bras_haut"), 0, SOL, t_in=V["fort"] - 0.02, scale=1.6, hide=V["rapide"] - 0.02))
E.append(El(halteres(), 0, SOL - 345, t_in=V["fort"], pop=True, scale=1.0, out=V["rapide"] - 0.1))
E.append(El(impact(), -165, SOL - 345, t_in=V["fort"] + 0.05, pop=True, scale=0.8, out=V["rapide"] - 0.1))
E.append(El(impact(), 165, SOL - 345, t_in=V["fort"] + 0.05, pop=True, scale=0.8, out=V["rapide"] - 0.1))
E.append(El(stick("course"), 0, SOL, t_in=V["rapide"] - 0.02, scale=1.6,
            moves=[(V["rapide"] + 0.15, V["rapide"] + 0.55, 1300, SOL)]))
E.append(El(vitesse(), -60, SOL - 160, t_in=V["rapide"] + 0.1, draw=0.12, scale=1.4, hide=V["rapide"] + 0.6,
            moves=[(V["rapide"] + 0.15, V["rapide"] + 0.55, 1150, SOL - 160)]))

# 6. « Encore faut-il qu'il réfléchisse » : une grosse tête, le cerveau gribouille, un « ? » rebondit
E.append(El([circle(0, 0, 210, 70), [(205, 20), (240, 50), (205, 70)]], 0, 40, t_in=V["encore"], draw=0.6, out=15.1))
E.append(El(gribouillis(5, n=90, rx=150, ry=110), 0, 20, t_in=V["reflechisse"], draw=0.6, width=5, out=15.15))
E.append(El(interrogation(), 290, -150, t_in=V["reflechisse"] + 0.35, pop=True, scale=1.6, dots=[(0, 14, 7)],
            rot_fn=lambda t: 12 * math.sin(7 * t), out=15.2))

# 7. « et qu'il soit prêt » : une horloge, l'aiguille tourne et s'arrête pile sur « prêt »
def aig(t):
    T = V["pret"]
    return 1080 * (t - V["prete"]) if t < T else 1080 * (T - V["prete"]) + (360 - (1080 * (T - V["prete"])) % 360) * spring(t - T, 18, 7)
E.append(El(horloge(), 0, 20, t_in=V["prete"] - 0.05, pop=True, out=16.9))
E.append(El(aiguille(115), 0, 20, t_in=V["prete"] - 0.05, pop=True, rot_fn=aig, out=16.95))
E.append(El(aiguille(70), 0, 20, t_in=V["prete"] - 0.05, pop=True, rot=120, out=16.95))
E.append(El(rayons(185, 230, 12, 0, 330), 0, 20, t_in=V["pret"], pop=True, out=16.9))

# 8. « Et si… » : trois points dessinés tombent et rebondissent, puis tout tombe
for k in range(3):
    E.append(El([circle(0, 0, 4, 12)], -60 + 60 * k, 20, t_in=V["etsi"] + 0.22 * k, drop=True, dots=[(0, 0, 14)], out=18.2 + 0.05 * k))

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "3_RESULTATS")
    if len(sys.argv) > 1:
        apercu(E, [0.5, 1.9, 3.3, 4.6, 6.4, 8.0, 9.8, 11.0, 11.9, 14.4, 15.9, 17.8], sys.argv[1])
    else:
        rendre(E, DUREE, "intro_doodle_720p", out)
