"""Descarga PDF de enlaces oficiales directos; no inventa ni simula descargas."""
import json
import urllib.request
from pathlib import Path
BASE = Path(__file__).resolve().parent
fuentes = json.loads((BASE/'FUENTES_OFICIALES.json').read_text(encoding='utf-8'))
for fuente in fuentes:
    destino = BASE/'documentos'/fuente['especialidad']/fuente['archivo']
    if fuente.get('descarga_automatica') is False:
        print('MANUAL:', fuente['titulo'], '->', fuente['url'])
        continue
    if destino.exists() and destino.stat().st_size > 1000:
        print('YA EXISTE:', destino)
        continue
    print('Descargando:', fuente['titulo'])
    try:
        req = urllib.request.Request(fuente['url'], headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=35) as resp:
            datos = resp.read(35_000_001)
        if len(datos) > 35_000_000 or not datos.startswith(b'%PDF-'):
            print('NO DESCARGADO: el servidor no devolvio un PDF valido.')
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(datos)
        print('OK:', destino.name, len(datos), 'bytes')
    except Exception as e:
        print('NO DESCARGADO:', type(e).__name__, str(e))
print('Fin. Los PDF no descargados pueden guardarse manualmente en las carpetas indicadas.')
