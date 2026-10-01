"""Arma la ruleta a partir de las fuentes editables.

Uso (desde la raíz del repo):  python build/build.py

1. data/participantes.csv  ->  data/participantes.js   (lo que carga index.html)
2. index.html + assets/ + data/  ->  dist/Ruleta Loteria Galilei.html
   Un solo archivo con todo embebido (datos, moto, audio y fuentes). Funciona sin internet:
   es el que se usa el día del evento.
3. dist/artifact.html: la misma página sin <html>/<head>/<body> y con las fuentes de
   Google enlazadas, para publicarla como artifact de Claude.

Solo usa la librería estándar de Python. Necesita internet para bajar las fuentes.
"""
import base64, csv, json, os, re, urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = lambda *a: os.path.join(ROOT, *a)


# ---------- 1. CSV -> participantes.js ----------
def fix_mojibake(s):
    """El export a veces trae UTF-8 leído como Windows-1252 (VIÃ‘AS -> VIÑAS)."""
    if 'Ã' in s:
        try:
            return s.encode('cp1252').decode('utf-8')
        except UnicodeError:
            pass
    return s

def num(v):
    return int(re.sub(r'\D', '', v or '') or 0)

def col(row, *names):
    for n in names:
        if n in row:
            return row[n]
    return ''

def build_data():
    """Una fila por Player id. Tickets: el mayor. Juegos y puntaje: la fila del año más reciente."""
    people = {}
    with open(p('data', 'participantes.csv'), encoding='utf-8-sig') as f:
        for x in csv.DictReader(f):
            pid = col(x, 'Player id', 'id')
            year = num(col(x, 'Year', 'Anio', 'Año'))
            row = {
                'id': pid[:8],
                'n': fix_mojibake(col(x, 'Player', 'Nombre').strip()),
                'c': fix_mojibake(col(x, 'Empresa').strip()),
                'l': fix_mojibake(col(x, 'Location', 'Sede').strip()),
                't': num(col(x, 'Tickets actuales', 'Tickets')),
                'g': num(col(x, 'Games played', 'Partidas')),
                's': num(col(x, 'Max score', 'Puntaje maximo')),
                '_y': year,
            }
            prev = people.get(pid)
            if prev:
                row['t'] = max(row['t'], prev['t'])
                if year <= prev['_y']:
                    prev['t'] = row['t']
                    continue
            people[pid] = row
    rows = [{k: v for k, v in r.items() if k != '_y'} for r in people.values()]
    js = ('// Generado por build/build.py desde data/participantes.csv. No editar a mano.\n'
          'window.PARTICIPANTES_FUENTE = "data/participantes.csv";\n'
          'window.PARTICIPANTES = ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';\n')
    open(p('data', 'participantes.js'), 'w', encoding='utf-8').write(js)
    print(f'participantes: {len(rows)} personas')
    return js


# ---------- 2 y 3. standalone y artifact ----------
def data_uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def embedded_fonts(html):
    """Descarga el CSS de Google Fonts que enlaza index.html y embebe el subset latin."""
    url = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com[^"]+)"', html).group(1)
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
    css = urllib.request.urlopen(urllib.request.Request(url.replace('&amp;', '&'), headers={'User-Agent': ua})).read().decode()
    faces = []
    for subset, block in re.findall(r'/\* (\S+) \*/\s*(@font-face \{.*?\})', css, re.S):
        if subset != 'latin':
            continue
        font_url = re.search(r'url\((https://[^)]+)\)', block).group(1)
        font = base64.b64encode(urllib.request.urlopen(font_url).read()).decode()
        faces.append(block.replace(font_url, 'data:font/woff2;base64,' + font))
    return '\n'.join(faces)

def build_pages(data_js):
    html = open(p('index.html'), encoding='utf-8').read()

    def sub_once(pattern, repl, text):
        out, n = re.subn(pattern, lambda m: repl, text, count=1)
        assert n == 1, pattern
        return out

    html = sub_once(r'<script src="data/participantes\.js"></script>', '<script>\n' + data_js + '</script>', html)
    html = sub_once(r'const MOTO = "assets/moto-gali\.webp";', f'const MOTO = "{data_uri(p("assets", "moto-gali.webp"), "image/webp")}";', html)
    html = sub_once(r'const ESCENA = "assets/siderax-moto\.webp";', f'const ESCENA = "{data_uri(p("assets", "siderax-moto.webp"), "image/webp")}";', html)
    # imágenes referenciadas con src="assets/..." en el HTML (símbolo de Galilei, Gali, etc.)
    mimes = {'.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.mp4': 'video/mp4'}
    html = re.sub(r'src="assets/([^"]+)"',
                  lambda m: f'src="{data_uri(p("assets", m.group(1)), mimes[os.path.splitext(m.group(1))[1].lower()])}"', html)
    # fondos del CSS: url("assets/...")
    html = re.sub(r'url\("assets/([^"]+)"\)',
                  lambda m: f'url("{data_uri(p("assets", m.group(1)), mimes[os.path.splitext(m.group(1))[1].lower()])}")', html)
    html = sub_once(r'const WIN_AUDIO = "assets/victoria\.mp3";', f'const WIN_AUDIO = "{data_uri(p("assets", "victoria.mp3"), "audio/mpeg")}";', html)
    os.makedirs(p('dist'), exist_ok=True)

    # artifact: sin envoltura de documento (el visor de Claude pone la suya), fuentes enlazadas
    art = re.sub(r'<!doctype html>\s*<html[^>]*>\s*<head>\s*', '', html, flags=re.I)
    art = re.sub(r'<meta [^>]*>\s*', '', art)
    art = re.sub(r'\s*</head>\s*<body>\s*', '\n', art)
    art = re.sub(r'\s*</body>\s*</html>\s*$', '\n', art)
    open(p('dist', 'artifact.html'), 'w', encoding='utf-8').write(art)

    # standalone: fuentes embebidas, sin nada externo
    alone = re.sub(r'<link rel="preconnect"[^>]*>\n', '', html)
    alone = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>\n', '', alone)
    alone = alone.replace('<style>\n', '<style>\n' + embedded_fonts(html) + '\n', 1)
    assert 'googleapis' not in alone and 'assets/' not in alone
    out = p('dist', 'Ruleta Loteria Galilei.html')
    open(out, 'w', encoding='utf-8').write(alone)
    print(f'standalone: {round(len(alone) / 1024)} KB -> dist/Ruleta Loteria Galilei.html')


if __name__ == '__main__':
    build_pages(build_data())
