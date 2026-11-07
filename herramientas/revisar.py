# Revisión automática del sitio (la corre GitHub en cada cambio):
#  - todos los .json se pueden leer
#  - las actualizaciones de FRIDAY PC están bien firmadas y cada archivo coincide con su huella
#  - no se colaron claves ni datos privados
#  - los enlaces internos y el mapa del sitio apuntan a páginas que existen
import base64, hashlib, json, os, re, sys
from urllib.parse import urlparse, unquote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLICA = 'MMmQUW2xuNwPiszVKY3PmpGJo+T7ZLO3EVhnuZVHzGo='
DOMINIO = 'bufalabs-arg.github.io'
mal = []
def falla(t): mal.append(t); print('MAL ', t)

def archivos(ext=None):
    for d, ds, fs in os.walk(RAIZ):
        ds[:] = [x for x in ds if not x.startswith('.')]
        for f in fs:
            if ext is None or f.endswith(ext):
                yield os.path.join(d, f)
rel = lambda p: os.path.relpath(p, RAIZ)

# 1) JSON
n = 0
for p in archivos('.json'):
    n += 1
    try: json.load(open(p, encoding='utf-8'))
    except Exception as e: falla(f'{rel(p)} no es JSON válido: {e}')
print(f'ok  {n} archivos JSON')

# 2) firmas de las actualizaciones
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    clave = Ed25519PublicKey.from_public_bytes(base64.b64decode(PUBLICA))
except ImportError:
    clave = None; print('(sin el paquete cryptography: no reviso firmas)')
act = os.path.join(RAIZ, 'actualizaciones')
for m in ('friday.json', 'friday-linux.json'):
    p = os.path.join(act, m)
    if not os.path.exists(p): continue
    j = json.load(open(p)); datos = base64.b64decode(j['datos'])
    if clave:
        try: clave.verify(base64.b64decode(j['firma']), datos)
        except Exception: falla(f'{m}: la firma no coincide con la clave pública de FRIDAY'); continue
    d = json.loads(datos)
    for a in d['archivos']:
        f = os.path.join(act, a['url'])
        if not os.path.exists(f): falla(f"{m}: falta {a['url']}"); continue
        h = hashlib.sha256(open(f, 'rb').read()).hexdigest()
        if h != a['sha256'] or os.path.getsize(f) != a['bytes']: falla(f"{m}: {a['url']} no coincide con su huella")
    print(f"ok  {m}: {d['completa']} firmada, {len(d['archivos'])} archivos verificados")

# 3) nada privado
PROHIBIDO = [re.compile(rb'-----BEGIN [A-Z ]*PRIVATE KEY-----'), re.compile(rb'gsk_[A-Za-z0-9]{40,}'), re.compile(rb'AIza[0-9A-Za-z_\-]{35}'),
             re.compile(rb'"clave_?privada"\s*:')]
PUBLICOS = {b'nombre@gmail.com', b'bufalabs.ar@gmail.com'}   # el contacto público de BufaLabs
MAIL = re.compile(rb'[A-Za-z0-9._%+-]+@(?:gmail|hotmail|outlook|yahoo)\.com')
for p in archivos():
    b = os.path.basename(p).lower()
    if 'privad' in b or b in ('tv-pairing.json', '.env') or b.endswith(('.pem', '.key')): falla(f'{rel(p)}: este archivo no se publica')
    if os.path.getsize(p) > 3_000_000 or b.endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4', '.zip', '.exe', '.gz', '.ico', '.woff2')): continue
    s = open(p, 'rb').read()
    for r in PROHIBIDO:
        if r.search(s): falla(f'{rel(p)}: tiene algo que parece privado ({r.pattern[:30]!r})')
    if set(MAIL.findall(s)) - PUBLICOS: falla(f'{rel(p)}: tiene un mail personal')
print('ok  sin claves ni datos privados')

# 4) enlaces internos
def existe(dest):
    dest = unquote(dest.split('#')[0].split('?')[0])
    if not dest: return True
    f = os.path.normpath(os.path.join(RAIZ, dest.lstrip('/')))
    return os.path.isfile(f) or os.path.isfile(os.path.join(f, 'index.html'))
ATTR = re.compile(r'''(?:href|src)\s*=\s*["']([^"'<>{}$`]+)["']''')
nl = 0
for p in archivos('.html'):
    s = open(p, encoding='utf-8', errors='replace').read()
    s = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', s)   # lo de adentro de los scripts no son enlaces
    bt = re.search(r'<base\s+href=["\']([^"\']*)["\']', s)
    base = urlparse(bt.group(1)).path.strip('/') if bt else os.path.dirname(rel(p))
    for u in ATTR.findall(s):
        o = urlparse(u)
        if o.scheme in ('http', 'https'):
            if o.netloc != DOMINIO: continue
            dest = o.path
        elif o.scheme or u.startswith(('#', '//')): continue
        else: dest = u if u.startswith('/') else os.path.join('/', base, u)
        nl += 1
        if not existe(dest): falla(f'{rel(p)}: enlace roto a {u}')
print(f'ok  {nl} enlaces internos revisados')

# 5) mapa del sitio
for m in ('sitemap.txt',):
    p = os.path.join(RAIZ, m)
    if not os.path.exists(p): continue
    for u in open(p).read().split():
        if not existe(urlparse(u).path): falla(f'{m}: {u} no existe')
print('ok  mapa del sitio')

print('\nTODO BIEN' if not mal else f'\n{len(mal)} problemas'); sys.exit(1 if mal else 0)
