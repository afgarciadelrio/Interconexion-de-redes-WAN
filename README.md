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

<img width="800" height="800" alt="image" src="https://github.com/user-attachments/assets/8ba9e676-e778-4b79-a5f7-c16fb2432c6c" />


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

```
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GNS3 AI Studio — Arquitectura MCP</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

  :root {
    --bg: #080c14;
    --surface: #0d1420;
    --card: #111827;
    --border: rgba(255,255,255,0.07);
    --accent: #00d4ff;
    --accent2: #7c3aed;
    --green: #10b981;
    --amber: #f59e0b;
    --coral: #f43f5e;
    --text: #e2e8f0;
    --muted: #64748b;
    --mono: 'JetBrains Mono', monospace;
    --sans: 'Space Grotesk', sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    overflow-x: hidden;
    padding: 40px 20px 60px;
  }

  /* Grid de fondo */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .container {
    max-width: 900px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
  }

  /* HEADER */
  .header {
    text-align: center;
    margin-bottom: 48px;
    animation: fadeDown 0.6s ease;
  }

  .header .badge {
    display: inline-block;
    background: rgba(0,212,255,0.1);
    border: 1px solid rgba(0,212,255,0.3);
    color: var(--accent);
    font-family: var(--mono);
    font-size: 11px;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
  }

  .header h1 {
    font-size: 36px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent), #fff 50%, var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
  }

  .header p {
    color: var(--muted);
    font-size: 14px;
  }

  /* DIAGRAMA */
  .diagram {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
  }

  /* CAPAS */
  .layer {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 16px;
    animation: fadeIn 0.5s ease both;
  }

  .layer:nth-child(1)  { animation-delay: 0.1s; }
  .layer:nth-child(2)  { animation-delay: 0.15s; }
  .layer:nth-child(3)  { animation-delay: 0.2s; }
  .layer:nth-child(4)  { animation-delay: 0.25s; }
  .layer:nth-child(5)  { animation-delay: 0.3s; }
  .layer:nth-child(6)  { animation-delay: 0.35s; }
  .layer:nth-child(7)  { animation-delay: 0.4s; }
  .layer:nth-child(8)  { animation-delay: 0.45s; }
  .layer:nth-child(9)  { animation-delay: 0.5s; }
  .layer:nth-child(10) { animation-delay: 0.55s; }
  .layer:nth-child(11) { animation-delay: 0.6s; }

  .layer-label {
    width: 80px;
    flex-shrink: 0;
    text-align: right;
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1px;
    text-transform: uppercase;
    line-height: 1.3;
  }

  .layer-content {
    flex: 1;
  }

  /* CARDS */
  .card {
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid var(--border);
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
  }

  .card::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0;
    transition: opacity 0.2s;
  }

  .card:hover { transform: translateY(-1px); }
  .card:hover::before { opacity: 1; }

  .card-title {
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .card-sub {
    font-size: 12px;
    color: var(--muted);
  }

  /* COLORES POR TIPO */
  .card.user     { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.25); }
  .card.user:hover { background: rgba(16,185,129,0.14); border-color: rgba(16,185,129,0.5); }
  .card.user .card-title { color: #10b981; }

  .card.frontend  { background: rgba(16,185,129,0.06); border-color: rgba(16,185,129,0.2); }
  .card.frontend:hover { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.4); }
  .card.frontend .card-title { color: #34d399; }

  .card.backend  { background: rgba(0,212,255,0.06); border-color: rgba(0,212,255,0.2); }
  .card.backend:hover { background: rgba(0,212,255,0.12); border-color: rgba(0,212,255,0.4); }
  .card.backend .card-title { color: var(--accent); }

  .card.ai       { background: rgba(124,58,237,0.08); border-color: rgba(124,58,237,0.25); }
  .card.ai:hover { background: rgba(124,58,237,0.15); border-color: rgba(124,58,237,0.5); }
  .card.ai .card-title { color: #a78bfa; }

  .card.mcp      { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.3); box-shadow: 0 0 20px rgba(245,158,11,0.05); }
  .card.mcp:hover { background: rgba(245,158,11,0.14); border-color: rgba(245,158,11,0.5); }
  .card.mcp .card-title { color: var(--amber); }

  .card.module   { background: rgba(244,63,94,0.06); border-color: rgba(244,63,94,0.2); }
  .card.module:hover { background: rgba(244,63,94,0.12); border-color: rgba(244,63,94,0.4); }
  .card.module .card-title { color: #fb7185; }

  .card.gns3     { background: rgba(148,163,184,0.06); border-color: rgba(148,163,184,0.2); }
  .card.gns3:hover { background: rgba(148,163,184,0.12); border-color: rgba(148,163,184,0.4); }
  .card.gns3 .card-title { color: #94a3b8; }

  /* TOOLS GRID */
  .tools-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    margin-top: 10px;
  }

  .tool-chip {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 6px;
    padding: 4px 8px;
    font-family: var(--mono);
    font-size: 10px;
    color: #fbbf24;
    text-align: center;
  }

  /* MÓDULOS LADO A LADO */
  .modules-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    width: 100%;
  }

  /* CONECTOR / FLECHA */
  .connector {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 6px 0;
    width: 100%;
  }

  .connector-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
  }

  .connector-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .connector-arrow {
    font-size: 16px;
    line-height: 1;
    filter: drop-shadow(0 0 4px currentColor);
  }

  .connector-label {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1px;
    white-space: nowrap;
  }

  .arr-green  { color: #10b981; }
  .arr-blue   { color: var(--accent); }
  .arr-purple { color: #a78bfa; }
  .arr-amber  { color: var(--amber); }
  .arr-coral  { color: #fb7185; }
  .arr-gray   { color: #64748b; }

  /* CONECTOR DIVIDIDO (para 2 módulos) */
  .connector-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    width: 100%;
    padding: 4px 0;
  }

  .split-arrow {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    gap: 2px;
  }

  /* PANEL DE TOOLTIP */
  .tooltip-panel {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background: var(--card);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 13px;
    color: var(--accent);
    font-family: var(--mono);
    max-width: 500px;
    width: 90%;
    text-align: center;
    z-index: 100;
    opacity: 0;
    transition: all 0.3s ease;
    pointer-events: none;
    box-shadow: 0 0 30px rgba(0,212,255,0.1);
  }

  .tooltip-panel.show {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }

  /* FOOTER */
  .footer {
    text-align: center;
    margin-top: 48px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 12px;
    font-family: var(--mono);
    animation: fadeIn 0.8s ease 0.8s both;
  }

  .footer span { color: var(--accent); }

  /* BADGE PRINCIPAL MCP */
  .mcp-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4);
    color: var(--amber);
    font-family: var(--mono);
    font-size: 10px;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 6px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .mcp-badge::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--amber);
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(245,158,11,0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 4px rgba(245,158,11,0); }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  @keyframes fadeDown {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  /* RESPONSIVE */
  @media (max-width: 600px) {
    .layer-label { width: 50px; font-size: 9px; }
    .tools-grid { grid-template-columns: repeat(2, 1fr); }
    .header h1 { font-size: 24px; }
    .modules-row { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<div class="container">

  <!-- HEADER -->
  <div class="header">
    <div class="badge">Model Context Protocol</div>
    <h1>GNS3 AI Studio</h1>
    <p>Arquitectura completa — de un prompt en español a una topología Cisco real</p>
  </div>

  <!-- DIAGRAMA -->
  <div class="diagram">

    <!-- CAPA: Usuario -->
    <div class="layer">
      <div class="layer-label">usuario</div>
      <div class="layer-content">
        <div class="card user" onclick="showTip('El usuario escribe en español: \"Crea una topología OSPF con 3 routers\". No necesita saber Python, ni comandos Cisco, ni nada técnico.')">
          <div class="card-title">👤 Usuario</div>
          <div class="card-sub">Escribe un prompt en español desde el navegador</div>
        </div>
      </div>
    </div>

    <!-- FLECHA -->
    <div class="layer">
      <div class="layer-label"></div>
      <div class="layer-content">
        <div class="connector">
          <div class="connector-center">
            <div class="connector-arrow arr-green">↓</div>
            <div class="connector-label">WebSocket en tiempo real</div>
          </div>
        </div>
      </div>
    </div>

    <!-- CAPA: Interfaz web -->
    <div class="layer">
      <div class="layer-label">frontend</div>
      <div class="layer-content">
        <div class="card frontend" onclick="showTip('static/index.html — La interfaz visual tipo ChatGPT. Muestra el chat, los botones rápidos, el estado del sistema y las tarjetas de herramientas ejecutadas. HTML + CSS + JS vanilla.')">
          <div class="card-title">🌐 static/index.html</div>
          <div class="card-sub">Interfaz web tipo ChatGPT — HTML + CSS + JS vanilla</div>
        </div>
      </div>
    </div>

    <!-- FLECHA -->
    <div class="layer">
      <div class="layer-label"></div>
      <div class="layer-content">
        <div class="connector">
          <div class="connector-center">
            <div class="connector-arrow arr-blue">↓</div>
            <div class="connector-label">WebSocket bidireccional</div>
          </div>
        </div>
      </div>
    </div>

    <!-- CAPA: Backend -->
    <div class="layer">
      <div class="layer-label">backend</div>
      <div class="layer-content">
        <div class="card backend" onclick="showTip('app.py — Servidor web construido con FastAPI. Recibe los mensajes del navegador por WebSocket, los envía a Claude, gestiona las herramientas MCP y devuelve los resultados al usuario en tiempo real.')">
          <div class="card-title">⚡ app.py</div>
          <div class="card-sub">Backend FastAPI con WebSockets — orquesta toda la comunicación</div>
        </div>
      </div>
    </div>

    <!-- FLECHA -->
    <div class="layer">
      <div class="layer-label"></div>
      <div class="layer-content">
        <div class="connector">
          <div class="connector-center">
            <div class="connector-arrow arr-purple">↓</div>
            <div class="connector-label">API Anthropic (claude-sonnet-4-6)</div>
          </div>
        </div>
      </div>
    </div>

    <!-- CAPA: Claude -->
    <div class="layer">
      <div class="layer-label">IA</div>
      <div class="layer-content">
        <div class="card ai" onclick="showTip('Claude Sonnet de Anthropic — El modelo de inteligencia artificial que interpreta el prompt en español y decide qué herramientas del MCP invocar. No genera código; toma decisiones y ejecuta acciones.')">
          <div class="card-title">🤖 Claude Sonnet (Anthropic)</div>
          <div class="card-sub">Interpreta el prompt y decide qué herramientas invocar</div>
        </div>
      </div>
    </div>

    <!-- FLECHA -->
    <div class="layer">
      <div class="layer-label"></div>
      <div class="layer-content">
        <div class="connector">
          <div class="connector-center">
            <div class="connector-arrow arr-amber">↓</div>
            <div class="connector-label">Model Context Protocol (stdio)</div>
          </div>
        </div>
      </div>
    </div>

    <!-- CAPA: MCP Server (PRINCIPAL) -->
    <div class="layer">
      <div class="layer-label">mcp</div>
      <div class="layer-content">
        <div class="card mcp" onclick="showTip('EL CORAZÓN del proyecto — gns3_mcp_server.py. Servidor MCP desarrollado por el equipo que expone 14 herramientas en JSON-Schema. Anthropic creó el protocolo MCP; nosotros creamos el servidor que lo implementa para GNS3.')">
          <div class="mcp-badge">Desarrollado por el equipo</div>
          <div class="card-title">🎯 gns3_mcp_server.py — Servidor MCP</div>
          <div class="card-sub">14 herramientas JSON-Schema expuestas a Claude</div>
          <div class="tools-grid">
            <div class="tool-chip">crear_proyecto</div>
            <div class="tool-chip">eliminar_proyecto</div>
            <div class="tool-chip">listar_proyectos</div>
            <div class="tool-chip">agregar_nodo</div>
            <div class="tool-chip">conectar_nodos</div>
            <div class="tool-chip">listar_nodos</div>
            <div class="tool-chip">iniciar_nodos</div>
            <div class="tool-chip">detener_nodos</div>
            <div class="tool-chip">configurar_router</div>
            <div class="tool-chip">ejecutar_comandos</div>
            <div class="tool-chip">crear_lan_simple</div>
            <div class="tool-chip">hub_spoke</div>
            <div class="tool-chip">triangulo</div>
            <div class="tool-chip">lineal</div>
          </div>
        </div>
      </div>
    </div>

    <!-- FLECHAS SPLIT -->
    <div class="layer">
      <div class="layer-label"></div>
      <div class="layer-content">
        <div class="connector-split">
          <div class="split-arrow">
            <div class="connector-arrow arr-coral">↓</div>
            <div class="connector-label">API REST GNS3</div>
          </div>
          <div class="split-arrow">
            <div class="connector-arrow arr-coral">↓</div>
            <div class="connector-label">Telnet asíncrono</div>
          </div>
        </div>
      </div>
    </div>

    <!-- CAPA: Módulos -->
    <div class="layer">
      <div class="layer-label">módulos</div>
      <div class="layer-content">
        <div class="modules-row">
          <div class="card module" onclick="showTip('gns3_helpers.py — Capa de abstracción sobre la API REST de GNS3 (localhost:3080). Contiene funciones para crear proyectos, agregar nodos built-in (switch, VPCS) y nodos con template (Cisco IOSv), crear enlaces y controlar el estado.')">
            <div class="card-title">🛠️ gns3_helpers.py</div>
            <div class="card-sub">API REST de GNS3 — crea nodos, enlaces, proyectos</div>
          </div>
          <div class="card module" onclick="showTip('cisco_config.py — Conexión Telnet asíncrona a los routers Cisco IOSv usando telnetlib3. Envía secuencias de comandos IOS para configurar hostname, IPs en interfaces y protocolos como OSPF automáticamente.')">
            <div class="card-title">⚙️ cisco_config.py</div>
            <div class="card-sub">Telnet asíncrono — configura IPs y OSPF en Cisco IOS</div>
          </div>
        </div>
      </div>
    </div>

    <!-- FLECHA FINAL -->
    <div class="layer">
      <div class="layer-label"></div>
      <div class="layer-content">
        <div class="connector">
          <div class="connector-center">
            <div class="connector-arrow arr-gray">↓</div>
            <div class="connector-label">HTTP REST + Telnet (puerto 3080)</div>
          </div>
        </div>
      </div>
    </div>

    <!-- CAPA: GNS3 -->
    <div class="layer">
      <div class="layer-label">gns3</div>
      <div class="layer-content">
        <div class="card gns3" onclick="showTip('GNS3 corriendo en localhost:3080 con routers Cisco IOSv reales (no simulados como Packet Tracer). La topología aparece en el canvas de GNS3 con los dispositivos conectados, encendidos y configurados.')">
          <div class="card-title">🔌 GNS3 (localhost:3080) + Cisco IOSv</div>
          <div class="card-sub">Topología creada con routers Cisco IOS reales — ¡no simulados!</div>
        </div>
      </div>
    </div>

  </div>

  <!-- FOOTER -->
  <div class="footer">
    <p>Haz clic en cualquier componente para ver más detalles</p>
    <p style="margin-top:8px">
      <span>GNS3 AI Studio v1.0</span> —
      Ingeniería en Telecomunicaciones, Universidad Compensar —
      <span>github.com/afgarciadelrio/Interconexion-de-redes-WAN</span>
    </p>
  </div>

</div>

<!-- TOOLTIP PANEL -->
<div class="tooltip-panel" id="tooltip"></div>

<script>
let hideTimeout;

function showTip(text) {
  const panel = document.getElementById('tooltip');
  panel.textContent = text;
  panel.classList.add('show');
  clearTimeout(hideTimeout);
  hideTimeout = setTimeout(() => panel.classList.remove('show'), 5000);
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.card')) {
    document.getElementById('tooltip').classList.remove('show');
  }
});
</script>
</body>
</html>
```

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
