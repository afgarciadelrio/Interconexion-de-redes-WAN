"""
Helpers GNS3 v2.1 - Maneja templates Y nodos built-in correctamente
"""
import requests
import math
import asyncio
from cisco_config import configurar_router, enviar_comandos

GNS3_URL = "http://localhost:3080/v2"
_TEMPLATES_CACHE = None

# Nodos built-in: se crean con endpoint /nodes directo
NODOS_BUILTIN = {
    "switch":  {"node_type": "ethernet_switch"},
    "hub":     {"node_type": "ethernet_hub"},
    "vpcs":    {"node_type": "vpcs"},
    "cloud":   {"node_type": "cloud"},
    "nat":     {"node_type": "nat"},
}

# Nodos con template (Cisco)
TEMPLATES_NOMBRES = {
    "router":    "Cisco IOSv",
    "switch_l3": "Cisco IOSvL2",
    "switch_l2": "Capa 2",
}

def cargar_templates():
    global _TEMPLATES_CACHE
    _TEMPLATES_CACHE = requests.get(f"{GNS3_URL}/templates").json()
    return _TEMPLATES_CACHE

def buscar_template_id(busqueda):
    global _TEMPLATES_CACHE
    if _TEMPLATES_CACHE is None:
        cargar_templates()
    busqueda = busqueda.lower()
    for t in _TEMPLATES_CACHE:
        if t["name"].lower() == busqueda:
            return t["template_id"]
    for t in _TEMPLATES_CACHE:
        if busqueda in t["name"].lower():
            return t["template_id"]
    return None

def buscar_project_id(nombre):
    try:
        for p in requests.get(f"{GNS3_URL}/projects").json():
            if p["name"].lower() == nombre.lower():
                return p["project_id"]
    except Exception as e:
        print(f"Error: {e}")
    return None

def abrir_proyecto(pid):
    try:
        requests.post(f"{GNS3_URL}/projects/{pid}/open")
    except Exception:
        pass

def crear_proyecto(nombre):
    r = requests.post(f"{GNS3_URL}/projects", json={"name": nombre})
    r.raise_for_status()
    pid = r.json()["project_id"]
    abrir_proyecto(pid)
    return pid

def eliminar_proyecto(pid):
    return requests.delete(f"{GNS3_URL}/projects/{pid}").status_code

def listar_proyectos():
    return requests.get(f"{GNS3_URL}/projects").json()

def agregar_nodo(pid, tipo, nombre, x, y):
    """
    Agrega un nodo al proyecto.
    Built-in (switch, hub, vpcs, cloud, nat) → endpoint /nodes
    Cisco (router, switch_l3, switch_l2) → endpoint /templates/{id}
    """
    abrir_proyecto(pid)
    
    # CAMINO 1: Built-in (sin template)
    if tipo in NODOS_BUILTIN:
        payload = {
            "name": nombre,
            "node_type": NODOS_BUILTIN[tipo]["node_type"],
            "compute_id": "local",
            "x": x,
            "y": y,
        }
        r = requests.post(f"{GNS3_URL}/projects/{pid}/nodes", json=payload)
        r.raise_for_status()
        return r.json()
    
    # CAMINO 2: Con template (Cisco)
    if tipo in TEMPLATES_NOMBRES:
        nombre_tpl = TEMPLATES_NOMBRES[tipo]
        tpl_id = buscar_template_id(nombre_tpl)
        if not tpl_id:
            cargar_templates()
            tpl_id = buscar_template_id(nombre_tpl)
        if not tpl_id:
            raise ValueError(f"Plantilla '{nombre_tpl}' no encontrada")
        r = requests.post(
            f"{GNS3_URL}/projects/{pid}/templates/{tpl_id}",
            json={"x": x, "y": y, "name": nombre}
        )
        r.raise_for_status()
        return r.json()
    
    raise ValueError(f"Tipo '{tipo}' desconocido")

def listar_nodos(pid):
    return requests.get(f"{GNS3_URL}/projects/{pid}/nodes").json()

def buscar_nodo_por_nombre(pid, nombre):
    for n in listar_nodos(pid):
        if n["name"].lower() == nombre.lower():
            return n
    return None

def conectar(pid, nodo_a_id, adapter_a, port_a, nodo_b_id, adapter_b, port_b):
    payload = {"nodes": [
        {"node_id": nodo_a_id, "adapter_number": adapter_a, "port_number": port_a},
        {"node_id": nodo_b_id, "adapter_number": adapter_b, "port_number": port_b}
    ]}
    r = requests.post(f"{GNS3_URL}/projects/{pid}/links", json=payload)
    r.raise_for_status()
    return r.json()

def iniciar_todos(pid):
    return requests.post(f"{GNS3_URL}/projects/{pid}/nodes/start").status_code

def detener_todos(pid):
    return requests.post(f"{GNS3_URL}/projects/{pid}/nodes/stop").status_code

def posicion_circular(i, total, radio=300, centro_x=0, centro_y=0):
    ang = math.radians((360 / total) * i)
    return int(centro_x + radio * math.cos(ang)), int(centro_y + radio * math.sin(ang))

def posicion_linea(i, total, espaciado=200, y=0):
    inicio_x = -(total - 1) * espaciado // 2
    return inicio_x + i * espaciado, y
