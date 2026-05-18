# Automatización de Topologías de Red en GNS3 con Inteligencia Artificial y Model Context Protocol

**Autores:**  
Andrés F. García del Río  
José L. Castro Martín  
Gabriel E. de Hoyos Ozuna  

**Programa:** Ingeniería en Telecomunicaciones  
**Universidad:** Fundación Universitaria Compensar, Bogotá, Colombia  
**Contacto:** {afgarciadelrio | jluiscastro | gdehoyos}@ucompensar.edu.co  

---

## 📌 Descripción

**GNS3 AI Studio** es una plataforma basada en inteligencia artificial que automatiza la creación y configuración de topologías de red en GNS3 a partir de descripciones en lenguaje natural.

El sistema integra:

- Model Context Protocol (MCP)  
- API de Anthropic Claude Sonnet  
- API REST de GNS3  
- Backend en FastAPI  

Permite generar automáticamente:

- Dispositivos de red  
- Enlaces  
- Direccionamiento IP  
- Protocolos de enrutamiento (como OSPF)  

✅ Reduciendo el tiempo de creación de laboratorios de horas a minutos.

---

## 🚀 Problema

La creación manual de topologías en GNS3 implica:

- 2 a 4 horas de configuración  
- Alto conocimiento técnico  
- Complejidad en uso de API REST  
- Curva de aprendizaje en comandos Cisco  

Esto limita el aprendizaje rápido y la validación de escenarios.

---

## 🧠 Solución

GNS3 AI Studio permite:

- Describir una topología en lenguaje natural  
- Generar automáticamente la infraestructura  
- Configurar routers y protocolos  
- Ejecutar todo en pocos minutos  

---

## 🏗️ Arquitectura

El sistema está basado en cuatro componentes principales:

- **GNS3 REST API** → Gestión de proyectos, nodos y enlaces  
- **MCP (Model Context Protocol)** → Comunicación entre IA y herramientas  
- **Anthropic Claude API** → Procesamiento de lenguaje natural  
- **FastAPI + WebSockets** → Backend en tiempo real  

Los routers se configuran mediante Telnet asíncrono usando `telnetlib3`.

---

## 🔧 Herramientas MCP

El sistema expone 14 herramientas:

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

## ⚙️ Instalación

### 1️⃣ Sistema y GNS3

```bash
sudo apt update && sudo apt upgrade -y
sudo add-apt-repository ppa:gns3/ppa
sudo apt install gns3-gui gns3-server -y
sudo usermod -aG ubridge,libvirt,kvm,wireshark $USER && sudo reboot
