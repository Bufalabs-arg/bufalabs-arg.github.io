#!/usr/bin/env python3
"""Copia FRIDAY Móvil a /app/ de este sitio (el espejo que abre la app de Android).

La app de Android (el APK) es una ventana de Chrome sin barra de dirección, y para abrirse así
Android le pide al dominio que diga que esa app es suya (/.well-known/assetlinks.json). Ese
permiso solo vale para el dominio entero, así que la página del celu tiene que vivir también acá.

  python3 herramientas/espejo_movil.py <carpeta de FRIDAY Móvil> [destino]
"""
import filecmp, os, shutil, sys

AFUERA = {'.git', '.github', 'PUBLICAR.txt', 'README.md', 'FRIDAY-movil.zip', 'pruebas'}


def espejar(origen, destino):
    cambios = []
    quedan = set()
    for d, ds, fs in os.walk(origen):
        ds[:] = sorted(x for x in ds if x not in AFUERA and not x.startswith('.'))
        for f in sorted(fs):
            if f in AFUERA or f.startswith('.'):
                continue
            rel = os.path.relpath(os.path.join(d, f), origen)
            quedan.add(rel)
            src, dst = os.path.join(d, f), os.path.join(destino, rel)
            if os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            cambios.append(rel)
    # lo que ya no está en FRIDAY Móvil tampoco queda en el espejo
    for d, ds, fs in os.walk(destino, topdown=False):
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), destino)
            if rel not in quedan:
                os.remove(os.path.join(d, f))
                cambios.append('(borrado) ' + rel)
        if d != destino and not os.listdir(d):
            os.rmdir(d)
    if not os.path.isfile(os.path.join(destino, 'index.html')):
        sys.exit('el espejo quedó sin index.html: algo salió mal')
    return cambios


if __name__ == '__main__':
    origen = sys.argv[1]
    destino = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app')
    # el espejo borra lo que sobra, así que nunca puede apuntar a la raíz del sitio
    if os.path.isdir(os.path.join(destino, '.git')) or os.path.basename(os.path.abspath(destino)) != 'app':
        sys.exit('el destino tiene que ser la carpeta app/ del sitio, no «%s»' % os.path.abspath(destino))
    os.makedirs(destino, exist_ok=True)
    c = espejar(origen, destino)
    print(f'{len(c)} archivos al día' if c else 'ya estaba al día')
    for x in c[:20]:
        print('  ', x)
