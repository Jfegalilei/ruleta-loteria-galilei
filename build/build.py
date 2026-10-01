"""Arma la ruleta a partir de las fuentes editables.

Uso (desde la raíz del repo):  python build/build.py

1. data/loterias.json + un CSV por lotería  ->  data/participantes.js   (lo que carga index.html)
   loterias.json lista las loterías del selector: id, nombre, título del premio, CSV y, salvo la
   de la moto, las imágenes "escena" (debajo de la ruleta) y "premio" (en el anuncio), o null.
2. index.html + assets/ + data/  ->  dist/Ruleta Loteria Galilei.html
   Un solo archivo con todo embebido (datos, moto, audio y fuentes). Funciona sin internet:
   es el que se usa el día del evento.
3. dist/artifact.html: la misma página sin <html>/<head>/<body> y con las fuentes de
   Google enlazadas, para publicarla como artifact de Claude.

Solo usa la librería estándar de Python. Necesita internet para bajar las fuentes.
"""
import base64, csv, hashlib, json, os, re, unicodedata, urllib.request

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

def norm_col(s):
    """Nombre de columna comparable: sin mayúsculas, tildes ni guiones bajos (tickets_actuales = Tickets actuales)."""
    s = unicodedata.normalize('NFD', (s or '').strip().lower().replace('_', ' '))
    return re.sub(r'\s+', ' ', ''.join(ch for ch in s if not unicodedata.combining(ch)))

def col(row, *names):
    cols = {norm_col(k): v for k, v in row.items() if k is not None}
    for n in names:
        if norm_col(n) in cols and cols[norm_col(n)] is not None:
            return cols[norm_col(n)]
    return ''

def clave_persona(nombre, empresa):
    """Sin Player id, una persona es su nombre + empresa (sin tildes, mayúsculas ni espacios de más)."""
    t = unicodedata.normalize('NFD', f'{nombre}|{empresa}'.lower())
    return re.sub(r'\s+', ' ', ''.join(ch for ch in t if not unicodedata.combining(ch))).strip()

def read_csv(name, columnas=(), sumar=False, empresa_fija=''):
    """Una fila por persona (Player id, o nombre + empresa si no hay id).
    Normal: tickets, el mayor; juegos y puntaje, la fila del año más reciente.
    sumar=True (Reviews): el CSV trae una fila por persona y sede, y se suman las de cada persona;
    la sede que se muestra es la de más reviews."""
    people = {}
    if not os.path.exists(p('data', name)):
        return []
    with open(p('data', name), encoding='utf-8-sig') as f:
        for x in csv.DictReader(f):
            nombre = fix_mojibake(col(x, 'Player', 'Nombre', 'Jugador').strip())
            empresa = fix_mojibake(col(x, 'Empresa', 'company', 'Company').strip()) or empresa_fija  # Auteco: el export no trae empresa
            if not nombre:
                continue
            pid = col(x, 'Player id', 'id') or hashlib.sha1(clave_persona(nombre, empresa).encode()).hexdigest()
            year = num(col(x, 'Year', 'Anio', 'Año'))
            row = {
                'id': pid[:8],
                'n': nombre,
                'c': empresa,
                'l': fix_mojibake(col(x, 'Location', 'Sede', 'location_name', 'Rol').strip()),  # Auteco: el rol hace de sede
                't': num(col(x, *columnas, 'Tickets actuales', 'Tickets')),  # en Reviews, cada review es un ticket
                'g': num(col(x, 'Games played', 'Partidas', 'Juegos sept', 'Juegos')),
                's': num(col(x, 'Max score', 'Puntaje maximo', 'Puntaje max sept', 'Puntaje máximo')),
                '_y': year,
            }
            prev = people.get(pid)
            if prev and sumar:
                if row['t'] > prev['_max']:
                    prev['l'], prev['_max'] = row['l'], row['t']
                prev['t'] += row['t']
                continue
            if sumar:
                row['_max'] = row['t']
            if prev:
                row['t'] = max(row['t'], prev['t'])
                if year <= prev['_y']:
                    prev['t'] = row['t']
                    continue
            people[pid] = row
    return [{k: v for k, v in r.items() if k not in ('_y', '_max')} for r in people.values()]

IMG_MIMES = {'.png': 'image/png', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml'}

def build_data():
    """Lee data/loterias.json y el CSV de cada lotería.
    Devuelve (js del repo, js del standalone con las imágenes de cada lotería embebidas)."""
    lots = json.load(open(p('data', 'loterias.json'), encoding='utf-8'))
    assert lots and lots[0]['id'] == 'moto', 'La primera lotería debe ser la de la moto (usa las claves de siempre)'
    out = []
    for l in lots:
        rows = read_csv(l['csv'], l.get('columnas', ()), l.get('sumar', False), l.get('empresa', ''))
        item = {k: v for k, v in l.items() if k not in ('csv', 'columnas', 'sumar')}
        item['fuente'] = 'data/' + l['csv']
        item['participantes'] = rows
        out.append(item)
        print(f"{l['id']}: {len(rows)} personas" + ('' if rows else f" (falta data/{l['csv']})"))

    def js(items):
        return ('// Generado por build/build.py desde data/loterias.json y sus CSV. No editar a mano.\n'
                'window.LOTERIAS = ' + json.dumps(items, ensure_ascii=False, separators=(',', ':')) + ';\n')
    embedded = []
    for item in out:
        e = dict(item)
        for k in ('escena', 'premio'):
            if e.get(k):
                e[k] = data_uri(p(*e[k].split('/')), IMG_MIMES[os.path.splitext(e[k])[1].lower()])
        embedded.append(e)
    repo_js = js(out)
    open(p('data', 'participantes.js'), 'w', encoding='utf-8').write(repo_js)
    return repo_js, js(embedded)


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

    # index.html pide la lista con document.write y una marca de tiempo (sin caché); aquí va embebida
    html = sub_once(r'<script>document\.write\(\'<script src="data/participantes\.js\?t=[^\n]*?</script>', '<script>\n' + data_js + '</script>', html)
    html = sub_once(r'const MOTO = "assets/moto-gali\.webp";', f'const MOTO = "{data_uri(p("assets", "moto-gali.webp"), "image/webp")}";', html)
    html = sub_once(r'const ESCENA = "assets/siderax-moto\.webp";', f'const ESCENA = "{data_uri(p("assets", "siderax-moto.webp"), "image/webp")}";', html)
    # imágenes referenciadas con src="assets/..." en el HTML (símbolo de Galilei, Gali, etc.)
    mimes = {'.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.mp4': 'video/mp4', '.mp3': 'audio/mpeg'}
    html = re.sub(r'src="assets/([^"]+)"',
                  lambda m: f'src="{data_uri(p("assets", m.group(1)), mimes[os.path.splitext(m.group(1))[1].lower()])}"', html)
    # imágenes dentro de SVG: href="assets/..."
    html = re.sub(r'href="assets/([^"]+)"',
                  lambda m: f'href="{data_uri(p("assets", m.group(1)), mimes[os.path.splitext(m.group(1))[1].lower()])}"', html)
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
    build_pages(build_data()[1])
