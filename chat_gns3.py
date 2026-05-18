#!/usr/bin/env python3
"""
Chat interactivo con Claude para controlar GNS3
Sin timeouts, ejecución directa de herramientas MCP
"""
import asyncio
import os
import sys
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# === CONFIGURACIÓN ===
MODELO = "claude-sonnet-4-6"
SERVER_SCRIPT = "/home/gabriel/gns3-mcp/gns3_mcp_server.py"
PYTHON_PATH = "/home/gabriel/gns3-mcp/venv/bin/python3"

SYSTEM_PROMPT = """Eres un asistente experto en redes y GNS3.

Tu trabajo es ayudar al usuario a crear y gestionar topologías de red 
de forma automatizada usando las herramientas MCP disponibles.

IMPORTANTE sobre Cisco IOSv:
- Los routers Cisco IOSv tardan ~2 minutos en arrancar después de iniciarse
- SIEMPRE espera antes de intentar configurarlos
- Cuando el usuario pida "crear topología con OSPF configurado", el flujo es:
  1. Crear proyecto y nodos
  2. Conectar enlaces
  3. Iniciar nodos
  4. ESPERAR 120 segundos
  5. Configurar cada router

Cuando uses herramientas:
- Sé claro sobre lo que estás haciendo
- Informa al usuario cuando estés esperando el boot de IOSv
- Muestra progreso en operaciones largas

Sé conciso pero informativo."""


class GNS3Chat:
    def __init__(self):
        self.anthropic = Anthropic()
        self.session = None
        self.tools_mcp = []
        self.historial = []
        self.stdio_ctx = None

    async def conectar_mcp(self):
        """Conecta con el servidor MCP de GNS3"""
        params = StdioServerParameters(
            command=PYTHON_PATH,
            args=[SERVER_SCRIPT]
        )
        self.stdio_ctx = stdio_client(params)
        read, write = await self.stdio_ctx.__aenter__()
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        # Obtener las herramientas disponibles
        resp = await self.session.list_tools()
        self.tools_mcp = [{
            "name": t.name,
            "description": t.description,
            "input_schema": t.inputSchema
        } for t in resp.tools]
        
        print(f"✅ Conectado al MCP de GNS3")
        print(f"🔧 {len(self.tools_mcp)} herramientas disponibles:\n")
        for t in self.tools_mcp:
            print(f"   • {t['name']}")
        print()

    async def procesar_mensaje(self, mensaje_usuario):
        """Envía mensaje a Claude y maneja llamadas a herramientas"""
        self.historial.append({"role": "user", "content": mensaje_usuario})
        
        iteracion = 0
        max_iteraciones = 20
        
        while iteracion < max_iteraciones:
            iteracion += 1
            
            # Llamar a Claude
            respuesta = self.anthropic.messages.create(
                model=MODELO,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=self.tools_mcp,
                messages=self.historial
            )
            
            # Procesar cada bloque de la respuesta
            tool_calls = []
            texto_respuesta = ""
            
            for bloque in respuesta.content:
                if bloque.type == "text":
                    texto_respuesta += bloque.text
                elif bloque.type == "tool_use":
                    tool_calls.append(bloque)
            
            # Mostrar lo que Claude dice
            if texto_respuesta:
                print(f"\n🤖 Claude: {texto_respuesta}\n")
            
            # Guardar respuesta del assistant
            self.historial.append({"role": "assistant", "content": respuesta.content})
            
            # Si no usó herramientas, terminamos
            if respuesta.stop_reason != "tool_use":
                break
            
            # Ejecutar las herramientas que pidió Claude
            tool_results = []
            for tc in tool_calls:
                print(f"🔧 Ejecutando: {tc.name}({tc.input})")
                
                try:
                    resultado = await self.session.call_tool(tc.name, tc.input)
                    texto_resultado = "\n".join([c.text for c in resultado.content])
                    print(f"📤 Resultado:\n{texto_resultado}\n")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tc.id,
                        "content": texto_resultado
                    })
                except Exception as e:
                    error_msg = f"❌ Error ejecutando {tc.name}: {str(e)}"
                    print(error_msg)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tc.id,
                        "content": error_msg,
                        "is_error": True
                    })
            
            # Mandar los resultados de vuelta a Claude
            self.historial.append({"role": "user", "content": tool_results})
        
        if iteracion >= max_iteraciones:
            print("⚠️  Se alcanzó el límite de iteraciones.")

    async def cerrar(self):
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.stdio_ctx:
            await self.stdio_ctx.__aexit__(None, None, None)


async def main():
    # Verificar API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY no está configurada")
        print("\nPara configurarla:")
        print('  echo \'export ANTHROPIC_API_KEY="sk-ant-..."\' >> ~/.bashrc')
        print('  source ~/.bashrc')
        sys.exit(1)
    
    print("=" * 70)
    print("🤖 ASISTENTE GNS3 - Powered by Claude + MCP")
    print("=" * 70)
    print()
    
    chat = GNS3Chat()
    
    try:
        await chat.conectar_mcp()
    except Exception as e:
        print(f"❌ No se pudo conectar al MCP: {e}")
        print("\nAsegúrate de que GNS3 esté abierto.")
        sys.exit(1)
    
    print("💡 Escribe lo que quieras hacer en GNS3.")
    print("💡 Ejemplos:")
    print("   - 'Crea una topología hub-and-spoke con 4 routers'")
    print("   - 'Crea una LAN con 6 PCs'")
    print("   - 'Lista todos los proyectos'")
    print("   - Escribe 'salir' para terminar\n")
    
    try:
        while True:
            try:
                entrada = input("👤 Tú: ").strip()
            except EOFError:
                break
            
            if not entrada:
                continue
            if entrada.lower() in ["salir", "exit", "quit"]:
                print("👋 ¡Hasta pronto!")
                break
            
            await chat.procesar_mensaje(entrada)
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. ¡Hasta pronto!")
    finally:
        await chat.cerrar()


if __name__ == "__main__":
    asyncio.run(main())
