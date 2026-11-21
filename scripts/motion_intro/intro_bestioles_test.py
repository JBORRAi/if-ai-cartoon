"""TEST 0 → 5.6 s : la bande de bestioles porte la narration (bouche du narrateur sur la voix)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from doodle import W, H, CX, CY, spring, smooth, clamp01
from bestioles import *

ICI = os.path.dirname(os.path.abspath(__file__))
MP3 = os.path.join(ICI, "../../MONTAGE/EXPORTS/IF_EP01.mp3")
FPS, DUREE = 60, 5.6
ENV = enveloppe(MP3, FPS, DUREE + 1)

narr = Bestiole(7, R=190, couleur=(140, 200, 205), yeux=2, bouche="dents", antenne=2)
A = Bestiole(21, R=75, couleur=(246, 168, 92), yeux=1, antenne=1)
B = Bestiole(5, R=85, couleur=(245, 160, 170), yeux=3, antenne=0)
C = Bestiole(33, R=110, couleur=(250, 210, 110), yeux=2, antenne=1, bouche="sourire")
foule = [Bestiole(100 + k, R=48) for k in range(5)]
P_AGES, P_EPO, P_HOM, P_ING = pancarte("LES ÂGES"), pancarte("LES ÉPOQUES"), pancarte("L'HOMME", 90), pancarte("INGÉNIOSITÉ !", 80)

def entree(t, t0, dur=0.0):   # saut d'entrée depuis le bas (0 -> 1 avec rebond)
    return spring(t - t0, 11, 5.5)
def sortie(t, t1): v = t - t1; return 0 if v < 0 else 3000 * v * v - 500 * v   # petit saut puis chute

def coller(img, im, x, y, k=1.0, rot=0):
    if k <= 0.02: return
    g = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    if rot: g = g.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(g, (int(CX + x - g.width / 2), int(CY + y - g.height)))

def image(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    # A : arrive sur « travers », pancarte sur « âges »
    if 0.24 <= t:
        k = entree(t, 0.24); y = 260 + (1 - k) * 500 + sortie(t, 2.3)
        if y < 900:
            sq = 1 + 0.25 * math.exp(-8 * (t - 0.5)) * math.sin(20 * (t - 0.5)) if t > 0.5 else 1
            reg = (1, 0) if t > 1.2 else (0.3, -0.6)
            A.dessin(img, d, -260, y, t, sq=sq, regard=reg)
            if t >= 0.78: coller(img, P_AGES, -260, y - 280, spring(t - 0.78), 4 * math.sin(4 * t))
    # B : arrive sur « époques »
    if 1.3 <= t:
        k = entree(t, 1.3); y = 260 + (1 - k) * 500 + sortie(t, 2.36)
        if y < 900:
            B.dessin(img, d, 240, y, t, regard=(-1, 0) if t < 1.9 else (0, -0.5))
            if t >= 1.48: coller(img, P_EPO, 240, y - 290, spring(t - 1.48), -4 * math.sin(4 * t))
    # C : « L'homme », ampoule sur « immense »
    if 2.5 <= t:
        k = entree(t, 2.5); y = 270 + (1 - k) * 560
        amp = clamp01((t - 3.76) / 0.15) if t >= 3.76 else 0
        C.dessin(img, d, 120, y, t, regard=(0, -1) if t > 3.8 else (-0.3, 0), ampoule=amp, yeux_k=1 + 0.3 * amp,
                 bouche=0.6 if t > 4.2 else 0)
        pan = P_ING if t >= 4.2 else P_HOM
        if t >= 2.56: coller(img, pan, 120 + 330, y - 330, spring(t - (4.2 if t >= 4.2 else 2.56)), 3 * math.sin(3 * t))
    # la foule fait « oooh » sur « ingéniosité »
    for k, b in enumerate(foule):
        t0 = 4.2 + 0.07 * k
        if t >= t0:
            y = 470 + (1 - entree(t, t0)) * 300
            b.dessin(img, d, -150 + 150 * k, y, t, bouche=0.7, yeux_k=1.3, regard=(0, -1))
    # narrateur : surgit en bas à gauche, parle sur la voix
    k = entree(t, 0.0)
    env = float(ENV[min(int(t * FPS), len(ENV) - 1)])
    narr.dessin(img, d, -700, 560 + 120 + (1 - k) * 500, t, sq=1 + 0.04 * math.sin(6 * t), bouche=env, regard=(0.8, -0.3))
    return img

if __name__ == "__main__":
    from doodle import rendre
    class F:   # adaptateur vers rendre() : un seul « élément » qui dessine toute l'image
        def rendu(s, img, drw, t): img.alpha_composite(image(t))
    out = os.path.join(ICI, "..", "3_RESULTATS")
    import doodle; doodle.BEIGE = CREME
    if len(sys.argv) > 1:
        doodle.apercu([F()], [0.6, 1.0, 1.8, 2.2, 3.0, 4.0, 4.6, 5.4], sys.argv[1])
    else:
        rendre([F()], DUREE, "TEST_bestioles", out)
