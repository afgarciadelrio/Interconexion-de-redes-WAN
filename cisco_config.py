"""
Módulo para enviar comandos a routers Cisco IOSv vía telnet
"""
import asyncio
import telnetlib3

async def enviar_comandos(host, puerto, comandos, espera_inicial=5):
    """
    Conecta por telnet a un router y envía una lista de comandos.
    Devuelve la salida completa.
    """
    try:
        reader, writer = await asyncio.wait_for(
            telnetlib3.open_connection(host, puerto, encoding='ascii'),
            timeout=10
        )
    except Exception as e:
        return f"❌ No se pudo conectar a {host}:{puerto} - {e}"
    
    await asyncio.sleep(espera_inicial)
    
    # Salir de cualquier prompt inicial
    writer.write("\r\n")
    await asyncio.sleep(1)
    writer.write("\r\n")
    await asyncio.sleep(1)
    
    salida_total = ""
    for cmd in comandos:
        writer.write(cmd + "\r\n")
        await asyncio.sleep(1.5)
        try:
            data = await asyncio.wait_for(reader.read(4096), timeout=2)
            salida_total += data
        except asyncio.TimeoutError:
            pass
    
    writer.close()
    return salida_total


async def configurar_router(host, puerto, hostname, interfaces, ospf_proceso=None, ospf_redes=None):
    """
    Configura un router Cisco IOSv completo:
    - hostname
    - interfaces con IPs
    - OSPF (opcional)
    
    interfaces = {"GigabitEthernet0/0": "10.0.0.1 255.255.255.252", ...}
    ospf_redes = [("10.0.0.0", "0.0.0.3", 0), ...]  # (red, wildcard, área)
    """
    cmds = [
        "",
        "enable",
        "configure terminal",
        f"hostname {hostname}",
        "no ip domain-lookup",
        "line con 0",
        " logging synchronous",
        " exec-timeout 0 0",
        "exit",
    ]
    
    # Interfaces
    for intf, ip_mask in interfaces.items():
        cmds += [
            f"interface {intf}",
            f" ip address {ip_mask}",
            " no shutdown",
            " exit",
        ]
    
    # OSPF
    if ospf_proceso and ospf_redes:
        cmds.append(f"router ospf {ospf_proceso}")
        for red, wc, area in ospf_redes:
            cmds.append(f" network {red} {wc} area {area}")
        cmds.append(" exit")
    
    cmds += [
        "end",
        "write memory",
    ]
    
    return await enviar_comandos(host, puerto, cmds, espera_inicial=3)
