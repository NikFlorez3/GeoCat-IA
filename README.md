# GeoCat IA — Sistema Multiagente de Catastro y Geodesia

**Proyecto académico de Ingeniería Catastral y Geodesia**

**Desarrollado por:** Nikole Flórez y Diana Avendaño

## 1. Descripción del proyecto

GeoCat IA es un sistema multiagente de inteligencia artificial orientado a responder consultas técnicas relacionadas con Catastro y Geodesia en Colombia.

El proyecto utiliza modelos de lenguaje Qwen ejecutados localmente mediante Ollama, configuraciones de agentes en OpenCode y una implementación funcional en Python.

Su propósito es explorar cómo diferentes agentes especializados pueden colaborar para resolver preguntas técnicas, consultar documentos de referencia y generar respuestas que integren conocimientos de ambas disciplinas.

## 2. Objetivo

Desarrollar y evaluar un sistema multiagente con un Coordinador y dos agentes especializados en Catastro y Geodesia, utilizando herramientas de inteligencia artificial local para apoyar la consulta y el análisis de información técnica.

## 3. Arquitectura del sistema

El sistema contempla tres agentes principales.

### Agente Coordinador

Es el encargado de analizar la pregunta del usuario e identificar qué especialidad debe intervenir.

En la implementación Python, esta clasificación se realiza mediante reglas auditables.

### Agente Catastro

Atiende consultas relacionadas con:

- Zonas Homogéneas Físicas (ZHF).
- Zonas Homogéneas Geoeconómicas (ZHG).
- Identificación predial.
- Avalúos y valoración catastral.
- Información física y económica del territorio.

### Agente Geodesia

Atiende consultas relacionadas con:

- MAGNA-SIRGAS.
- Sistemas de referencia geodésicos.
- Sistemas de coordenadas.
- Proyecciones cartográficas.
- MAGNA-SIRGAS / Origen-Nacional (EPSG:9377).

Cuando una pregunta involucra ambas disciplinas, la implementación Python consulta los dos especialistas y genera una síntesis interdisciplinaria mediante una regla explícita.

## 4. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Python | Implementación del sistema multiagente funcional |
| Ollama | Ejecución local de los modelos de lenguaje |
| Qwen | Generación de respuestas mediante inteligencia artificial |
| OpenCode | Configuración de un agente principal y dos subagentes especializados |
| PyPDF | Lectura y recuperación de información de documentos PDF |
| GitHub | Publicación del código y documentación |

### Modelos utilizados

- `qwen3:4b`
- `qwen2.5:3b`
- `qwen2.5:7b`

Los modelos deben descargarse mediante Ollama. No están incluidos directamente en el repositorio.

## 5. Implementaciones del proyecto

### 5.1. Agentes configurados en OpenCode

Se desarrollaron las configuraciones correspondientes al Coordinador y a los dos especialistas.

Los archivos se encuentran en:

```text
.opencode/
└── agents/
    ├── coordinador.md
    ├── catastro.md
    └── geodesia.md
```

El archivo `opencode.json` contiene la configuración del proveedor Ollama y los modelos asignados.

Durante el desarrollo se realizaron pruebas de interacción con OpenCode y consultas directas a agentes especializados. También se identificaron dificultades en la delegación mediante herramientas de subagentes.

Por ello, la delegación automática entre los subagentes nativos de OpenCode no se presenta como una funcionalidad completamente validada.

### 5.2. Sistema multiagente en Python

Se desarrolló una implementación independiente en Python, conectada directamente con Ollama, que permite:

1. Recibir preguntas del usuario.
2. Clasificar las consultas mediante reglas.
3. Seleccionar Catastro, Geodesia o ambos.
4. Recuperar información de documentos locales.
5. Generar respuestas con modelos Qwen.
6. Detectar determinados errores conocidos mediante un validador.
7. Intentar una corrección cuando se identifica un error.
8. Presentar las respuestas y, cuando corresponde, una síntesis interdisciplinaria.

**Importante:** el programa Python no invoca directamente los subagentes nativos de OpenCode. Ambas implementaciones forman parte del mismo proyecto académico, pero tienen mecanismos de ejecución diferentes.

## 6. Instalación del sistema Python

### Paso 1. Descargar el repositorio

Acceder a:

https://github.com/NikFlorez3/GeoCat-IA

Seleccionar **Code → Download ZIP**, descargar el archivo y descomprimirlo.

### Paso 2. Instalar Python

Instalar Python desde:

https://www.python.org/downloads/

Se recomienda utilizar Python 3.11, versión empleada durante el desarrollo.

### Paso 3. Instalar Ollama

Descargar Ollama desde:

https://ollama.com/download

Una vez instalado, comprobar que el servicio esté funcionando.

### Paso 4. Instalar las dependencias y modelos

En Windows, abrir la carpeta del proyecto y ejecutar:

```bat
instalar.bat
```

Este archivo comprueba la disponibilidad de Python y Ollama, instala las dependencias de Python y descarga los modelos Qwen necesarios.

También es posible descargar los modelos manualmente:

```powershell
ollama pull qwen3:4b
ollama pull qwen2.5:3b
ollama pull qwen2.5:7b
```

**Nota:** la descarga de modelos requiere conexión a internet y suficiente espacio de almacenamiento.

### Paso 5. Ejecutar GeoCat IA

Abrir:

```bat
iniciar.bat
```

El programa mostrará una terminal donde se podrán introducir preguntas.

También puede ejecutarse manualmente:

```powershell
python sistema_multiagente.py
```

### Paso 6. Realizar una consulta

Por ejemplo:

```text
Tu pregunta: ¿Qué es MAGNA-SIRGAS?
```

El Coordinador clasificará la pregunta y seleccionará el agente correspondiente.

Para finalizar la sesión, escribir:

```text
salir
```

## 7. Ejecución de los agentes en OpenCode

Para utilizar las configuraciones nativas de OpenCode se requiere instalar OpenCode y disponer de Ollama con los modelos correspondientes.

1. Instalar OpenCode desde https://opencode.ai.
2. Descargar los modelos Qwen indicados anteriormente.
3. Abrir una terminal dentro de la carpeta del proyecto.
4. Ejecutar:

```powershell
opencode
```

5. Revisar la configuración del Coordinador y los especialistas disponibles.

Esta modalidad es independiente de `sistema_multiagente.py`. La disponibilidad de las herramientas de delegación depende de la configuración y versión de OpenCode.

## 8. Pruebas de funcionamiento

Se realizaron pruebas locales para evaluar la ejecución del sistema Python.

### Prueba 1. Consulta de Geodesia

**Pregunta:** ¿Qué es MAGNA-SIRGAS y en qué se diferencia de EPSG:9377?

**Resultado:**

- Agente seleccionado: Geodesia.
- Documentos consultados: dos.
- Tiempo de ejecución: 14,45 segundos.
- Respuesta generada correctamente.
- Validador sin errores conocidos.

### Prueba 2. Consulta de Catastro

**Pregunta:** ¿Qué son las Zonas Homogéneas Físicas y Geoeconómicas y cuál es su importancia en los avalúos catastrales?

**Resultado:**

- Agente seleccionado: Catastro.
- Documento consultado: PDF técnico del IGAC.
- Tiempo de ejecución: 12,19 segundos.
- Respuesta generada correctamente.

Durante la revisión se identificó una afirmación incorrecta relacionada con tasas tributarias que no fue detectada por el validador. Esto evidencia una limitación de la verificación automática.

### Prueba 3. Consulta interdisciplinaria

**Pregunta:** ¿Cómo se relaciona MAGNA-SIRGAS / Origen-Nacional EPSG:9377 con la delimitación de Zonas Homogéneas Físicas y Geoeconómicas?

**Resultado:**

- Agentes seleccionados: Catastro y Geodesia.
- Documentos utilizados: tres.
- Tiempo total: 15,24 segundos.
- Respuestas de ambos especialistas generadas correctamente.
- Síntesis interdisciplinaria presentada.

### Verificaciones internas

Se ejecutó:

```powershell
python sistema_multiagente.py --test
```

**Resultado:** 11 verificaciones básicas superadas.

Estas verificaciones comprueban aspectos del funcionamiento del programa, pero no garantizan la exactitud factual de todas las respuestas generadas.

## 9. Estructura del repositorio

```text
GeoCat-IA/
├── .opencode/
│   └── agents/
│       ├── catastro.md
│       ├── coordinador.md
│       └── geodesia.md
├── documentos/
│   ├── catastro/
│   └── geodesia/
├── .gitignore
├── FUENTES_OFICIALES.json
├── LEEME.txt
├── README.md
├── descargar_documentos.py
├── index.html
├── iniciar.bat
├── instalar.bat
├── opencode.json
├── requirements.txt
└── sistema_multiagente.py
```

## 10. Limitaciones del proyecto

GeoCat IA es un prototipo académico y presenta algunas limitaciones:

- Las respuestas generadas por Qwen pueden contener errores conceptuales.
- El validador detecta determinados errores conocidos, pero no realiza una verificación factual completa.
- Los documentos locales se utilizan como contexto y deben contrastarse con las fuentes oficiales vigentes.
- La ejecución depende de los recursos disponibles en el computador.
- La delegación nativa de subagentes en OpenCode no está completamente validada.
- La instalación completa en un computador diferente al utilizado durante el desarrollo todavía no ha sido comprobada.

## 11. Conclusiones

El proyecto permitió desarrollar y probar una arquitectura multiagente orientada a dos áreas de la Ingeniería Catastral y Geodesia.

Las pruebas de la implementación Python demostraron que el Coordinador puede identificar la especialidad requerida, seleccionar uno o ambos agentes y generar respuestas a partir de modelos locales y documentos técnicos.

La experiencia también permitió reconocer desafíos relacionados con la coordinación de agentes, la calidad de las respuestas y la necesidad de validar la información generada por inteligencia artificial.

**GeoCat IA constituye una aproximación académica al uso de sistemas multiagente como apoyo para la consulta de información técnica catastral y geodésica.**

---


**Proyecto académico — Ingeniería Catastral y Geodesia, 2026.**