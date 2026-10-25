@echo off
cd /d "%~dp0"
echo.
echo  Instalando la voz de FRIDAY (Daniela, espanol argentino).
echo  Son unos 130 MB: puede tardar unos minutos. No cierres esta ventana.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $ProgressPreference='SilentlyContinue'; New-Item -ItemType Directory -Force voz | Out-Null; Write-Host ' 1/3 Programa de voz...'; Invoke-WebRequest 'https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip' -OutFile 'voz\piper.zip'; Expand-Archive -Force 'voz\piper.zip' 'voz'; Remove-Item 'voz\piper.zip'; Write-Host ' 2/3 Voz de Daniela...'; Invoke-WebRequest 'https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_AR/daniela/high/es_AR-daniela-high.onnx' -OutFile 'voz\es_AR-daniela-high.onnx'; Write-Host ' 3/3 Configuracion...'; Invoke-WebRequest 'https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_AR/daniela/high/es_AR-daniela-high.onnx.json' -OutFile 'voz\es_AR-daniela-high.onnx.json'"
echo.
set OK=0
if exist "voz\piper\piper.exe" if exist "voz\es_AR-daniela-high.onnx" set OK=1
if "%OK%"=="1" (
  echo  Listo! Cerra FRIDAY y abrila de nuevo desde su icono
  echo  y en Ajustes, Voz y oido, elegi Daniela.
) else (
  echo  Algo fallo en la descarga. Revisa tu internet y proba de nuevo.
)
echo.
pause
