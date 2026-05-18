#!/usr/bin/env python3
"""
GNS3 MCP Server v4.1 - Con fix de port_a/port_b para switches
"""
import asyncio
import os
import yaml
import requests
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from cisco_config import configurar_router, enviar_comandos
import gns3_helpers as g

PLANTILLAS_DIR = os.path.expanduser("~/gns3-mcp/plantillas")
os.makedirs(PLANTILLAS_DIR, exist_ok=True)

app = Server("gns3-automation")

# === HERRAMIENTAS MCP ===
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        # --- CONSULTAS ---
        types.Tool(
            name="listar_proyectos",
            description="Lista todos los proyectos en GNS3",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="listar_nodos",
            description="Lista los nodos de un proyecto",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"}}, "required": ["proyecto"]}
        ),
        
        # --- PROYECTOS ---
        types.Tool(
            name="crear_proyecto",
            description="Crea un proyecto vacío en GNS3",
            inputSchema={"type": "object", "properties": {
                "nombre": {"type": "string"}}, "required": ["nombre"]}
        ),
        types.Tool(
            name="eliminar_proyecto",
            description="Elimina un proyecto por nombre",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"}}, "required": ["proyecto"]}
        ),
        
        # --- NODOS ---
        types.Tool(
            name="agregar_nodo",
            description="Agrega un nodo al proyecto. Tipos disponibles: router (Cisco IOSv, 4 interfaces g0/0 a g0/3), switch_l3 (Cisco IOSvL2), switch_l2, vpcs (PC virtual), switch (Ethernet switch con 8 puertos), hub, cloud, nat.",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"},
                "tipo": {"type": "string"},
                "nombre": {"type": "string"},
                "x": {"type": "integer", "default": 0},
                "y": {"type": "integer", "default": 0}
            }, "required": ["proyecto", "tipo", "nombre"]}
        ),
        types.Tool(
            name="conectar_nodos",
            description=(
                "Conecta dos nodos. IMPORTANTE: el comportamiento depende del tipo de nodo:\n"
                "- ROUTERS Cisco: usa adapter para elegir interfaz (0=g0/0, 1=g0/1, 2=g0/2, 3=g0/3), port siempre 0.\n"
                "- SWITCHES/HUBS: adapter SIEMPRE 0, y port para elegir puerto (0, 1, 2, 3, 4...). "
                "Cada conexión a un MISMO switch debe usar un port_b distinto.\n"
                "- VPCS/PCs: adapter=0, port=0 (solo tienen 1 interfaz).\n\n"
                "Ejemplo: para conectar 3 PCs al switch SW1:\n"
                "  PC1 → SW1: adapter_a=0, port_a=0, adapter_b=0, port_b=0\n"
                "  PC2 → SW1: adapter_a=0, port_a=0, adapter_b=0, port_b=1\n"
                "  PC3 → SW1: adapter_a=0, port_a=0, adapter_b=0, port_b=2\n"
                "Para conectar router R1 (interfaz g0/2) al switch SW1 puerto 7:\n"
                "  R1 → SW1: adapter_a=2, port_a=0, adapter_b=0, port_b=7"
            ),
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"},
                "nodo_a": {"type": "string"},
                "adapter_a": {"type": "integer", "default": 0},
                "port_a": {"type": "integer", "default": 0},
                "nodo_b": {"type": "string"},
                "adapter_b": {"type": "integer", "default": 0},
                "port_b": {"type": "integer", "default": 0}
            }, "required": ["proyecto", "nodo_a", "nodo_b"]}
        ),
        types.Tool(
            name="iniciar_nodos",
            description="Enciende TODOS los nodos del proyecto",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"}}, "required": ["proyecto"]}
        ),
        types.Tool(
            name="detener_nodos",
            description="Apaga TODOS los nodos del proyecto",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"}}, "required": ["proyecto"]}
        ),
        
        # --- CONFIGURACIÓN (routers Cisco encendidos) ---
        types.Tool(
            name="configurar_router",
            description="Configura un router Cisco IOSv: hostname, IPs en interfaces, OSPF. Cisco IOSv tiene 4 interfaces: GigabitEthernet0/0 a 0/3. El router debe estar encendido y haber booteado (~2 min).",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"},
                "router": {"type": "string"},
                "interfaces": {
                    "type": "object",
                    "description": "Dict {interfaz: 'ip mascara'}. Ej: {'GigabitEthernet0/0': '10.0.0.1 255.255.255.252'}"
                },
                "ospf_proceso": {"type": "integer", "description": "Número proceso OSPF (opcional)"},
                "ospf_redes": {
                    "type": "array",
                    "description": "Lista [red, wildcard, area]. Ej: [['10.0.0.0', '0.0.0.3', 0]]",
                    "items": {"type": "array"}
                }
            }, "required": ["proyecto", "router", "interfaces"]}
        ),
        types.Tool(
            name="ejecutar_comandos",
            description="Ejecuta comandos IOS en un router por telnet. Útil para verificaciones (show ip route, show ip ospf neighbor, etc.)",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"},
                "router": {"type": "string"},
                "comandos": {"type": "array", "items": {"type": "string"}}
            }, "required": ["proyecto", "router", "comandos"]}
        ),
        
        # --- TOPOLOGÍAS PREDISEÑADAS ---
        types.Tool(
            name="crear_lan_simple",
            description="Crea LAN: 1 switch + N PCs VPCS conectados. Listos para usar.",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"},
                "num_pcs": {"type": "integer", "description": "Cantidad de PCs (2-8)"}
            }, "required": ["proyecto", "num_pcs"]}
        ),
        types.Tool(
            name="crear_topologia_hub_spoke",
            description="Crea topología hub-and-spoke con routers Cisco IOSv. Solo cableado, SIN configuración IP/OSPF.",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"},
                "num_spokes": {"type": "integer", "description": "Cantidad de spokes (1-4, máx 4 por límite de interfaces IOSv)"}
            }, "required": ["proyecto", "num_spokes"]}
        ),
        types.Tool(
            name="crear_topologia_triangulo",
            description="Crea 3 routers Cisco IOSv conectados en triángulo. Solo cableado, SIN configuración.",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"}
            }, "required": ["proyecto"]}
        ),
        types.Tool(
            name="crear_topologia_lineal",
            description="Crea N routers conectados en línea: R1-R2-R3-...-RN. Solo cableado.",
            inputSchema={"type": "object", "properties": {
                "proyecto": {"type": "string"},
                "num_routers": {"type": "integer", "description": "Cantidad de routers (2-5)"}
            }, "required": ["proyecto", "num_routers"]}
        ),
    ]

# === IMPLEMENTACIÓN ===
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        # --- LISTAR PROYECTOS ---
        if name == "listar_proyectos":
            proyectos = g.listar_proyectos()
            if not proyectos:
                return [types.TextContent(type="text", text="📭 No hay proyectos.")]
            texto = f"📋 {len(proyectos)} proyectos:\n\n"
            for p in proyectos:
                est = "🟢" if p.get("status") == "opened" else "⚪"
                texto += f"{est} {p['name']}\n"
            return [types.TextContent(type="text", text=texto)]

        # --- LISTAR NODOS ---
        elif name == "listar_nodos":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                return [types.TextContent(type="text", text="❌ Proyecto no encontrado.")]
            nodos = g.listar_nodos(pid)
            if not nodos:
                return [types.TextContent(type="text", text="📭 Sin nodos.")]
            texto = f"🖥️  {len(nodos)} nodos:\n\n"
            for n in nodos:
                icono = {"started": "🟢", "stopped": "🔴"}.get(n.get("status"), "⚪")
                consola = n.get("console", "-")
                texto += f"{icono} {n['name']} ({n.get('node_type', '?')}) → consola:{consola}\n"
            return [types.TextContent(type="text", text=texto)]

        # --- CREAR PROYECTO ---
        elif name == "crear_proyecto":
            pid = g.crear_proyecto(arguments["nombre"])
            return [types.TextContent(type="text",
                text=f"✅ Proyecto '{arguments['nombre']}' creado.\n🆔 {pid[:8]}...")]

        # --- ELIMINAR PROYECTO ---
        elif name == "eliminar_proyecto":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                return [types.TextContent(type="text", text="❌ No encontrado.")]
            g.eliminar_proyecto(pid)
            return [types.TextContent(type="text", text="🗑️  Eliminado.")]

        # --- AGREGAR NODO ---
        elif name == "agregar_nodo":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                return [types.TextContent(type="text", text="❌ Proyecto no encontrado.")]
            nodo = g.agregar_nodo(
                pid, arguments["tipo"], arguments["nombre"],
                arguments.get("x", 0), arguments.get("y", 0)
            )
            return [types.TextContent(type="text",
                text=f"➕ {arguments['nombre']} ({arguments['tipo']}) agregado.")]

        # --- CONECTAR NODOS (CON FIX port_a/port_b) ---
        elif name == "conectar_nodos":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                return [types.TextContent(type="text", text="❌ Proyecto no encontrado.")]
            na = g.buscar_nodo_por_nombre(pid, arguments["nodo_a"])
            nb = g.buscar_nodo_por_nombre(pid, arguments["nodo_b"])
            if not na or not nb:
                return [types.TextContent(type="text", text="❌ Nodo no encontrado.")]
            g.conectar(pid,
                       na["node_id"], arguments.get("adapter_a", 0), arguments.get("port_a", 0),
                       nb["node_id"], arguments.get("adapter_b", 0), arguments.get("port_b", 0))
            return [types.TextContent(type="text",
                text=f"🔗 {arguments['nodo_a']} ↔ {arguments['nodo_b']} conectados.")]

        # --- INICIAR/DETENER ---
        elif name == "iniciar_nodos":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                return [types.TextContent(type="text", text="❌ Proyecto no encontrado.")]
            g.iniciar_todos(pid)
            return [types.TextContent(type="text",
                text="⚡ Iniciando nodos...\n💡 Cisco IOSv tarda ~2 min en arrancar.")]

        elif name == "detener_nodos":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                return [types.TextContent(type="text", text="❌ Proyecto no encontrado.")]
            g.detener_todos(pid)
            return [types.TextContent(type="text", text="🛑 Nodos detenidos.")]

        # --- CONFIGURAR ROUTER ---
        elif name == "configurar_router":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                return [types.TextContent(type="text", text="❌ Proyecto no encontrado.")]
            nodo = g.buscar_nodo_por_nombre(pid, arguments["router"])
            if not nodo:
                return [types.TextContent(type="text", text="❌ Router no encontrado.")]
            
            ospf_redes = arguments.get("ospf_redes")
            if ospf_redes:
                ospf_redes = [tuple(r) for r in ospf_redes]
            
            await configurar_router(
                "127.0.0.1", nodo["console"], arguments["router"],
                arguments["interfaces"],
                arguments.get("ospf_proceso"),
                ospf_redes,
            )
            return [types.TextContent(type="text",
                text=f"⚙️  {arguments['router']} configurado.")]

        # --- EJECUTAR COMANDOS ---
        elif name == "ejecutar_comandos":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                return [types.TextContent(type="text", text="❌ Proyecto no encontrado.")]
            nodo = g.buscar_nodo_por_nombre(pid, arguments["router"])
            if not nodo:
                return [types.TextContent(type="text", text="❌ Router no encontrado.")]
            
            cmds = ["", "enable", "terminal length 0"] + arguments["comandos"]
            salida = await enviar_comandos("127.0.0.1", nodo["console"], cmds, espera_inicial=2)
            return [types.TextContent(type="text",
                text=f"📤 Salida de {arguments['router']}:\n\n{salida[-2000:]}")]

        # --- CREAR LAN SIMPLE (con port_b correcto) ---
        elif name == "crear_lan_simple":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                pid = g.crear_proyecto(arguments["proyecto"])
            
            n = arguments["num_pcs"]
            if n > 8:
                n = 8  # límite de puertos del switch
            
            sw = g.agregar_nodo(pid, "switch", "SW1", 0, 0)
            for i in range(n):
                pc = g.agregar_nodo(pid, "vpcs", f"PC{i+1}", -200 + (i*80), 200)
                # IMPORTANTE: port_b = i para puerto diferente en el switch
                g.conectar(pid, pc["node_id"], 0, 0, sw["node_id"], 0, i)
            
            return [types.TextContent(type="text",
                text=f"✅ LAN '{arguments['proyecto']}' creada: 1 switch + {n} PCs (puertos 0 a {n-1}).")]

        # --- HUB-AND-SPOKE ---
        elif name == "crear_topologia_hub_spoke":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                pid = g.crear_proyecto(arguments["proyecto"])
            
            n = arguments["num_spokes"]
            if n > 4:
                n = 4  # IOSv solo tiene 4 interfaces
            
            hub = g.agregar_nodo(pid, "router", "R1-HUB", 0, -200)
            
            for i in range(n):
                x, y = g.posicion_circular(i, n, radio=250, centro_y=100)
                sp = g.agregar_nodo(pid, "router", f"R{i+2}-SPOKE", x, y)
                # Hub usa adapter i (g0/i), spoke usa adapter 0 (g0/0)
                g.conectar(pid, hub["node_id"], i, 0, sp["node_id"], 0, 0)
            
            return [types.TextContent(type="text",
                text=f"✅ Hub-and-Spoke '{arguments['proyecto']}' creado: 1 hub + {n} spokes.\n💡 Inicia los nodos y espera ~2 min a que bootee IOSv.")]

        # --- TRIÁNGULO ---
        elif name == "crear_topologia_triangulo":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                pid = g.crear_proyecto(arguments["proyecto"])
            
            r1 = g.agregar_nodo(pid, "router", "R1", 0, -150)
            r2 = g.agregar_nodo(pid, "router", "R2", -200, 100)
            r3 = g.agregar_nodo(pid, "router", "R3", 200, 100)
            
            # R1 g0/0 <-> R2 g0/0
            g.conectar(pid, r1["node_id"], 0, 0, r2["node_id"], 0, 0)
            # R1 g0/1 <-> R3 g0/0
            g.conectar(pid, r1["node_id"], 1, 0, r3["node_id"], 0, 0)
            # R2 g0/1 <-> R3 g0/1
            g.conectar(pid, r2["node_id"], 1, 0, r3["node_id"], 1, 0)
            
            return [types.TextContent(type="text",
                text=f"✅ Triángulo '{arguments['proyecto']}' creado con R1, R2, R3.\n💡 Inicia los nodos y espera el boot (~2 min).")]

        # --- LINEAL ---
        elif name == "crear_topologia_lineal":
            pid = g.buscar_project_id(arguments["proyecto"])
            if not pid:
                pid = g.crear_proyecto(arguments["proyecto"])
            
            n = arguments["num_routers"]
            if n > 5:
                n = 5
            
            routers = []
            for i in range(n):
                x, y = g.posicion_linea(i, n, espaciado=200)
                r = g.agregar_nodo(pid, "router", f"R{i+1}", x, y)
                routers.append(r)
            
            # R1-R2-R3-...-RN
            for i in range(n - 1):
                # Router actual usa g0/1 (derecha), siguiente usa g0/0 (izquierda)
                g.conectar(pid, routers[i]["node_id"], 1, 0, routers[i+1]["node_id"], 0, 0)
            
            return [types.TextContent(type="text",
                text=f"✅ Topología lineal '{arguments['proyecto']}' creada: {n} routers en línea.\n💡 Inicia y espera boot.")]

    except Exception as e:
        import traceback
        return [types.TextContent(type="text",
            text=f"❌ Error: {str(e)}\n\n{traceback.format_exc()}")]

# === MAIN ===
async def main():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await app.run(read, write,
            InitializationOptions(
                server_name="gns3-automation",
                server_version="4.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
