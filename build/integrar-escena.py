"""Integra una imagen (personaje con fondo transparente) en la escena nocturna del planeta de Siderax:
menos saturación, tonos medios más oscuros, tinte frío (luz azul del planeta) y un poco de luz cian de
los cristales en los bordes. Se mezcla con la imagen original según la fuerza, y los tonos cálidos
(bolsa, monedas) pueden llevar más ajuste que el resto.

Uso: python build/integrar-escena.py <imagen con fondo transparente> <salida.webp> [fuerza] [calidos]
  fuerza   cuánto ajuste en general, de 0 a 1 (por defecto 1)
  calidos  ajuste para los tonos cálidos (naranja, marrón, dorado), de 0 a 1 (por defecto = fuerza)
Así se hizo assets/siderax-dinero.webp:
  python build/integrar-escena.py siderax.png assets/siderax-dinero.webp 0.25 0.6
"""
import numpy as np, os, sys
from PIL import Image, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
fuerza = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
calidos = float(sys.argv[4]) if len(sys.argv) > 4 else fuerza

im = Image.open(SRC).convert('RGBA')
a = np.asarray(im)[:, :, 3]
ys, xs = np.nonzero(a > 20)
im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
arr = np.asarray(im).astype(np.float32) / 255
orig, al = arr[:, :, :3], arr[:, :, 3:]

# ajuste completo
lum = (orig * [0.2126, 0.7152, 0.0722]).sum(2, keepdims=True)
rgb = lum + (orig - lum) * 0.62                     # menos saturación
rgb = np.power(np.clip(rgb, 0, 1), 1.18) * 0.86     # tonos medios más oscuros
rgb = rgb * np.array([0.90, 0.95, 1.10])            # tinte frío
lum2 = (rgb * [0.2126, 0.7152, 0.0722]).sum(2, keepdims=True)
rgb = rgb + (1 - lum2) * np.array([0.00, 0.012, 0.045])   # sombras con ambiente azul
A = Image.fromarray((al[:, :, 0] * 255).astype(np.uint8))
inner = np.asarray(A.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
rim = np.clip(al[:, :, 0] - inner, 0, 1)[:, :, None]
rgb = rgb + rim * np.array([0.10, 0.32, 0.42]) * 0.55

# cuánto se aplica en cada píxel: más en los tonos cálidos
r, g, b = orig[:, :, 0], orig[:, :, 1], orig[:, :, 2]
calido = np.clip((r - b - 0.12) / 0.25, 0, 1) * (r >= g * 0.95)
calido = np.asarray(Image.fromarray((calido * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), np.float32)[:, :, None] / 255
w = fuerza + (calidos - fuerza) * calido
out_rgb = orig * (1 - w) + np.clip(rgb, 0, 1) * w

out = np.concatenate([np.clip(out_rgb, 0, 1), al], 2)
Image.fromarray((out * 255).astype(np.uint8)).save(OUT, 'WEBP', quality=90, method=6)
px = out[:, :, :3][out[:, :, 3] > 0.8] * 255
print('guardado', OUT, im.size, 'luz', round(px.mean(1).mean(), 1), 'sat', round((px.max(1) - px.min(1)).mean(), 1),
      os.path.getsize(OUT) // 1024, 'KB')
