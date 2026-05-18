#!/usr/bin/env python3
"""
GNS3 AI Studio - Backend FastAPI
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import os
import requests
from pathlib import Path
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="GNS3 AI Studio")

MODELO = "claude-sonnet-4-6"
SERVER_SCRIPT = str(BASE_DIR / "gns3_mcp_server.py")
PYTHON_PATH = str(BASE_DIR / "venv/bin/python3")

SYSTEM_PROMPT = """Eres GNS3 AI Studio, asistente experto en redes Cisco.
Tu trabajo es crear y gestionar topologías en GNS3 usando las herramientas disponibles.

REGLAS:
- Responde SIEMPRE en español
- Sé conciso y directo
- Cuando el usuario pida crear algo, HAZLO inmediatamente con las herramientas
- Cisco IOSv tarda ~2 min en bootear, informa al usuario
- Máximo 4 spokes en hub-and-spoke (límite de interfaces IOSv)
- Para OSPF con configuración: crea → conecta → inicia → espera 120s → configura"""

@app.get("/")
async def root():
    with open(STATIC_DIR / "index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/status")
async def status():
    gns3_ok = False
    version = "N/A"
    try:
        r = requests.get("http://localhost:3080/v2/version", timeout=2)
        if r.status_code == 200:
            gns3_ok = True
            version = r.json().get("version", "?")
    except:
        pass
    return {
        "gns3": gns3_ok,
        "version": version,
        "api": bool(os.getenv("ANTHROPIC_API_KEY"))
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    anthropic = Anthropic()
    historial = []

    try:
        params = StdioServerParameters(command=PYTHON_PATH, args=[SERVER_SCRIPT])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                resp = await session.list_tools()
                tools = [{
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema
                } for t in resp.tools]

                await websocket.send_json({"type": "ready", "tools": len(tools)})

                while True:
                    data = await websocket.receive_json()
                    mensaje = data.get("message", "").strip()
                    if not mensaje:
                        continue

                    historial.append({"role": "user", "content": mensaje})

                    iteracion = 0
                    while iteracion < 20:
                        iteracion += 1

                        respuesta = anthropic.messages.create(
                            model=MODELO,
                            max_tokens=4096,
                            system=SYSTEM_PROMPT,
                            tools=tools,
                            messages=historial
                        )

                        tool_calls = []
                        texto = ""

                        for bloque in respuesta.content:
                            if bloque.type == "text":
                                texto += bloque.text
                            elif bloque.type == "tool_use":
                                tool_calls.append(bloque)

                        if texto:
                            await websocket.send_json({"type": "text", "content": texto})

                        historial.append({"role": "assistant", "content": respuesta.content})

                        if respuesta.stop_reason != "tool_use":
                            await websocket.send_json({"type": "done"})
                            break

                        tool_results = []
                        for tc in tool_calls:
                            await websocket.send_json({
                                "type": "tool_start",
                                "tool": tc.name,
                                "args": tc.input
                            })
                            try:
                                resultado = await session.call_tool(tc.name, tc.input)
                                texto_r = "\n".join([c.text for c in resultado.content])
                                await websocket.send_json({
                                    "type": "tool_result",
                                    "tool": tc.name,
                                    "result": texto_r
                                })
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tc.id,
                                    "content": texto_r
                                })
                            except Exception as e:
                                err = f"Error: {str(e)}"
                                await websocket.send_json({
                                    "type": "tool_error",
                                    "tool": tc.name,
                                    "error": err
                                })
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tc.id,
                                    "content": err,
                                    "is_error": True
                                })

                        historial.append({"role": "user", "content": tool_results})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            pass
