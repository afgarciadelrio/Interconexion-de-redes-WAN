#!/bin/bash
echo "🌐 Iniciando GNS3 AI Studio..."
cd ~/gns3-mcp
source venv/bin/activate

# Verificar GNS3
if ! curl -s http://localhost:3080/v2/version > /dev/null 2>&1; then
    echo "⚠️  GNS3 no está corriendo. Iniciando..."
    gns3 &
    sleep 5
fi

# Verificar API Key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    source ~/.bashrc
fi

echo "✅ Abriendo navegador..."
sleep 2
xdg-open http://localhost:8080 2>/dev/null &

echo "🚀 Servidor iniciado en: http://localhost:8080"
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
