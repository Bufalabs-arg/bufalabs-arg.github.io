# Arma en la página la lista de actualizaciones para el público (desde novedades.json)
# y el aviso de la última en el inicio.
import json
import html

MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
       'septiembre', 'octubre', 'noviembre', 'diciembre']
APP = {'compu': 'Compu', 'celu': 'Celu', 'casa': 'Tablet'}
e = html.escape


def fecha(f):
    a, m, d = f.split('-')
    return f'{int(d)} de {MES[int(m) - 1]}'


def render(s, archivo='/home/claude/bufalabs-site/novedades.json'):
    N = json.load(open(archivo, encoding='utf-8'))
    for n in N:
        assert n['app'] in APP, n
    lis = []
    for i, n in enumerate(N):
        cuerpo = f'<h3>{e(n["titulo"])}</h3>'
        if n.get('resumen'):
            cuerpo += f'<p>{e(n["resumen"])}</p>'
        if n.get('items'):
            cuerpo += '<ul>' + ''.join(f'<li><b>{e(t)}.</b> {e(x)}</li>' for t, x in n['items']) + '</ul>'
        clase = ' class="ultima"' if i == 0 else ''
        meta = (f'<span class="ver">{e(n["version"])}</span><span class="app {n["app"]}">{APP[n["app"]]}</span>'
                f'<time datetime="{n["fecha"]}">{fecha(n["fecha"])}</time>')
        lis.append(f'          <li{clase} data-app="{n["app"]}"><div class="vn">{meta}</div><div class="min0">{cuerpo}</div></li>')
    bloque = (
        '      <div class="hist" id="actualizaciones">\n'
        '        <h2 class="titulo oculto">Todas las actualizaciones</h2>\n'
        '        <div class="filtros" aria-label="Mostrar"><button class="on" data-f="" aria-pressed="true">Todas</button>'
        '<button data-f="compu" aria-pressed="false">Compu</button><button data-f="celu" aria-pressed="false">Celu</button>'
        '<button data-f="casa" aria-pressed="false">Tablet</button></div>\n'
        '        <ol class="vlista" id="vlista">\n' + '\n'.join(lis) + '\n        </ol>\n      </div>\n')
    assert s.count('<!--ACTUALIZACIONES-->\n') == 1 and s.count('<!--ULTIMA-->') == 1
    s = s.replace('<!--ACTUALIZACIONES-->\n', bloque)
    u = N[0]
    corta = u['version'].replace('Móvil ', '').replace('Casa ', '')
    s = s.replace('<!--ULTIMA-->', f'<a class="ultimo" href="#actualizaciones"><b>Nuevo</b>'
                                   f'<span>{e(u["titulo"])} · {APP[u["app"]]} {e(corta)}</span></a>')
    return s
