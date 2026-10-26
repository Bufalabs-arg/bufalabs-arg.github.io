#!/usr/bin/env python3
"""Publica una versión de FRIDAY para la compu (Windows y Linux) en la página de BufaLabs.

Para cada sistema arma su aviso firmado (actualizaciones/friday.json para Windows,
actualizaciones/friday-linux.json para Linux) y copia a actualizaciones/v<versión>/ solo los archivos
que cambiaron (los que quedaron igual apuntan a la versión donde ya estaban). También rehace las
descargas completas (descargas/FRIDAY-Setup.exe, descargas/FRIDAY.zip y descargas/FRIDAY-linux.tar.gz).
Antes, compilá todo con codigo-exe/compilar.sh (FRIDAY.exe, friday de Linux y FRIDAY-Setup.exe).

Uso: python3 publicar_pc.py <carpeta de FRIDAY> <repo de la página> <archivo con la clave privada> [windows,linux]
La carpeta de FRIDAY tiene friday.html, FRIDAY.exe, codigo-exe/ y linux/ (friday, friday.png, instalar.sh, LEEME.txt).
"""
import base64, datetime, hashlib, io, json, os, re, shutil, sys, tarfile, zipfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SISTEMAS = {
    'windows': {
        'manifiesto': 'friday.json', 'exe': 'FRIDAY.exe',
        # nombre publicado -> dónde está, relativo a la carpeta de FRIDAY
        'archivos': {'friday.html': 'friday.html', 'FRIDAY.exe': 'FRIDAY.exe', 'bufalabs.ico': 'bufalabs.ico', 'friday.ico': 'friday.ico',
                     'INSTALAR-FRIDAY.bat': 'INSTALAR-FRIDAY.bat', 'instalar-voz.bat': 'instalar-voz.bat',
                     'presentacion-friday.html': 'presentacion-friday.html', 'LEEME-EXE.txt': 'LEEME-EXE.txt'},
        'descarga': ['FRIDAY.exe', 'friday.html', 'bufalabs.ico', 'friday.ico', 'INSTALAR-FRIDAY.bat', 'instalar-voz.bat'],
    },
    'linux': {
        'manifiesto': 'friday-linux.json', 'exe': 'friday',
        'archivos': {'friday.html': 'friday.html', 'friday': 'linux/friday', 'friday.png': 'linux/friday.png', 'instalar.sh': 'linux/instalar.sh'},
        'descarga': ['friday', 'friday.html', 'friday.png', 'instalar.sh'],
    },
}


def huella(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def tup(v):
    return tuple(int(x) for x in str(v).split('.'))


def publicar(sis, fri, sitio, firmar, ver, grande, exe, nov, ya):
    cfg = SISTEMAS[sis]
    act = os.path.join(sitio, 'actualizaciones')
    prev = os.path.join(act, cfg['manifiesto'])
    if os.path.exists(prev):
        viejo = json.loads(base64.b64decode(json.load(open(prev))['datos']))
        ant = {a['nombre']: a['sha256'] for a in viejo['archivos']}
        h_exe = huella(os.path.join(fri, cfg['archivos'][cfg['exe']]))
        if ant.get(cfg['exe']) and ant[cfg['exe']] != h_exe and viejo['exe'] == exe:
            sys.exit(f"{cfg['exe']} cambió pero sigue diciendo {exe}: subí appVersion")
        if tup(viejo.get('completa') or viejo['version']) > tup(ver):
            sys.exit(f'{sis}: esa versión es más vieja que la publicada')

    archivos, nuevos = [], 0
    for n, rel_src in cfg['archivos'].items():
        p = os.path.join(fri, rel_src)
        if not os.path.exists(p):
            if n == cfg['exe']:
                sys.exit(f'falta {p}')
            continue
        h = huella(p)
        rel = ya.get((n, h))
        if not rel:
            rel = f'v{ver}/{n}'
            os.makedirs(os.path.join(act, f'v{ver}'), exist_ok=True)
            shutil.copy2(p, os.path.join(act, rel))
            ya[(n, h)] = rel
            nuevos += 1
        archivos.append({'nombre': n, 'url': rel, 'sha256': h, 'bytes': os.path.getsize(p)})

    datos = {'producto': 'FRIDAY PC', 'sistema': sis, 'version': grande, 'completa': ver, 'exe': exe,
             'fecha': datetime.date.today().isoformat(), 'titulo': nov.get('titulo', ''), 'novedades': nov.get('items', []), 'archivos': archivos}
    b = json.dumps(datos, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    with open(prev, 'w') as f:
        json.dump({'datos': base64.b64encode(b).decode(), 'firma': base64.b64encode(firmar(b)).decode()}, f, indent=1)

    # la descarga completa, para instalarla de cero
    desc = os.path.join(sitio, 'descargas')
    os.makedirs(desc, exist_ok=True)
    if sis == 'windows':
        leeme = os.path.join(desc, 'LEEME.txt')
        zp = os.path.join(desc, 'FRIDAY.zip')
        with zipfile.ZipFile(zp + '.nuevo', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            z.writestr(zipfile.ZipInfo('FRIDAY/'), '')
            if os.path.exists(leeme):
                z.write(leeme, 'FRIDAY/LEEME.txt')
            for n in cfg['descarga']:
                p = os.path.join(fri, cfg['archivos'][n])
                if os.path.exists(p):
                    z.write(p, 'FRIDAY/' + n)
        os.replace(zp + '.nuevo', zp)
        # el instalador de un solo archivo (FRIDAY-Setup.exe), si está compilado con esta misma versión
        setup = os.path.join(fri, 'FRIDAY-Setup.exe')
        carga = os.path.join(fri, 'codigo-exe', 'setup', 'payload.zip')
        if os.path.exists(setup):
            with zipfile.ZipFile(carga) as z:
                adentro = re.search(r"const FRIDAY_VER\s*=\s*'([\d.]+)'", z.read('friday.html').decode('utf-8')).group(1)
                h_exe = hashlib.sha256(z.read('FRIDAY.exe')).hexdigest()
            if adentro != ver or h_exe != huella(os.path.join(fri, 'FRIDAY.exe')):
                sys.exit(f'FRIDAY-Setup.exe lleva la {adentro} (u otro FRIDAY.exe): recompilalo con compilar.sh')
            if os.path.getmtime(setup) < os.path.getmtime(carga):
                sys.exit('FRIDAY-Setup.exe es más viejo que su payload.zip: recompilalo con compilar.sh')
            shutil.copy2(setup, os.path.join(desc, 'FRIDAY-Setup.exe'))
            print(f'windows: FRIDAY-Setup.exe ({os.path.getsize(setup) // 1048576} MB) en descargas.')
    else:
        tp = os.path.join(desc, 'FRIDAY-linux.tar.gz')
        with tarfile.open(tp + '.nuevo', 'w:gz', compresslevel=9) as t:
            def meter(src, nombre, modo):
                ti = t.gettarinfo(src, 'FRIDAY/' + nombre)
                ti.mode, ti.uid, ti.gid, ti.uname, ti.gname = modo, 0, 0, '', ''
                with open(src, 'rb') as f:
                    t.addfile(ti, f)
            d = tarfile.TarInfo('FRIDAY')
            d.type, d.mode, d.mtime = tarfile.DIRTYPE, 0o755, int(datetime.datetime.now().timestamp())
            t.addfile(d)
            for n in cfg['descarga']:
                meter(os.path.join(fri, cfg['archivos'][n]), n, 0o755 if n in ('friday', 'instalar.sh') else 0o644)
            leeme = os.path.join(fri, 'linux', 'LEEME.txt')
            if os.path.exists(leeme):
                meter(leeme, 'LEEME.txt', 0o644)
        os.replace(tp + '.nuevo', tp)
    print(f'{sis}: publicada la {ver} ({cfg["exe"]} {exe}): {len(archivos)} archivos, {nuevos} nuevos.')


def main(fri, sitio, clave, sistemas='windows,linux'):
    html = open(os.path.join(fri, 'friday.html'), encoding='utf-8').read()
    ver = re.search(r"const FRIDAY_VER\s*=\s*'(\d+(?:\.\d+)?)'", html).group(1)   # "101.02"
    grande = ver.split('.')[0]                                                    # "101" (lo que entienden las FRIDAY viejas)
    nov = json.loads(re.search(r'const NOVEDADES=(\{.*?\});\n', html).group(1))
    assert nov['version'] == ver, 'NOVEDADES no es de esta versión'
    exe = re.search(r'appVersion\s*=\s*"([\d.]+)"', open(os.path.join(fri, 'codigo-exe', 'main.go')).read()).group(1)
    act = os.path.join(sitio, 'actualizaciones')
    os.makedirs(act, exist_ok=True)
    k = Ed25519PrivateKey.from_private_bytes(base64.b64decode(open(clave).read().strip()))
    # lo que ya estaba publicado: (nombre, huella) -> dónde está
    ya = {}
    for d in sorted(os.listdir(act)):
        if d.startswith('v') and os.path.isdir(os.path.join(act, d)):
            for n in os.listdir(os.path.join(act, d)):
                ya.setdefault((n, huella(os.path.join(act, d, n))), f'{d}/{n}')
    for sis in sistemas.split(','):
        publicar(sis.strip(), fri, sitio, k.sign, ver, grande, exe, nov, ya)


if __name__ == '__main__':
    main(*sys.argv[1:5])
