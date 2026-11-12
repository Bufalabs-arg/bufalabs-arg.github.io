#!/bin/sh
# FRIDAY para Linux — BufaLabs
# Se instala en tu usuario (no pide contraseña): queda en el menú de aplicaciones y arranca sola al prender la compu.
#   curl -fsSL https://bufalabs-arg.github.io/linux/instalar.sh | sh
#   curl -fsSL https://bufalabs-arg.github.io/linux/instalar.sh | sh -s -- --desinstalar
set -e
TGZ="https://bufalabs-arg.github.io/descargas/FRIDAY-linux.tar.gz"
DEST="$HOME/.local/share/bufalabs-friday"

if [ "$(uname)" != "Linux" ]; then
  echo "Este instalador es para Linux. Para Windows y Mac: https://bufalabs-arg.github.io/instalar/"
  exit 1
fi
if [ "$1" = "--desinstalar" ]; then
  if [ -f "$DEST/instalar.sh" ]; then sh "$DEST/instalar.sh" --desinstalar; else echo "FRIDAY no estaba instalada."; fi
  exit 0
fi
case "$(uname -m)" in
  x86_64|amd64) ;;
  *) echo "Esta FRIDAY es para compus de 64 bits (Intel o AMD). Esta compu es $(uname -m)."; exit 1 ;;
esac

echo "Bajando FRIDAY…"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if command -v curl >/dev/null 2>&1; then curl -fsSL "$TGZ" -o "$TMP/FRIDAY-linux.tar.gz"
else wget -qO "$TMP/FRIDAY-linux.tar.gz" "$TGZ"; fi
tar xzf "$TMP/FRIDAY-linux.tar.gz" -C "$TMP"
# que el instalador pueda preguntarte (aunque esto venga por un caño desde curl)
if [ -t 1 ] && [ -r /dev/tty ]; then sh "$TMP/FRIDAY/instalar.sh" < /dev/tty; else sh "$TMP/FRIDAY/instalar.sh"; fi
