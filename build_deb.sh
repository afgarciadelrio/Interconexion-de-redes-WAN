#!/bin/bash
# ============================================================
# GNS3 AI Studio - Constructor del Instalador .deb
# ============================================================
# Genera un paquete .deb instalable que incluye:
# - Python 3 con venv aislado
# - Todas las librerías necesarias
# - Interfaz web completa
# - Asistente gráfico de primera configuración (zenity)
# - Icono en menú de aplicaciones
# ============================================================
set -e

APP_NAME="gns3-ai-studio"
APP_VERSION="1.0.0"
BUILD_DIR="$HOME/gns3-build"
DEB_DIR="$BUILD_DIR/${APP_NAME}_${APP_VERSION}_amd64"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   GNS3 AI Studio - Build .deb v${APP_VERSION}      ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# === VERIFICAR DEPENDENCIAS ===
echo "📦 Verificando dependencias de construcción..."
sudo apt install -y python3 python3-venv python3-pip dpkg-dev 2>/dev/null

# === LIMPIAR BUILD ANTERIOR ===
echo "🧹 Limpiando builds anteriores..."
rm -rf "$BUILD_DIR"
mkdir -p "$DEB_DIR"

# === CREAR ESTRUCTURA DEL PAQUETE ===
echo "📁 Creando estructura del paquete Debian..."
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/gns3-ai-studio/static"
mkdir -p "$DEB_DIR/usr/local/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"

# === COPIAR ARCHIVOS DE LA APLICACIÓN ===
echo "📋 Copiando archivos de la aplicación..."
cp "$SCRIPT_DIR/app.py"                "$DEB_DIR/opt/gns3-ai-studio/"
cp "$SCRIPT_DIR/gns3_mcp_server.py"    "$DEB_DIR/opt/gns3-ai-studio/"
cp "$SCRIPT_DIR/gns3_helpers.py"       "$DEB_DIR/opt/gns3-ai-studio/"
cp "$SCRIPT_DIR/cisco_config.py"       "$DEB_DIR/opt/gns3-ai-studio/"
cp "$SCRIPT_DIR/gns3_marketplace.py"   "$DEB_DIR/opt/gns3-ai-studio/" 2>/dev/null || true
cp "$SCRIPT_DIR/chat_gns3.py"          "$DEB_DIR/opt/gns3-ai-studio/" 2>/dev/null || true
cp "$SCRIPT_DIR/static/index.html"     "$DEB_DIR/opt/gns3-ai-studio/static/"
cp "$SCRIPT_DIR/requirements.txt"      "$DEB_DIR/opt/gns3-ai-studio/"

# === CREAR VENV CON DEPENDENCIAS ===
echo "🐍 Creando entorno Python aislado..."
echo "   (Esto puede tomar 2-3 minutos)"
python3 -m venv "$DEB_DIR/opt/gns3-ai-studio/venv"
"$DEB_DIR/opt/gns3-ai-studio/venv/bin/pip" install --upgrade pip -q
"$DEB_DIR/opt/gns3-ai-studio/venv/bin/pip" install \
    -r "$DEB_DIR/opt/gns3-ai-studio/requirements.txt" \
    -q --no-cache-dir

echo "✅ Dependencias Python instaladas"

# === SCRIPT DE INICIO ===
echo "📝 Creando script de arranque..."
cat > "$DEB_DIR/opt/gns3-ai-studio/start.sh" << 'STARTSCRIPT'
#!/bin/bash
# GNS3 AI Studio - Script de inicio

APP_DIR="/opt/gns3-ai-studio"
CONFIG_DIR="$HOME/.config/gns3-ai-studio"
CONFIG_FILE="$CONFIG_DIR/config.env"

mkdir -p "$CONFIG_DIR"

# === PRIMERA EJECUCIÓN: ASISTENTE DE CONFIGURACIÓN ===
if [ ! -f "$CONFIG_FILE" ]; then
    zenity --info \
        --title="GNS3 AI Studio - Bienvenido" \
        --text="¡Bienvenido a GNS3 AI Studio!\n\nEsta es tu primera vez ejecutando la aplicación.\n\nNecesitarás una API Key de Anthropic para usar la inteligencia artificial.\n\nObtén una en:\nhttps://console.anthropic.com\n\nEn la siguiente ventana ingresa tu API Key." \
        --width=450 2>/dev/null || true

    API_KEY=$(zenity --entry \
        --title="GNS3 AI Studio - Configuración" \
        --text="Ingresa tu API Key de Anthropic:\n\n(Empieza con sk-ant-...)" \
        --entry-text="sk-ant-" \
        --width=500 2>/dev/null)

    if [ -z "$API_KEY" ] || [ "$API_KEY" = "sk-ant-" ]; then
        zenity --error \
            --title="Configuración cancelada" \
            --text="Se requiere una API Key válida para usar GNS3 AI Studio.\n\nPuedes ejecutar la aplicación de nuevo cuando tengas tu key." \
            2>/dev/null || true
        exit 1
    fi

    echo "ANTHROPIC_API_KEY=$API_KEY" > "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"
    
    zenity --info \
        --title="Configuración completada" \
        --text="✅ Configuración guardada correctamente.\n\nGNS3 AI Studio se está iniciando..." \
        --width=400 \
        --timeout=3 2>/dev/null || true
fi

# === CARGAR CONFIGURACIÓN ===
source "$CONFIG_FILE"
export ANTHROPIC_API_KEY

# === VERIFICAR GNS3 ===
if ! curl -s --connect-timeout 2 http://localhost:3080/v2/version > /dev/null 2>&1; then
    zenity --question \
        --title="GNS3 no detectado" \
        --text="⚠️ GNS3 no está corriendo en este momento.\n\n¿Deseas iniciarlo automáticamente?" \
        --width=400 2>/dev/null

    if [ $? -eq 0 ]; then
        gns3 &
        sleep 5
    else
        zenity --warning \
            --title="GNS3 requerido" \
            --text="GNS3 AI Studio necesita GNS3 corriendo para funcionar.\n\nInicia GNS3 manualmente y vuelve a ejecutar la aplicación." \
            2>/dev/null || true
        exit 1
    fi
fi

# === MATAR INSTANCIA ANTERIOR SI EXISTE ===
pkill -f "uvicorn app:app" 2>/dev/null || true
sleep 1

# === INICIAR SERVIDOR ===
cd "$APP_DIR"
"$APP_DIR/venv/bin/uvicorn" app:app \
    --host 0.0.0.0 \
    --port 8080 \
    > /tmp/gns3-studio.log 2>&1 &

SERVER_PID=$!

# Esperar que el servidor inicie
sleep 3

# === ABRIR NAVEGADOR ===
xdg-open http://localhost:8080 2>/dev/null || \
    sensible-browser http://localhost:8080 2>/dev/null || \
    firefox http://localhost:8080 2>/dev/null || \
    google-chrome http://localhost:8080 2>/dev/null

# === NOTIFICACIÓN ===
notify-send "GNS3 AI Studio" \
    "✅ Aplicación iniciada en http://localhost:8080" \
    --icon=network-wired 2>/dev/null || true

# === MANTENER PROCESO VIVO ===
wait $SERVER_PID
STARTSCRIPT
chmod +x "$DEB_DIR/opt/gns3-ai-studio/start.sh"

# === COMANDO CLI GLOBAL ===
echo "🔧 Creando comando CLI..."
cat > "$DEB_DIR/usr/local/bin/gns3-ai-studio" << 'CLI'
#!/bin/bash
exec /opt/gns3-ai-studio/start.sh "$@"
CLI
chmod +x "$DEB_DIR/usr/local/bin/gns3-ai-studio"

# === ICONO SVG ===
echo "🎨 Creando icono..."
cat > /tmp/gns3-studio-icon.svg << 'ICON'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="40" fill="#0d1117"/>
  <circle cx="128" cy="80" r="32" fill="#00d4ff" opacity="0.9"/>
  <circle cx="60" cy="190" r="26" fill="#3fb950" opacity="0.9"/>
  <circle cx="196" cy="190" r="26" fill="#3fb950" opacity="0.9"/>
  <line x1="128" y1="112" x2="60" y2="164" stroke="#00d4ff" stroke-width="8" stroke-linecap="round"/>
  <line x1="128" y1="112" x2="196" y2="164" stroke="#00d4ff" stroke-width="8" stroke-linecap="round"/>
  <line x1="86" y1="190" x2="170" y2="190" stroke="#3fb950" stroke-width="6" stroke-linecap="round"/>
  <text x="128" y="245" text-anchor="middle" fill="#8b949e" font-size="20" font-family="sans-serif" font-weight="bold">AI Studio</text>
</svg>
ICON

if command -v rsvg-convert &> /dev/null; then
    rsvg-convert -w 256 -h 256 /tmp/gns3-studio-icon.svg \
        -o "$DEB_DIR/usr/share/icons/hicolor/256x256/apps/gns3-ai-studio.png"
    ICON_NAME="gns3-ai-studio"
    echo "✅ Icono personalizado creado"
else
    ICON_NAME="network-wired"
    echo "ℹ️  Usando icono del sistema (instala librsvg2-bin para icono personalizado)"
fi

# === DESKTOP ENTRY ===
echo "🖥️  Creando entrada en menú de aplicaciones..."
cat > "$DEB_DIR/usr/share/applications/gns3-ai-studio.desktop" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=GNS3 AI Studio
GenericName=Network Topology Automation
Comment=Automatiza topologías de red con Inteligencia Artificial
Exec=/opt/gns3-ai-studio/start.sh
Icon=${ICON_NAME}
Terminal=false
Categories=Network;Education;Engineering;
Keywords=GNS3;network;AI;cisco;topology;automation;OSPF;routing;
StartupNotify=true
DESKTOP

# === ARCHIVO DE CONTROL DEL PAQUETE ===
echo "📦 Creando metadatos del paquete..."
INSTALLED_SIZE=$(du -sk "$DEB_DIR/opt" | cut -f1)

cat > "$DEB_DIR/DEBIAN/control" << CONTROL
Package: gns3-ai-studio
Version: ${APP_VERSION}
Section: net
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.10), python3-venv, zenity, curl, xdg-utils
Recommends: gns3-gui, gns3-server
Installed-Size: ${INSTALLED_SIZE}
Maintainer: Gabriel De Hoyos <gdehoyos@ucompensar.edu.co>
Homepage: https://github.com/afgarciadelrio/Interconexion-de-redes-WAN
Description: GNS3 AI Studio - Automatización de redes con IA
 Aplicación web que automatiza la creación de topologías de red
 en GNS3 mediante inteligencia artificial. Permite a usuarios sin
 conocimientos técnicos avanzados crear laboratorios de red
 completos usando lenguaje natural en español.
 .
 Características principales:
  * Interfaz web moderna tipo ChatGPT
  * Soporte para Cisco IOSv (routers reales, no simulados)
  * Configuración automática de OSPF, IPs y enlaces
  * 14 herramientas MCP integradas con Claude AI
  * Topologías: LAN, hub-and-spoke, triángulo, lineal
  * Soporte multimarca: VyOS, pfSense, MikroTik
 .
 Desarrollado como proyecto académico de Interconexión de Redes WAN
 en Ingeniería en Telecomunicaciones, Universidad Compensar.
CONTROL

# === SCRIPT POST-INSTALACIÓN ===
cat > "$DEB_DIR/DEBIAN/postinst" << 'POSTINST'
#!/bin/bash
set -e

# Actualizar caché de iconos
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi

# Actualizar base de datos de aplicaciones
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   ✅ GNS3 AI Studio instalado correctamente  ║"
echo "╠══════════════════════════════════════════════╣"
echo "║                                              ║"
echo "║   Para iniciar:                              ║"
echo "║   • Búscalo en el menú de aplicaciones       ║"
echo "║   • O ejecuta: gns3-ai-studio                ║"
echo "║                                              ║"
echo "║   Primera vez: te pedirá tu API Key de       ║"
echo "║   Anthropic (console.anthropic.com)          ║"
echo "║                                              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
POSTINST
chmod 755 "$DEB_DIR/DEBIAN/postinst"

# === SCRIPT PRE-REMOCIÓN ===
cat > "$DEB_DIR/DEBIAN/prerm" << 'PRERM'
#!/bin/bash
# Detener instancias en ejecución
pkill -f "uvicorn app:app" 2>/dev/null || true
pkill -f "gns3-ai-studio" 2>/dev/null || true
exit 0
PRERM
chmod 755 "$DEB_DIR/DEBIAN/prerm"

# === CONSTRUIR EL .DEB ===
echo ""
echo "🔨 Construyendo el paquete .deb..."
cd "$BUILD_DIR"
dpkg-deb --build --root-owner-group "${APP_NAME}_${APP_VERSION}_amd64"

# === COPIAR AL ESCRITORIO Y AL PROYECTO ===
DEB_FILE="${APP_NAME}_${APP_VERSION}_amd64.deb"
cp "$BUILD_DIR/$DEB_FILE" "$HOME/Desktop/" 2>/dev/null || cp "$BUILD_DIR/$DEB_FILE" "$HOME/"

# === RESUMEN FINAL ===
DEB_SIZE=$(du -h "$BUILD_DIR/$DEB_FILE" | cut -f1)

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   ✅ ¡PAQUETE .DEB CREADO EXITOSAMENTE!              ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║                                                      ║"
echo "║   📦 Archivo: $DEB_FILE"
echo "║   📊 Tamaño: $DEB_SIZE"
echo "║   📍 Ubicación: ~/Desktop/ (o ~/ si no hay desktop)  ║"
echo "║                                                      ║"
echo "║   🚀 Para instalar:                                  ║"
echo "║   sudo dpkg -i $DEB_FILE      "
echo "║                                                      ║"
echo "║   O doble clic en el .deb desde el administrador     ║"
echo "║   de archivos de Ubuntu                              ║"
echo "║                                                      ║"
echo "║   🗑️  Para desinstalar:                              ║"
echo "║   sudo apt remove gns3-ai-studio                     ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
