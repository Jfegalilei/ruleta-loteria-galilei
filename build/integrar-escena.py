"""Integra una imagen (personaje con fondo transparente) en la escena nocturna del planeta de Siderax:
menos saturación, tonos medios más oscuros, tinte frío (luz azul del planeta) y un poco de luz cian de
los cristales en los bordes. Así se hizo assets/siderax-dinero.webp.

Uso: python build/integrar-escena.py <imagen con fondo transparente> <salida.webp> [saturación, 0.62]
Ejemplo: python build/integrar-escena.py siderax.png assets/siderax-dinero.webp
"""
import numpy as np, os, sys
from PIL import Image, ImageFilter
SRC, OUT = sys.argv[1], sys.argv[2]
im =Image.open(SRC).convert('RGBA')
a = np.asarray(im)[:, :, 3]
ys, xs = np.nonzero(a > 20)
im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
arr = np.asarray(im).astype(np.float32) / 255
rgb, al = arr[:, :, :3], arr[:, :, 3:]
lum = (rgb * [0.2126, 0.7152, 0.0722]).sum(2, keepdims=True)
sat = float(sys.argv[3]) if len(sys.argv) > 3 else 0.62
rgb = lum + (rgb - lum) * sat                       # menos saturación
rgb = np.power(np.clip(rgb, 0, 1), 1.18) * 0.86     # tonos medios más oscuros
rgb = rgb * np.array([0.90, 0.95, 1.10])            # tinte frío
lum2 = (rgb * [0.2126, 0.7152, 0.0722]).sum(2, keepdims=True)
rgb = rgb + (1 - lum2) * np.array([0.00, 0.012, 0.045])   # sombras con ambiente azul
# luz cian en el borde: alfa erosionado vs. original = contorno, difuminado hacia dentro
A = Image.fromarray((al[:, :, 0] * 255).astype(np.uint8))
inner = np.asarray(A.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
rim = np.clip(al[:, :, 0] - inner, 0, 1)[:, :, None]
rgb = rgb + rim * np.array([0.10, 0.32, 0.42]) * 0.55
out = np.concatenate([np.clip(rgb, 0, 1), al], 2)
Image.fromarray((out * 255).astype(np.uint8)).save(OUT, 'WEBP', quality=90, method=6)
px = (out[:, :, :3][out[:, :, 3] > 0.8] * 255)
l = px.mean(1)
print('guardado', OUT, im.size, 'luz', round(l.mean(), 1), 'sat', round((px.max(1) - px.min(1)).mean(), 1), os.path.getsize(OUT) // 1024, 'KB')
