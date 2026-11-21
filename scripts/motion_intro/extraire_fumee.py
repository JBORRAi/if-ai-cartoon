"""Découpe la planche de fumée (PRINCIPES_ANIMATION/*.avif, 3 x 2 dessins) en 6 images détourées, en miroir
(la traînée doit suivre le mot qui part vers la droite), teintes adaptées au papier. -> ASSETS/fumee/fumee_1..6.png"""
import os, glob, subprocess, numpy as np
from PIL import Image
ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = glob.glob(os.path.join(ICI, "PRINCIPES_ANIMATION", "*.avif"))[0]
png = os.path.join(ICI, "ASSETS", "fumee", "_planche.png")
subprocess.run(["sips", "-s", "format", "png", src, "--out", png], capture_output=True)
a = np.array(Image.open(png).convert("RGB")).astype(np.float32)
fond = a[5, 5]
masque = np.clip((np.abs(a - fond).sum(axis=2) - 25) / 40, 0, 1)
H, W = masque.shape
masque[:4, :] = masque[-4:, :] = 0; masque[:, :4] = masque[:, -4:] = 0
from scipy import ndimage
lab, n = ndimage.label(masque > 0.3)
lum = a.mean(axis=2)
k = np.clip((lum - 90) / 150, 0, 1)[..., None]
sombre, clair = np.array([150, 140, 128]), np.array([252, 248, 238])
rgb = sombre + (clair - sombre) * k
M = 140                                                   # marge : les traînées peuvent déborder de leur case
for r in range(2):
    for c in range(3):
        sel = np.zeros_like(masque)
        for i in range(1, n + 1):                         # chaque tache va au dessin dont la case contient son centre
            ys, xs = np.nonzero(lab == i)
            if len(xs) < 12: continue                    # poussières de compression
            if int(ys.mean() // (H / 2)) == r and int(xs.mean() // (W / 3)) == c: sel[lab == i] = masque[lab == i]
        y0, y1, x0, x1 = r * H // 2, (r + 1) * H // 2, c * W // 3 - M, (c + 1) * W // 3 + M
        canvas = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
        xa, xb = max(x0, 0), min(x1, W)
        canvas[:, xa - x0:xb - x0, :3] = rgb[y0:y1, xa:xb]; canvas[:, xa - x0:xb - x0, 3] = sel[y0:y1, xa:xb] * 255
        Image.fromarray(canvas, "RGBA").transpose(Image.FLIP_LEFT_RIGHT).save(os.path.join(ICI, "ASSETS", "fumee", f"fumee_{r * 3 + c + 1}.png"))
print("ok")
