# GeoCat IA — Sistema Multiagente de Catastro y Geodesia



## Descripción del proyecto



GeoCat IA es un sistema multiagente desarrollado en Python que utiliza modelos de inteligencia artificial locales mediante Ollama y Qwen.



Su objetivo es responder consultas técnicas relacionadas con Catastro y Geodesia en Colombia, utilizando agentes especializados y documentos de referencia.



## Arquitectura del sistema



El proyecto cuenta con tres componentes principales:



**1. Coordinador:** analiza la pregunta y determina qué especialistas deben intervenir.



**2. Agente Catastro:** atiende consultas sobre Zonas Homogéneas Físicas y Geoeconómicas, identificación predial, avalúos y gestión catastral.



**3. Agente Geodesia:** responde preguntas sobre MAGNA-SIRGAS, sistemas de referencia, coordenadas y proyecciones cartográficas.



Cuando una pregunta requiere ambas especialidades, el sistema consulta a los dos agentes y presenta una síntesis interdisciplinaria.



## Tecnologías utilizadas



- Python 3.9 o superior.

- Ollama para ejecutar modelos locales.

- Qwen como modelo de lenguaje.

- OpenCode para configurar y utilizar agentes especializados.

- Documentos técnicos de referencia.

- GitHub para almacenar y compartir el proyecto.



## Funcionamiento



1. El usuario introduce una pregunta.

2. El Coordinador clasifica la consulta.

3. Se seleccionan los especialistas correspondientes.

4. Los agentes generan respuestas utilizando Qwen y documentos técnicos disponibles.

5. Un validador comprueba errores conocidos.

6. Cuando se detecta un error, el sistema realiza un intento de autocorrección.

7. Se presenta la respuesta aprobada o se informa si fue bloqueada.



La validación automática no garantiza la exactitud factual completa de las respuestas.



## Instalación y ejecución



### 1. Descargar el proyecto



Descargar el repositorio de GitHub y descomprimirlo.



### 2. Instalar Python y Ollama



Instalar Python y Ollama en el computador.



### 3. Descargar los modelos



Ejecutar en una terminal:



```bash

ollama pull qwen3:4b

ollama pull qwen2.5:3b

```



### 4. Instalar las dependencias



Desde la carpeta del proyecto:



```bash

python -m pip install -r requirements.txt

```



### 5. Ejecutar el sistema



```bash

python sistema_multiagente.py

```



También se puede realizar una consulta directamente:



```bash

python sistema_multiagente.py --pregunta "¿Qué es MAGNA-SIRGAS?"

```



### 6. Ejecutar las pruebas



```bash

python sistema_multiagente.py --test

```



## Estructura principal



```text

GeoCat_IA_Entrega/

├── .opencode/

│   └── agents/

│       ├── coordinador.md

│       ├── catastro.md

│       └── geodesia.md

├── documentos/

│   ├── catastro/

│   └── geodesia/

├── sistema_multiagente.py

├── descargar_documentos.py

├── opencode.json

├── requirements.txt

└── README.md

```



## Consideraciones



GeoCat IA utiliza modelos locales. Por tanto, para ejecutar el sistema desde el repositorio es necesario instalar las dependencias y descargar los modelos correspondientes.



El repositorio permite consultar el código, revisar la arquitectura multiagente y reproducir las pruebas.



**Proyecto académico — Ingeniería Catastral y Geodesia.**

**Elaborado por Nikole Flórez y Diana Avendaño**




