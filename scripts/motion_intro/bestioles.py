"""Bestioles doodle (générées en code) qui portent la narration : corps en blob, yeux qui clignent et regardent,
bouche qui parle sur l'enveloppe de la voix off, pancartes. Trait bleu marine, aplats pastel, fond crème."""
import math, os, random, subprocess, numpy as np, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from doodle import W, H, CX, CY, spring, smooth, clamp01

MARINE = (96, 62, 38, 255)   # trait sépia (nom historique)
CREME = (250, 244, 232)
PASTELS = [(246, 168, 92), (250, 210, 110), (140, 200, 205), (245, 160, 170), (175, 210, 140), (190, 175, 230)]
MARKER = "/System/Library/Fonts/Supplemental/MarkerFelt.ttc"
LW = 8

def enveloppe(mp3, fps=60, duree=20.0):
    """volume de la voix image par image (0..1), lissé."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    raw = subprocess.run([ff, "-v", "error", "-t", str(duree), "-i", mp3, "-ac", "1", "-ar", "48000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    n = 48000 // fps
    rms = np.array([np.sqrt(np.mean(a[i:i + n] ** 2)) for i in range(0, len(a) - n, n)])
    rms = np.clip((rms - 0.01) / (np.percentile(rms, 95) - 0.01 + 1e-6), 0, 1)
    out = np.copy(rms)
    for i in range(1, len(out)): out[i] = max(rms[i], out[i - 1] * 0.6)
    return out

class Bestiole:
    def __init__(s, seed, R=80, couleur=None, yeux=None, bouche=None, antenne=None):
        r = random.Random(seed); s.seed = seed
        s.R = R; s.h = r.uniform(0.85, 1.3)
        s.coul = couleur or r.choice(PASTELS)
        s.a, s.b, s.ph, s.ps = r.uniform(.04, .1), r.uniform(.02, .07), r.uniform(0, 6), r.uniform(0, 6)
        s.yeux = yeux if yeux is not None else r.choice([1, 2, 2, 2, 3])
        s.bouche = bouche or r.choice(["dents", "sourire", "dents"])
        s.antenne = antenne if antenne is not None else r.choice([0, 1, 2])
        s.clignes = [r.uniform(0.5, 3) + 2.6 * k for k in range(12)]

    def dessin(s, img, drw, x, y, t, sq=1.0, bouche=0.0, regard=(0, 0), rot=0.0, ampoule=0.0, yeux_k=1.0):
        R, h = s.R, s.h * sq
        sx = 1 / math.sqrt(max(sq, 0.2))
        cx, cy = x, y - (R * h + 22)
        def P(px, py): return (CX + cx + px * sx, CY + cy + py)
        # pattes
        for d in (-1, 1):
            a = P(d * R * 0.35, R * h * 0.85); b = (a[0] + d * 6, CY + y)
            drw.line([a, b], fill=MARINE, width=LW); drw.line([(b[0] - 14 * (d < 0) , b[1]), (b[0] + 14 * (d > 0), b[1])], fill=MARINE, width=LW)
        # antennes
        for k in range(s.antenne):
            d = (-1) ** k * (0.3 if s.antenne == 2 else 0)
            base = P(d * R, -R * h * 0.92); top = (base[0] + d * 50 + 8 * math.sin(3 * t + k), base[1] - 70)
            drw.line([base, top], fill=MARINE, width=LW - 2)
            rr = 13 + 10 * ampoule
            col = (250, 200, 70, 255) if ampoule > 0 else MARINE
            drw.ellipse((top[0] - rr, top[1] - rr, top[0] + rr, top[1] + rr), fill=col, outline=MARINE, width=5)
            if ampoule > 0:
                for i in range(8):
                    an = i * math.pi / 4; r0, r1 = rr + 10, rr + 10 + 24 * ampoule
                    drw.line([(top[0] + r0 * math.cos(an), top[1] + r0 * math.sin(an)), (top[0] + r1 * math.cos(an), top[1] + r1 * math.sin(an))], fill=MARINE, width=5)
        # corps
        pts = []
        for i in range(64):
            th = 2 * math.pi * i / 64
            rr = R * (1 + s.a * math.sin(3 * th + s.ph) + s.b * math.sin(5 * th + s.ps))
            pts.append(P(rr * math.cos(th), rr * h * math.sin(th)))
        drw.polygon(pts, fill=s.coul + (255,)); drw.line(pts + [pts[0]], fill=MARINE, width=LW, joint="curve")
        # hachures crayon sur le bas du corps
        rnd = random.Random(s.seed * 31 + int(t * 8))
        for i in range(7):
            xx = -R * 0.6 + i * R * 0.2
            drw.line([P(xx + rnd.uniform(-3, 3), R * h * 0.45), P(xx + 26 + rnd.uniform(-3, 3), R * h * 0.75)], fill=MARINE[:3] + (90,), width=3)
        # yeux
        cl = any(0 <= t - c < 0.12 for c in s.clignes)
        ry = R * 0.2 * yeux_k
        xs = [0] if s.yeux == 1 else [-R * 0.32, R * 0.32] if s.yeux == 2 else [-R * 0.42, 0, R * 0.42]
        for i, ex in enumerate(xs):
            r_ = ry * (1.35 if s.yeux == 1 else 1.0) * (0.85 if s.yeux == 3 and i == 1 else 1)
            ey = -R * h * 0.28 - (10 if s.yeux == 3 and i == 1 else 0)
            c = P(ex, ey)
            if cl:
                drw.line([(c[0] - r_, c[1]), (c[0] + r_, c[1])], fill=MARINE, width=LW - 2); continue
            drw.ellipse((c[0] - r_, c[1] - r_, c[0] + r_, c[1] + r_), fill=(255, 255, 255, 255), outline=MARINE, width=6)
            pr = r_ * 0.45; px, py = c[0] + regard[0] * r_ * 0.45, c[1] + regard[1] * r_ * 0.45
            drw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=MARINE)
        # bouche
        m = P(0, R * h * 0.22)
        bw = R * 0.45
        if s.bouche == "sourire" and bouche < 0.15:
            drw.arc((m[0] - bw, m[1] - bw * 0.6, m[0] + bw, m[1] + bw * 0.6), 20, 160, fill=MARINE, width=LW - 2)
        else:
            bh = R * (0.06 + 0.42 * bouche)
            drw.ellipse((m[0] - bw, m[1] - bh, m[0] + bw, m[1] + bh), fill=(70, 36, 24, 255), outline=MARINE, width=6)
            if s.bouche == "dents" and bh > R * 0.1:
                for k in range(4):
                    x0 = m[0] - bw * 0.6 + k * bw * 0.3
                    drw.polygon([(x0, m[1] - bh + 4), (x0 + bw * 0.26, m[1] - bh + 4), (x0 + bw * 0.13, m[1] - bh + 4 + bh * 0.5)], fill=(255, 255, 255, 255))

def pancarte(texte, taille=70):
    f = ImageFont.truetype(MARKER, taille, index=0)
    l, t, r, b = f.getbbox(texte)
    w, h = r - l + 70, b - t + 50
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), radius=18, fill=(255, 255, 255, 255), outline=MARINE, width=7)
    d.text((10 + 35 - l, 10 + 25 - t), texte, font=f, fill=MARINE)
    return im
