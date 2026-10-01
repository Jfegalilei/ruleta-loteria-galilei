"""Convierte el Excel de una lotería (con la columna tickets_a_sumar) en el CSV que lee el build.

Uso: python build/excel-a-csv.py <archivo.xlsx> <data/destino.csv>
Ejemplo: python build/excel-a-csv.py "GaliLotería Septiembre 2026 (para sumar tickets).xlsx" data/participantes.csv

Escribe las mismas columnas del Excel, pero tickets_actuales queda con el total (tickets_actuales +
tickets_a_sumar) y se quitan las columnas de apoyo. Calcula el total aquí mismo, así no depende de que
Excel haya guardado el resultado de la fórmula. Los enteros se escriben sin ".0".
"""
import csv, sys, unicodedata, openpyxl

def norm(s):
    s = unicodedata.normalize('NFD', str(s or '').strip().lower().replace('_', ' '))
    return ' '.join(''.join(c for c in s if not unicodedata.combining(c)).split())

src, dst = sys.argv[1], sys.argv[2]
ws = openpyxl.load_workbook(src, data_only=True).worksheets[0]
rows = [r for r in ws.iter_rows(values_only=True) if any(c is not None and str(c).strip() for c in r)]
head = [norm(h) for h in rows[0]]
i_t = next(i for i, h in enumerate(head) if h in ('tickets actuales', 'tickets', 'reviews'))
i_x = next((i for i, h in enumerate(head) if h == 'tickets a sumar'), None)
apoyo = {i for i, h in enumerate(head) if h in ('tickets a sumar', 'tickets totales')}
num = lambda v: int(float(v)) if v not in (None, '') else 0
fix = lambda v: '' if v is None else (str(int(v)) if isinstance(v, float) and v.is_integer() else str(v).strip())
sumados = 0
with open(dst, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow([fix(h) for i, h in enumerate(rows[0]) if i not in apoyo])
    for r in rows[1:]:
        r = list(r)
        if i_x is not None and num(r[i_x]):
            sumados += 1
            r[i_t] = num(r[i_t]) + num(r[i_x])
        w.writerow([fix(v) for i, v in enumerate(r) if i not in apoyo])
print(f'{dst}: {len(rows) - 1} personas, {sumados} con tickets sumados')
