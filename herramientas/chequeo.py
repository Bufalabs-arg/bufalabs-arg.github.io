# Chequeo semanal de BufaLabs (lo corre GitHub todos los domingos; también a mano desde Actions).
# Revisa que la página, las descargas, FRIDAY Móvil y el servidor anden, y que a las llaves les quede cupo.
# Escribe un informe en Markdown y termina con error si algo anda mal (así GitHub abre un aviso).
import json, os, sys, time, urllib.request, urllib.error

SITIO = os.environ.get('SITIO', 'https://bufalabs-arg.github.io')
CELU = os.environ.get('CELU', 'https://pedropiratita134.github.io/FRIDAY')
SERVIDOR = os.environ.get('SERVIDOR', 'https://bufalabs.pedrobufager.workers.dev')
mal, ojo, bien = [], [], []

def pedir(url, metodo='GET', datos=None, cab=None, tiempo=25):
    req = urllib.request.Request(url, method=metodo, data=datos, headers={'User-Agent': 'BufaLabs-chequeo/1', **(cab or {})})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=tiempo) as r:
            return r.status, r.read() if metodo != 'HEAD' else b'', dict(r.headers), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, e.read() if metodo != 'HEAD' else b'', dict(e.headers or {}), time.time() - t
    except Exception as e:
        return 0, str(e).encode(), {}, time.time() - t

def revisar(nombre, ok, detalle='', aviso=False):
    (bien if ok else (ojo if aviso else mal)).append((nombre, detalle))

# ---- la página
for ruta in ('/', '/instalar/', '/novedades/', '/tutoriales/', '/diferencias/', '/ayuda/', '/sitemap.txt'):
    st, cuerpo, _, seg = pedir(SITIO + ruta)
    revisar(f'Página {ruta}', st == 200 and len(cuerpo) > 200, f'respondió {st}' if st != 200 else f'{seg:.1f} s')
for ruta, minimo in (('/descargas/FRIDAY-Setup.exe', 2_000_000), ('/descargas/FRIDAY.zip', 2_000_000), ('/descargas/FRIDAY-linux.tar.gz', 2_000_000)):
    st, _, cab, _ = pedir(SITIO + ruta, 'HEAD')
    tam = int(cab.get('Content-Length') or cab.get('content-length') or 0)
    revisar(f'Descarga {ruta.split("/")[-1]}', st == 200 and tam >= minimo, f'respondió {st}, {tam // 1048576} MB')
st, cuerpo, _, _ = pedir(SITIO + '/actualizaciones/friday.json')
try:
    import base64
    d = json.loads(base64.b64decode(json.loads(cuerpo)['datos'])); revisar('Actualización de la compu publicada', True, d['completa'])
except Exception as e:
    revisar('Actualización de la compu publicada', False, f'no se pudo leer ({st})')

# ---- FRIDAY Móvil
st, cuerpo, _, _ = pedir(CELU + '/version.json')
try: v = json.loads(cuerpo)['version']; revisar('FRIDAY Móvil publicada', True, 'versión ' + v)
except Exception: revisar('FRIDAY Móvil publicada', False, f'version.json respondió {st}')
st, cuerpo, _, _ = pedir(CELU + '/')
revisar('FRIDAY Móvil abre', st == 200 and b'FRIDAY' in cuerpo, f'respondió {st}')

# ---- el servidor
st, cuerpo, _, seg = pedir(SERVIDOR + '/ping')
try:
    p = json.loads(cuerpo)
    revisar('Servidor vivo', st == 200 and p.get('ok'), f"v{p.get('rev') or p.get('v')}, {seg:.1f} s")
    revisar('Servidor con llaves de Groq', (p.get('groq') or 0) > 0, f"{p.get('groq')} llaves")
    revisar('Servidor con respaldo de Cloudflare', bool(p.get('cloudflare')), 'falta el enlace AI' if not p.get('cloudflare') else 'sí', aviso=True)
    revisar('Avisos con el celu bloqueado', bool(p.get('avisos')), 'falta la base D1 o el código nuevo' if not p.get('avisos') else 'sí', aviso=True)
    c = p.get('cupo')
    if c: revisar('Cupo de las llaves', c['pensar_pct_min'] >= 15, f"a la más usada le queda {c['pensar_pct_min']}% hoy", aviso=True)
except Exception:
    revisar('Servidor vivo', False, f'respondió {st}: {cuerpo[:120]!r}')
cuerpo_chat = json.dumps({'model': 'openai/gpt-oss-20b', 'messages': [{'role': 'user', 'content': 'Respondé solo con la palabra: listo'}], 'max_tokens': 20}).encode()
st, cuerpo, cab, seg = pedir(SERVIDOR + '/openai/v1/chat/completions', 'POST', cuerpo_chat, {'Content-Type': 'application/json', 'X-Friday': 'web-chequeosemanal'}, 60)
try: txt = json.loads(cuerpo)['choices'][0]['message']['content']
except Exception: txt = ''
revisar('El servidor piensa', st == 200 and bool(txt.strip()), f"con {cab.get('X-Cerebro') or cab.get('x-cerebro') or '?'}, {seg:.1f} s" if st == 200 else f'respondió {st}')
st, cuerpo, _, _ = pedir(SERVIDOR + '/estado')
try:
    e = json.loads(cuerpo).get('err') or []
    revisar('Errores recientes del servidor', len(e) < 15, f'{len(e)} en la memoria del servidor' + (': ' + ', '.join(sorted({f"{x.get('ruta')}/{x.get('cerebro')} {x.get('status')}" for x in e[-8:]})) if e else ''), aviso=True)
except Exception: pass

# ---- el informe
hoy = time.strftime('%d/%m/%Y', time.gmtime(time.time() - 3 * 3600))
lin = [f'## Chequeo semanal · {hoy}', '']
if mal: lin += ['**Algo anda mal:**', ''] + [f'- ❌ {n}: {d}' for n, d in mal] + ['']
if ojo: lin += ['**Para mirar:**', ''] + [f'- ⚠️ {n}: {d}' for n, d in ojo] + ['']
lin += ['**Anda bien:**', ''] + [f'- ✅ {n}' + (f': {d}' if d else '') for n, d in bien]
print('\n'.join(lin))
with open(os.environ.get('GITHUB_OUTPUT', os.devnull), 'a') as f:
    f.write(f'mal={len(mal)}\nojo={len(ojo)}\n')
sys.exit(1 if mal else 0)
