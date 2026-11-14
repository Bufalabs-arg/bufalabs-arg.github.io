#!/bin/sh
# Instala FRIDAY de BufaLabs en esta compu (Linux). No pide contraseña: queda todo en tu usuario.
#   sh instalar.sh                 instala (o actualiza) y la abre
#   sh instalar.sh --desinstalar   la saca (tus datos quedan en ~/.local/share/FRIDAY)
set -e
DEST="$HOME/.local/share/bufalabs-friday"
APPS="$HOME/.local/share/applications"
AUTO="$HOME/.config/autostart"
DESDE="$(cd "$(dirname "$0")" && pwd)"

if [ "$1" = "--desinstalar" ]; then
  [ -x "$DEST/friday" ] && "$DEST/friday" --apagar 2>/dev/null || true
  rm -f "$APPS/bufalabs-friday.desktop" "$AUTO/bufalabs-friday.desktop"
  rm -rf "$DEST"
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS" 2>/dev/null || true
  echo "Listo: saqué FRIDAY. Tus datos siguen en ~/.local/share/FRIDAY (borralos si querés)."
  exit 0
fi

case "$(uname -m)" in
  x86_64|amd64) ;;
  *) echo "Esta FRIDAY es para compus de 64 bits (Intel o AMD). Esta compu es $(uname -m)."; exit 1 ;;
esac

echo "Instalando FRIDAY…"
# si ya estaba andando, la apagamos para reemplazarla
[ -x "$DEST/friday" ] && "$DEST/friday" --apagar 2>/dev/null && sleep 1 || true
mkdir -p "$DEST" "$APPS" "$AUTO"
if [ "$DESDE" != "$DEST" ]; then
  for f in friday friday-isla friday.html friday.png instalar.sh LEEME.txt; do
    [ -f "$DESDE/$f" ] && cp -f "$DESDE/$f" "$DEST/$f"
  done
fi
chmod +x "$DEST/friday" "$DEST/instalar.sh"; [ -f "$DEST/friday-isla" ] && chmod +x "$DEST/friday-isla"

# en el menú de aplicaciones (clic derecho: Buscar actualizaciones / Apagar FRIDAY)
cat > "$APPS/bufalabs-friday.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=FRIDAY
GenericName=Asistente con inteligencia artificial
Comment=La asistente de BufaLabs: te escucha, te habla y hace cosas de verdad
Exec="$DEST/friday"
Icon=$DEST/friday.png
Terminal=false
Categories=Utility;
Keywords=friday;asistente;bufalabs;ia;
StartupNotify=false
Actions=actualizar;apagar;

[Desktop Action actualizar]
Name=Buscar actualizaciones
Exec="$DEST/friday" --actualizar

[Desktop Action apagar]
Name=Apagar FRIDAY
Exec="$DEST/friday" --apagar
DESK
# que arranque sola al prender la compu (queda atrás)
cat > "$AUTO/bufalabs-friday.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=FRIDAY
Exec="$DEST/friday" --fondo
Icon=$DEST/friday.png
Terminal=false
X-GNOME-Autostart-enabled=true
NoDisplay=true
DESK
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS" 2>/dev/null || true

# FRIDAY se abre en Chrome, Edge, Chromium o Brave (en modo app, como un programa)
NAV=""
for n in microsoft-edge microsoft-edge-stable google-chrome google-chrome-stable chromium chromium-browser brave-browser brave vivaldi-stable vivaldi; do
  command -v "$n" >/dev/null 2>&1 && NAV="$n" && break
done

# lo opcional: manejar ventanas, teclado, música y portapapeles
FALTA=""
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
  for p in playerctl wl-copy; do command -v "$p" >/dev/null 2>&1 || FALTA="$FALTA $p"; done
  command -v ydotool >/dev/null 2>&1 || command -v wtype >/dev/null 2>&1 || FALTA="$FALTA wtype"
else
  for p in wmctrl xdotool playerctl xclip; do command -v "$p" >/dev/null 2>&1 || FALTA="$FALTA $p"; done
fi
FALTA=$(echo "$FALTA" | sed 's/wl-copy/wl-clipboard/')
INST=""
if command -v apt >/dev/null 2>&1; then INST="sudo apt install -y"
elif command -v dnf >/dev/null 2>&1; then INST="sudo dnf install -y"
elif command -v pacman >/dev/null 2>&1; then INST="sudo pacman -S --needed"
elif command -v zypper >/dev/null 2>&1; then INST="sudo zypper install -y"; fi

echo ""
echo "✔ FRIDAY quedó instalada. La encontrás en el menú de aplicaciones y arranca sola al prender la compu."
if [ -z "$NAV" ]; then
  echo ""
  echo "⚠ No encontré Chrome, Edge, Chromium ni Brave. FRIDAY anda mejor en uno de esos (el micrófono y la voz)."
  [ -n "$INST" ] && echo "  Por ejemplo: $INST chromium   (o bajá Chrome de google.com/chrome)"
fi
if [ -n "$FALTA" ]; then
  echo ""
  echo "Para que FRIDAY maneje ventanas, el teclado, la música y el portapapeles faltan:$FALTA"
  if [ -n "$INST" ] && [ -t 0 ]; then
    printf "¿Las instalo ahora? Te va a pedir tu contraseña. [S/n] "
    read -r RESP || RESP="n"
    case "$RESP" in
      n|N|no|NO) echo "  Cuando quieras:  $INST$FALTA" ;;
      *) $INST$FALTA || echo "  No se pudo: probá a mano  $INST$FALTA" ;;
    esac
  elif [ -n "$INST" ]; then echo "  $INST$FALTA"; fi
fi
echo ""
nohup "$DEST/friday" >/dev/null 2>&1 &
echo "Abriendo FRIDAY…"
