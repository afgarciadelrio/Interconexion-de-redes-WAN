# GNS3 AI Studio

Automatización de Topologías de Red en GNS3 Mediante Inteligencia Artificial y Model Context Protocol.

## Autores

- Andrés F. García del Rio
- Jose L. Castro Martín
- Gabriel E. de Hoyos Ozuna

**Ingeniería en Telecomunicaciones — Universidad Compensar, Bogotá, Colombia**

📧 `{afgarciadelrio | jluiscastro | gdehoyos}@ucompensar.edu.co`

---

# Abstract

Este trabajo presenta **GNS3 AI Studio**, una plataforma de inteligencia artificial que automatiza la creación y configuración de topologías de red en GNS3 a partir de descripciones en lenguaje natural.

El sistema integra:

- Model Context Protocol (MCP)
- API de Anthropic Claude Sonnet
- API REST de GNS3
- Backend FastAPI

La solución genera automáticamente:

- Dispositivos
- Enlaces
- Direccionamiento IP
- Protocolos como OSPF

reduciendo el tiempo de despliegue de laboratorios de redes de varias horas a pocos minutos.

---

# Palabras Clave

`GNS3` · `Model Context Protocol` · `Inteligencia Artificial` · `Automatización de Redes` · `OSPF` · `FastAPI` · `Anthropic Claude`

---

# I. INTRODUCCIÓN

La automatización de redes es un elemento fundamental en los entornos modernos de telecomunicaciones. Los laboratorios de simulación permiten validar configuraciones antes de su implementación productiva; sin embargo, la creación manual de topologías complejas en GNS3 requiere conocimientos avanzados y tiempo considerable de configuración.

Con el avance de los modelos de inteligencia artificial generativa y protocolos como **Model Context Protocol (MCP)**, es posible interpretar instrucciones en lenguaje natural y traducirlas en configuraciones técnicas.

En este contexto se desarrolló **GNS3 AI Studio**, orientado a:

- Entornos académicos
- Centros CCNA/CCNP
- Departamentos NOC

---

# II. PROBLEMÁTICA

Una topología OSPF de mediana complejidad puede requerir entre **2 y 4 horas** de configuración manual:

- Creación de proyectos
- Asignación de dispositivos
- Cableado lógico
- Direccionamiento IP
- Configuración de protocolos de enrutamiento

Esta situación limita el aprendizaje acelerado y la validación ágil de escenarios.

Adicionalmente, la curva de aprendizaje de la API REST de GNS3 y los comandos Cisco constituye una barrera para usuarios en formación.

Se identifica la necesidad de una herramienta que traduzca descripciones en lenguaje natural a configuraciones funcionales de forma automática.

---

# III. METODOLOGÍA

El desarrollo se realizó sobre **Ubuntu 24.04 LTS** con **Python 3.12**.

La arquitectura integra cuatro componentes:

- API REST de GNS3 para administración de proyectos y dispositivos
- Model Context Protocol (MCP) como mecanismo de comunicación entre IA y herramientas
- API de Anthropic Claude Sonnet para procesamiento de lenguaje natural
- Backend FastAPI con WebSocket para interacción en tiempo real

Los routers se configuran mediante conexiones Telnet asíncronas con `telnetlib3`.

El servidor MCP expone **14 herramientas funcionales**:

- Creación de proyectos
- Adición de nodos
- Conexión de dispositivos
- Inicio/detención de routers
- Configuración automática de OSPF

La interfaz de usuario sigue un diseño tipo ChatGPT desarrollado en:

- HTML
- CSS
- JavaScript

---

## A. Herramientas MCP

`El MCP fue creado e implementado de forma original, no se encuentra en ningun repositorio publico aparte de este`

Las 14 herramientas expuestas vía JSONSchema cubren:

- `listar_proyectos`
- `listar_nodos`
- `crear_proyecto`
- `eliminar_proyecto`
- `agregar_nodo`
- `conectar_nodos`
- `iniciar_nodos`
- `detener_nodos`
- `configurar_router`
- `ejecutar_comandos`
- `crear_lan_simple`
- `crear_topologia_hub_spoke`
- `crear_topologia_triangulo`
- `crear_topologia_lineal`

---

# IV. INSTALACIÓN Y CONFIGURACIÓN

A continuación se describe el proceso completo de instalación del sistema sobre Ubuntu 24.04 LTS.

---

## Paso 1–2 — Sistema y GNS3

```bash
sudo apt update && sudo apt upgrade -y
sudo add-apt-repository ppa:gns3/ppa
sudo apt install gns3-gui gns3-server -y
sudo usermod -aG ubridge,libvirt,kvm,wireshark $USER && sudo reboot
```

---

## Paso 3 — Configurar GNS3


Abrir GNS3 y completar el Setup Wizard:

- Server type: `Local`
- Host: `127.0.0.1`
- Port: `3080`

<img width="720" height="533" alt="image" src="https://github.com/user-attachments/assets/4c6140dd-b595-4b58-b6ba-bbf4d201295c" />

### Fig. 1 — Configuración del servidor local en GNS3

```bash
curl http://localhost:3080/v2/version
```

_Verificar que la API REST responde correctamente._

---

## Paso 4 — Python y entorno virtual


```bash
sudo apt install python3 python3-pip python3-venv git curl wget -y
python3 --version
```

_Verificar Python 3.12+_

```bash
mkdir -p ~/gns3-mcp && cd ~/gns3-mcp

python3 -m venv venv
source venv/bin/activate

pip install requests anthropic mcp telnetlib3 pyyaml fastapi uvicorn websockets httpx
```

<img width="675" height="100" alt="image" src="https://github.com/user-attachments/assets/5e3a1636-b091-49c1-a41b-683ab0bed6ab" />

### Fig. 2 — Confirmación de la versión de Python

---

## Paso 5 — Obtener IDs de plantillas

```python
# obtener_templates.py

import requests

r = requests.get('http://localhost:3080/v2/templates')

for t in r.json():
    print(f"{t['name']:<40} {t['template_id']}")
```

---

## Paso 6 — Módulos principales del proyecto

### 1. `cisco_config.py`

Configuración asíncrona de routers Cisco IOSv vía Telnet:

- Hostname
- IPs
- OSPF

### 2. `gns3_helpers.py`

Abstracción sobre la API REST de GNS3:

- Proyectos
- Nodos
- Enlaces
- Plantillas dinámicas

### 3. `gns3_mcp_server.py`

Servidor MCP con 14 herramientas expuestas a Claude vía JSONSchema.

### 4. `app.py`

Backend FastAPI con WebSocket que orquesta:

- Navegador
- Claude
- MCP

---

## Paso 7 — API Key de Anthropic


1. Crear cuenta en:
   - https://console.anthropic.com

2. Generar API Key

3. Agregar saldo mínimo:
   - `$5 USD` para pruebas

<img width="825" height="231" alt="image" src="https://github.com/user-attachments/assets/453dddb4-2d49-4e49-9610-9ca8e147d29f" />

### Fig. 3 — Panel de claves API en Anthropic Console

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc

source ~/.bashrc
```

---

## Paso 8 — Empaquetado como instalador `.deb`

El script `build_deb.sh` automatiza:

- La estructura del paquete Debian
- El empaquetado del código con su entorno virtual
- Un asistente de primera configuración con `zenity`
- Icono de aplicación
- Generación del archivo `.deb` instalable con doble clic

---

# V. RESULTADOS


Las pruebas validaron la automatización de múltiples escenarios:

- Redes LAN
- Topologías lineales
- Triángulos OSPF
- Arquitecturas Hub-and-Spoke

El sistema configuró topologías completas, incluyendo:

- Direccionamiento IP
- Adyacencias OSPF
- Verificación de rutas

en aproximadamente **tres minutos**.

También se verificó interoperabilidad con:

- VyOS
- MikroTik
- pfSense


<img width="780" height="766" alt="image" src="https://github.com/user-attachments/assets/ada87244-7d2d-4b49-91ae-a9b606d570e3" />

### Fig. 4 — Interfaz web de GNS3 AI Studio

---

## Tabla I — Comparativa de tiempos de implementación

| Topología | Manual | Con GNS3 AI Studio | Reducción |
|---|---|---|---|
| LAN simple (4 PCs) | 30–60 min | ~1 min | >95% |
| Topología lineal | 45–90 min | ~2 min | >96% |
| Triángulo OSPF | 90–120 min | ~3 min | >97% |
| Hub-and-Spoke OSPF | 2–4 horas | ~3 min | >97% |

---

# VI. DISCUSIÓN

Un desafío principal fue la limitación de tiempo de espera de Claude Desktop, resuelta con un cliente Python personalizado para la API de Anthropic.

La administración dinámica de templates de GNS3 —cuyos UUID cambian entre instalaciones— se solucionó con un mecanismo de descubrimiento en tiempo de ejecución.

La arquitectura basada en MCP permite extender el sistema sin modificar el núcleo, facilitando la incorporación futura de:

- BGP
- EIGRP
- VLANs
- Soporte multi-fabricante

El instalador `.deb` reduce la fricción de adopción para usuarios sin experiencia en administración Linux.

---

# VII. CONCLUSIONES

GNS3 AI Studio demuestra que la integración de IA con plataformas de simulación de redes permite automatizar procesos complejos de configuración.

La reducción de tiempo supera el **95%**, comprimiendo procesos de **2–4 horas** a menos de **3 minutos**.

La solución tiene alto potencial en:

- Universidades
- Centros CCNA/CCNP
- NOC

La arquitectura permite expansión hacia:

- Protocolos avanzados como BGP y EIGRP
- Soporte multi-fabricante
- Entornos de VLANs

---

# Declaración de Uso de IA

Se utilizaron herramientas de IA para asistencia en redacción técnica y organización del manuscrito.

Todos los resultados y validaciones fueron revisados manualmente por los autores.

---

# Responsabilidad

Los autores asumen plena responsabilidad sobre la exactitud, originalidad e integridad del contenido, garantizando que el uso de IA no reemplazó el criterio técnico ni la validación académica.

---

# Referencias

1. Anthropic — Model Context Protocol Documentation  
   https://modelcontextprotocol.io

2. GNS3 Technologies Inc. — GNS3 REST API Documentation  
   https://gns3-server.readthedocs.io

3. FastAPI — FastAPI Framework Documentation  
   https://fastapi.tiangolo.com

4. Anthropic — Claude API Reference  
   https://docs.anthropic.com

5. Python Software Foundation — Python 3 Documentation  
   https://docs.python.org/3/

6. GNS3 Marketplace — GNS3 Appliances and Templates  
   https://www.gns3.com/marketplace/appliances
