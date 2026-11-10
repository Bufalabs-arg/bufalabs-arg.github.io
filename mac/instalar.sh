#!/bin/sh
# FRIDAY para Mac — BufaLabs
# Se instala en tu usuario (no pide contraseña): queda en Aplicaciones de tu carpeta y arranca sola al prender la Mac.
#   curl -fsSL https://bufalabs-arg.github.io/mac/instalar.sh | sh
#   curl -fsSL https://bufalabs-arg.github.io/mac/instalar.sh | sh -s -- --desinstalar
set -e
ZIP="https://bufalabs-arg.github.io/descargas/FRIDAY-mac.zip"
DEST="$HOME/Applications"
APP="$DEST/FRIDAY.app"
AGENTE="$HOME/Library/LaunchAgents/ar.bufalabs.friday.plist"

if [ "$(uname)" != "Darwin" ]; then
  echo "Este instalador es para Mac. Para Windows y Linux: https://bufalabs-arg.github.io/instalar/"
  exit 1
fi

apagar() {
  [ -x "$APP/Contents/MacOS/friday" ] && "$APP/Contents/MacOS/friday" --apagar >/dev/null 2>&1 || true
  launchctl bootout "gui/$(id -u)" "$AGENTE" >/dev/null 2>&1 || true
}

if [ "$1" = "--desinstalar" ]; then
  apagar
  rm -rf "$APP" "$AGENTE"
  echo "Listo: saqué FRIDAY. Tus datos siguen en ~/Library/Application Support/FRIDAY (borralos si querés)."
  exit 0
fi

VER="$(sw_vers -productVersion | cut -d. -f1)"
if [ "$VER" -lt 11 ] 2>/dev/null; then
  echo "FRIDAY necesita macOS 11 (Big Sur) o más nuevo. Esta Mac tiene $(sw_vers -productVersion)."
  exit 1
fi

echo "Bajando FRIDAY…"
TMP="$(mktemp -d)"
curl -fsSL "$ZIP" -o "$TMP/FRIDAY-mac.zip"
apagar
mkdir -p "$DEST"
rm -rf "$APP"
ditto -x -k "$TMP/FRIDAY-mac.zip" "$DEST"
rm -rf "$TMP"
# bajada con curl no queda «en cuarentena»; por las dudas, y la firma local para que la Mac la abra
xattr -dr com.apple.quarantine "$APP" >/dev/null 2>&1 || true
codesign --force --deep -s - "$APP" >/dev/null 2>&1 || true

# que arranque sola al prender la Mac (queda atrás, sin ventana)
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$AGENTE" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key><string>ar.bufalabs.friday</string>
	<key>ProgramArguments</key>
	<array><string>$APP/Contents/MacOS/friday</string><string>--servidor-fondo</string></array>
	<key>RunAtLoad</key><true/>
	<key>LimitLoadToSessionType</key><string>Aqua</string>
</dict>
</plist>
PLIST
launchctl bootstrap "gui/$(id -u)" "$AGENTE" >/dev/null 2>&1 || true

echo ""
echo "✔ FRIDAY quedó instalada en Aplicaciones (la de tu carpeta) y arranca sola al prender la Mac."
NAV=""
for n in "Google Chrome" "Microsoft Edge" "Brave Browser" "Chromium" "Vivaldi" "Opera"; do
  if [ -d "/Applications/$n.app" ] || [ -d "$HOME/Applications/$n.app" ]; then NAV="$n"; break; fi
done
if [ -z "$NAV" ]; then
  echo ""
  echo "⚠ No encontré Chrome, Edge ni Brave. FRIDAY se abre en Safari, pero la voz y el micrófono andan"
  echo "  mucho mejor en Chrome: bajalo gratis de google.com/chrome y abrí FRIDAY de nuevo."
fi
echo ""
echo "La primera vez la Mac te va a pedir permisos (micrófono, Calendario, Accesibilidad…): decile que sí."
sleep 1
open "$APP"
echo "Abriendo FRIDAY…"
