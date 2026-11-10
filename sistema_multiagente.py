"""Sistema multiagente local de Catastro y Geodesia (Ollama). Python >= 3.9."""
import argparse
import json
import re
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BASE = RAIZ / 'documentos'
URL_OLLAMA = 'http://127.0.0.1:11434/api/chat'
COORDINADOR = 'qwen3:4b'
ESPECIALISTA = 'qwen2.5:3b'
MAX_FRAGMENTOS = 3

CAT = ('catastro', 'catastral', 'predio', 'predial', 'parcela', 'avaluo',
       'zhf', 'zhg', 'zhge', 'homogenea', 'homogeneas', 'geoeconomica',
       'geoeconomicas', 'fisicas', 'impuesto predial', 'lindero',
       'terreno', 'propiedad inmueble', 'mercado inmobiliario', 'valoracion')
GEO = ('magna', 'sirgas', 'geodesia', 'geodesico', 'coordenada', 'gnss',
       'gps', 'datum', 'epsg', 'proyeccion', 'elipsoide',
       'georreferenciacion', 'transformacion de coordenadas',
       'levantamiento geodesico')

BASE_TECNICA = {
    'catastro': (
        'Las ZHF agrupan sectores del territorio con caracteristicas fisicas '
        'similares relevantes para estudios catastrales; no identifican por si '
        'mismas predios individuales. Las ZHG se relacionan con valores '
        'unitarios de terreno similares derivados de estudios economicos. '
        'Estos estudios son insumos de valoracion, no establecen tasas '
        'tributarias. Identificacion predial y avaluo son procesos diferentes. '
        'Las coordenadas localizan predios, pero no determinan su valor.'
    ),
    'geodesia': (
        'MAGNA-SIRGAS es un marco geodesico de referencia utilizado en Colombia. '
        'MAGNA-SIRGAS / Origen-Nacional (EPSG:9377) es un sistema de referencia '
        'de coordenadas proyectadas, basado en la proyeccion Transversa de '
        'Mercator, con coordenadas planas expresadas en metros. '
        'MAGNA-SIRGAS y EPSG:9377 no son sinonimos. '
        'La localizacion espacial ayuda a identificar predios, pero las '
        'coordenadas no determinan su valor economico. '
        'No inventes parametros de transformacion.'
    )
}


def normalizar(texto):
    texto = unicodedata.normalize('NFKD', str(texto))
    return ''.join(c for c in texto if not unicodedata.combining(c)).lower()


def coincide(texto, clave):
    clave = normalizar(clave)
    return bool(re.search(r'(?<![a-z0-9])' + re.escape(clave) + r'(?:[a-z0-9]*)?(?![a-z0-9])', texto))


def indicios(pregunta):
    t = normalizar(pregunta)
    return [a for a, claves in (('catastro', CAT), ('geodesia', GEO))
            if any(coincide(t, c) for c in claves)]


def extraer_json(texto):
    inicio = texto.find('{')
    if inicio < 0:
        raise ValueError('No se encontro un objeto JSON')
    obj, _ = json.JSONDecoder().raw_decode(texto[inicio:])
    return obj


def ollama(modelo, sistema, pregunta, json_mode=False):
    datos = {
        'model': modelo,
        'stream': False,
        'messages': [
            {'role': 'system', 'content': sistema},
            {'role': 'user', 'content': pregunta}
        ],
        'options': {'temperature': 0.1, 'num_predict': 550}
    }
    if json_mode:
        datos['format'] = 'json'
    solicitud = urllib.request.Request(
        URL_OLLAMA, data=json.dumps(datos).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST'
    )
    with urllib.request.urlopen(solicitud, timeout=240) as respuesta:
        cuerpo = json.loads(respuesta.read().decode('utf-8'))
    contenido = cuerpo.get('message', {}).get('content', '').strip()
    if not contenido:
        raise ValueError('Ollama devolvio una respuesta vacia')
    return contenido


def seleccionar(pregunta, consulta=ollama):
    pistas = indicios(pregunta)
    if pistas:
        return pistas, 'Reglas de pertinencia verificables', False
    sistema = (
        'Eres coordinador de dos especialistas: catastro (predios, avaluos, '
        'gestion catastral) y geodesia (referencias, GNSS, proyecciones). '
        'Selecciona solo los necesarios. Responde exclusivamente JSON '
        '{"agentes":["catastro"],"motivo":"..."}. '
        'Usa ambos solo si son necesarios; si el tema es ajeno usa [].'
    )
    try:
        obj = extraer_json(consulta(COORDINADOR, sistema, pregunta, True))
        if not isinstance(obj, dict) or not isinstance(obj.get('agentes'), list):
            raise ValueError('Estructura JSON inesperada')
        agentes = [a for a in ('catastro', 'geodesia') if a in obj['agentes']]
        return agentes, str(obj.get('motivo', 'Seleccion IA')), True
    except (ValueError, KeyError, urllib.error.URLError, TimeoutError) as e:
        print('[Coordinador] No fue posible interpretar la seleccion:', e)
        return [], 'Seleccion no disponible', True


def fragmentar(texto, max_chars=850):
    parrafos = [p.strip() for p in re.split(r'\n\s*\n', texto) if p.strip()]
    salida = []
    for p in parrafos:
        while len(p) > max_chars:
            corte = p.rfind(' ', 0, max_chars)
            if corte < max_chars // 2:
                corte = max_chars
            salida.append(p[:corte].strip())
            p = p[corte:].strip()
        if p:
            salida.append(p)
    return salida


def documentos(pregunta, agente):
    """Recupera fragmentos de TXT y PDF descargados localmente."""
    carpeta = BASE / agente
    if not carpeta.is_dir():
        return []
    stop = {'que', 'como', 'para', 'con', 'los', 'las', 'del', 'una', 'uno',
            'son', 'por', 'sus', 'en', 'de', 'el', 'la', 'y', 'se', 'un', 'al', 'es'}
    terminos = {w for w in re.findall(r'[a-z0-9]+', normalizar(pregunta))
                if len(w) > 2 and w not in stop}
    candidatos = []
    rutas = sorted(carpeta.glob('*.txt')) + sorted(carpeta.glob('*.pdf'))
    for ruta in rutas:
        try:
            if ruta.suffix.lower() == '.pdf':
                try:
                    from pypdf import PdfReader
                except ImportError:
                    print('[DOCUMENTOS] Para leer PDF: python -m pip install pypdf')
                    continue
                reader = PdfReader(str(ruta))
                bloques = [(i + 1, (pagina.extract_text() or '')[:20000])
                           for i, pagina in enumerate(reader.pages)]
            else:
                contenido = ruta.read_text(encoding='utf-8')
                bloques = [(i, parte) for i, parte in enumerate(fragmentar(contenido), 1)]
        except Exception as error:
            print('[DOCUMENTOS] No se pudo leer', ruta.name, ':', error)
            continue
        for num, bloque in bloques:
            for frag in fragmentar(bloque):
                palabras = set(re.findall(r'[a-z0-9]+', normalizar(frag)))
                puntos = len(terminos & palabras)
                if puntos:
                    puntos += 0.25 if ruta.suffix.lower() == '.pdf' else 0
                    candidatos.append((puntos, ruta.name, num, frag))
    candidatos.sort(key=lambda x: (-x[0], x[1], x[2]))
    return candidatos[:MAX_FRAGMENTOS]


def validar(texto, agente):
    t = normalizar(texto)
    errores = []
    if len(t.strip()) < 25:
        errores.append('Respuesta demasiado corta o vacia')
    for sigla in ('zhfmagna', 'zhgmagna', 'zhgemagna'):
        if sigla in t:
            errores.append('Sigla tecnica inventada: ' + sigla)
    patrones = [
        (r'magna.sirgas (?:es|son|corresponde a) (?:un |el )?sistema de coordenadas proyectadas',
         'Confunde marco MAGNA-SIRGAS con sistema proyectado'),
        (r'(?:coordenadas|magna.sirgas).{0,110}no (?:estan|esta|tienen|tiene|guardan|guarda) relacion (?:directa )?con (?:la )?identificacion',
         'Niega relacion espacial con identificacion predial'),
        (r'las? zhf (?:se utilizan para |sirven para )?(?:identificar|delimitar) (?:y )?(?:delimitar )?(?:los )?predios',
         'Confunde zonificacion con identificacion individual'),
        (r'las? zhf (?:se utilizan para |sirven para )?(?:identificar|delimitar) (?:individualmente )?(?:los )?predios',
         'Confunde zonificacion con identificacion predial'),
        (r'(?:las? )?zhg (?:establecen|determinan) (?:las? )?tasas? (?:tributarias?|del impuesto)',
         'Confunde zonas geoeconomicas con tasas tributarias'),
        (r'magna.sirgas no (?:tiene|guarda) relacion con (?:la )?identificacion',
         'Niega relacion espacial de MAGNA-SIRGAS'),
    ]
    for patron, error in patrones:
        if re.search(patron, t):
            errores.append(error)
    return errores


def fuentes_contexto(pasajes):
    return '\n\n'.join(
        f'[DOCUMENTO {nombre}, fragmento/pagina {num}]\n{contenido}'
        for _, nombre, num, contenido in pasajes
    ) or 'No se recuperaron documentos locales.'


def responder_agente(agente, pregunta, consulta=ollama):
    pasajes = documentos(pregunta, agente)
    sistema = (
        f'Eres especialista colombiano en {agente}. Responde en espanol, '
        'con precision y sin inventar. No mezcles competencias. No inventes '
        'leyes, citas, codigos ni parametros. Los documentos son contexto '
        'local y no se han verificado en vivo. Si falta evidencia, dilo. '
        'No afirmes haber consultado paginas oficiales en vivo. '
        'Distingue MAGNA-SIRGAS (marco geodesico) de MAGNA-SIRGAS / '
        'Origen-Nacional EPSG:9377 (sistema proyectado).\n'
        f'BASE TECNICA:\n{BASE_TECNICA[agente]}\n\n'
        f'FRAGMENTOS RECUPERADOS:\n{fuentes_contexto(pasajes)}'
    )
    return consulta(ESPECIALISTA, sistema, pregunta), pasajes


def corregir_respuesta(agente, pregunta, respuesta, errores, pasajes, consulta=ollama):
    """Un solo reintento correctivo; devuelve texto y nuevos errores."""
    instrucciones = (
        f'Eres especialista colombiano en {agente}. '
        'La respuesta anterior fue rechazada. Corrige los errores sin '
        'inventar fuentes, normas, cifras o codigos. '
        'MAGNA-SIRGAS es un marco geodesico, no un sistema proyectado; '
        'MAGNA-SIRGAS / Origen-Nacional (EPSG:9377) es un sistema '
        'de coordenadas proyectadas. Las coordenadas ayudan a ubicar '
        'predios, pero no fijan su valor economico. '
        'Responde directamente la pregunta en espanol, sin comentar '
        'el proceso de correccion.\n'
        f'ERRORES DETECTADOS:\n{chr(10).join("- " + e for e in errores)}\n'
        f'BASE TECNICA:\n{BASE_TECNICA[agente]}\n'
        f'FRAGMENTOS RECUPERADOS:\n{fuentes_contexto(pasajes)}'
    )
    solicitud = (
        f'PREGUNTA ORIGINAL:\n{pregunta}\n\n'
        f'RESPUESTA RECHAZADA:\n{respuesta}\n\n'
        'Redacta una respuesta nueva, corregida y autosuficiente.'
    )
    corregida = consulta(ESPECIALISTA, instrucciones, solicitud)
    return corregida, validar(corregida, agente)


def ejecutar(pregunta, consulta=ollama):
    inicio = time.perf_counter()
    print('\n[Coordinador] Clasificando la pregunta...')
    agentes, motivo, uso_ia = seleccionar(pregunta, consulta)
    print('[Coordinador] Metodo:', 'IA' if uso_ia else 'Reglas auditables')
    print('[Coordinador] Motivo:', motivo)
    print('[Coordinador] Agentes:', agentes)
    if not agentes:
        print('No se pudo asignar la pregunta. Reformula indicando Catastro o Geodesia.')
        return
    aprobados, bloqueados = {}, {}
    for agente in agentes:
        t = time.perf_counter()
        try:
            respuesta, pasajes = responder_agente(agente, pregunta, consulta)
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as error:
            bloqueados[agente] = ['Error de consulta: ' + str(error)]
            print(f'[{agente.upper()}] Error de consulta:', error)
            continue
        nombres = ', '.join(sorted({p[1] for p in pasajes})) if pasajes else 'ninguno'
        print(f'[{agente.upper()}] {time.perf_counter()-t:.2f} s; documentos: {nombres}')
        errores = validar(respuesta, agente)
        if errores:
            print('[VALIDADOR] Errores detectados:', '; '.join(errores))
            print(f'[CORRECTOR] Solicitando una correccion a {agente.upper()}...')
            try:
                corregida, nuevos_errores = corregir_respuesta(
                    agente, pregunta, respuesta, errores, pasajes, consulta
                )
                if nuevos_errores:
                    bloqueados[agente] = nuevos_errores
                    print('[VALIDADOR] BLOQUEADO tras correccion:', '; '.join(nuevos_errores))
                else:
                    aprobados[agente] = (corregida, pasajes)
                    print('[VALIDADOR] Correccion aceptada; no implica verificacion factual completa')
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as error:
                bloqueados[agente] = ['Error durante correccion: ' + str(error)]
                print('[CORRECTOR] Error:', error)
        else:
            aprobados[agente] = (respuesta, pasajes)
            print('[VALIDADOR] Sin errores conocidos (no implica verificacion factual completa)')
    print('\n' + '=' * 55 + '\nRESULTADO FINAL - V5.2 + AUTOCORRECCION\n' + '=' * 55)
    for agente, (respuesta, pasajes) in aprobados.items():
        print(f'\n{agente.upper()}:\n{respuesta}')
        if pasajes:
            print('Documentos locales usados como contexto: ' +
                  ', '.join(sorted({p[1] for p in pasajes})))
    if len(aprobados) == 2:
        print('\nSINTESIS INTERDISCIPLINARIA (REGLA EXPLICITA):')
        print('La geodesia aporta el marco de referencia para ubicar espacialmente los predios;')
        print('el catastro integra esa localizacion con informacion fisica, juridica y economica')
        print('para procesos de identificacion y valoracion. Las coordenadas no determinan')
        print('por si solas el valor de un inmueble.')
        print('Nota: sintesis estandar, no una nueva verificacion automatica por IA.')
    if bloqueados:
        print('\nRespuestas no publicadas:')
        for agente, razones in bloqueados.items():
            print('-', agente + ':', '; '.join(razones))
        if aprobados:
            print('ATENCION: Resultado parcial; falta al menos un especialista.')
    if not aprobados:
        print('ATENCION: Ninguna respuesta supero las verificaciones.')
    print(f'\nTiempo total: {time.perf_counter()-inicio:.2f} s')


def pruebas():
    casos = [
        ('¿Que son las Zonas Homogeneas Fisicas y Geoeconomicas y como se utilizan en los avaluos catastrales?', ['catastro']),
        ('¿Que es MAGNA-SIRGAS y cual es el EPSG de Origen Nacional?', ['geodesia']),
        ('¿Como se relacionan las coordenadas MAGNA-SIRGAS con la identificacion y valoracion de predios?', ['catastro', 'geodesia']),
        ('¿Como se calcula un avaluo catastral?', ['catastro']),
        ('¿Que es un datum geodesico?', ['geodesia'])
    ]
    for pregunta, esperado in casos:
        obtenido, _, _ = seleccionar(pregunta)
        assert obtenido == esperado, (pregunta, obtenido, esperado)
    assert extraer_json('texto {"agentes":["catastro"]} resto')['agentes'] == ['catastro']
    assert validar('Las ZHF sirven para identificar predios.', 'catastro')
    assert validar('MAGNA-SIRGAS es un sistema de coordenadas proyectadas.', 'geodesia')
    assert documentos('Que son las zonas homogeneas fisicas y geoeconomicas para avaluos?', 'catastro')
    assert documentos('Que es MAGNA-SIRGAS y EPSG 9377?', 'geodesia')
    # Comprueba que un error conocido active exactamente una correccion.
    llamadas = []
    def simular(modelo, sistema, pregunta, json_mode=False):
        llamadas.append(pregunta)
        if len(llamadas) == 1:
            return 'MAGNA-SIRGAS es un sistema de coordenadas proyectadas utilizado en Colombia.'
        return ('MAGNA-SIRGAS es un marco geodesico de referencia en Colombia. '
                'MAGNA-SIRGAS / Origen-Nacional EPSG:9377 es un sistema proyectado.')
    original = simular(ESPECIALISTA, '', 'pregunta')
    corregida, errores = corregir_respuesta('geodesia', 'pregunta', original,
                                            validar(original, 'geodesia'), [], simular)
    assert not errores and len(llamadas) == 2 and 'marco geodesico' in corregida
    print('11 verificaciones basicas superadas. No prueban exactitud factual del modelo.')


def main():
    parser = argparse.ArgumentParser(
        description='Sistema multiagente Catastro y Geodesia'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Ejecutar verificaciones basicas'
    )

    parser.add_argument(
        '--pregunta',
        type=str,
        help='Pregunta enviada desde OpenCode'
    )

    args = parser.parse_args()

    # Ejecutar las pruebas internas
    if args.test:
        pruebas()
        return

    # Ejecutar una pregunta directamente desde OpenCode
    if args.pregunta is not None:
        pregunta = args.pregunta.strip()

        if not pregunta:
            parser.error('La pregunta no puede estar vacia')

        ejecutar(pregunta)
        return

    # Modo interactivo tradicional
    print(
        'Sistema multiagente local V5.2 + autocorreccion. '
        'Escribe "salir" para terminar.'
    )

    while True:
        try:
            pregunta = input('\nTu pregunta: ').strip()

        except (KeyboardInterrupt, EOFError):
            print('\nHasta luego.')
            break

        if normalizar(pregunta) in ('salir', 'exit', 'quit'):
            break

        if pregunta:
            ejecutar(pregunta)


if __name__ == '__main__':
    main()