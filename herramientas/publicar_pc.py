#!/usr/bin/env python3
"""Publica una versión de FRIDAY para la compu en la página de BufaLabs.

Arma actualizaciones/friday.json (firmado) y copia a actualizaciones/v<versión>/ solo los archivos que
cambiaron (los que quedaron igual apuntan a la versión donde ya estaban). También rehace la descarga
completa (descargas/FRIDAY.zip).

Uso: python3 publicar_pc.py <carpeta de FRIDAY> <repo de la página> <archivo con la clave privada>
"""
import base64, hashlib, json, os, re, shutil, sys, zipfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ARCHIVOS = ['friday.html', 'FRIDAY.exe', 'bufalabs.ico', 'friday.ico', 'INSTALAR-FRIDAY.bat',
            'instalar-voz.bat', 'presentacion-friday.html', 'LEEME-EXE.txt']
EN_EL_ZIP = ['FRIDAY.exe', 'friday.html', 'bufalabs.ico', 'friday.ico', 'INSTALAR-FRIDAY.bat', 'instalar-voz.bat']


def huella(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main(fri, sitio, clave):
    html = open(os.path.join(fri, 'friday.html'), encoding='utf-8').read()
    ver = re.search(r"const FRIDAY_VER\s*=\s*'(\d+(?:\.\d+)?)'", html).group(1)   # "101.02"
    grande = ver.split('.')[0]                                                    # "101" (lo que entienden las FRIDAY viejas)
    nov = json.loads(re.search(r'const NOVEDADES=(\{.*?\});\n', html).group(1))
    assert nov['version'] == ver, 'NOVEDADES no es de esta versión'
    exe = re.search(r'appVersion\s*=\s*"([\d.]+)"', open(os.path.join(fri, 'codigo-exe', 'main.go')).read()).group(1)
    act = os.path.join(sitio, 'actualizaciones')
    os.makedirs(act, exist_ok=True)

    # lo que ya estaba publicado: huella -> dónde está
    ya = {}
    for d in sorted(os.listdir(act)):
        if d.startswith('v') and os.path.isdir(os.path.join(act, d)):
            for n in os.listdir(os.path.join(act, d)):
                ya[(n, huella(os.path.join(act, d, n)))] = f'{d}/{n}'
    # si el exe cambió, tiene que cambiar su versión (si no, la FRIDAY.exe nueva no toma el lugar de la vieja)
    prev = os.path.join(act, 'friday.json')
    if os.path.exists(prev):
        viejo = json.loads(base64.b64decode(json.load(open(prev))['datos']))
        h_exe = huella(os.path.join(fri, 'FRIDAY.exe'))
        ant = {a['nombre']: a['sha256'] for a in viejo['archivos']}
        if ant.get('FRIDAY.exe') and ant['FRIDAY.exe'] != h_exe and viejo['exe'] == exe:
            sys.exit(f'FRIDAY.exe cambió pero sigue diciendo {exe}: subí appVersion')
        tup = lambda v: tuple(int(x) for x in str(v).split('.'))
        if tup(viejo.get('completa') or viejo['version']) > tup(ver):
            sys.exit('esa versión es más vieja que la publicada')

    archivos, nuevos = [], 0
    for n in ARCHIVOS:
        p = os.path.join(fri, n)
        if not os.path.exists(p):
            continue
        h = huella(p)
        rel = ya.get((n, h))
        if not rel:
            rel = f'v{ver}/{n}'
            os.makedirs(os.path.join(act, f'v{ver}'), exist_ok=True)
            shutil.copy2(p, os.path.join(act, rel))
            nuevos += 1
        archivos.append({'nombre': n, 'url': rel, 'sha256': h, 'bytes': os.path.getsize(p)})

    datos = {'producto': 'FRIDAY PC', 'version': grande, 'completa': ver, 'exe': exe, 'fecha': __import__('datetime').date.today().isoformat(),
             'titulo': nov.get('titulo', ''), 'novedades': nov.get('items', []), 'archivos': archivos}
    k = Ed25519PrivateKey.from_private_bytes(base64.b64decode(open(clave).read().strip()))
    b = json.dumps(datos, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    with open(prev, 'w') as f:
        json.dump({'datos': base64.b64encode(b).decode(), 'firma': base64.b64encode(k.sign(b)).decode()}, f, indent=1)

    # la descarga completa, para instalarla de cero
    leeme = os.path.join(sitio, 'descargas', 'LEEME.txt')
    zp = os.path.join(sitio, 'descargas', 'FRIDAY.zip')
    with zipfile.ZipFile(zp + '.nuevo', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(zipfile.ZipInfo('FRIDAY/'), '')
        if os.path.exists(leeme):
            z.write(leeme, 'FRIDAY/LEEME.txt')
        for n in EN_EL_ZIP:
            p = os.path.join(fri, n)
            if os.path.exists(p):
                z.write(p, 'FRIDAY/' + n)
    os.replace(zp + '.nuevo', zp)
    print(f'Publicada la {ver} (FRIDAY.exe {exe}): {len(archivos)} archivos, {nuevos} nuevos.')


if __name__ == '__main__':
    main(*sys.argv[1:4])
