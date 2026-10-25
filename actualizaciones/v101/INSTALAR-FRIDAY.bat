@echo off
title Instalar FRIDAY
cd /d "%~dp0"
echo.
echo   Creando el acceso directo de FRIDAY con su logo...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d=(Get-Location).Path; $w=New-Object -ComObject WScript.Shell; $desk=[Environment]::GetFolderPath('Desktop'); $lnk=Join-Path $desk 'FRIDAY.lnk'; $exe=Join-Path $d 'FRIDAY.exe'; $s=$w.CreateShortcut($lnk); if(Test-Path $exe){ Unblock-File $exe -ErrorAction SilentlyContinue; $s.TargetPath=$exe; $s.Arguments='' } else { $s.TargetPath=(Join-Path $env:WINDIR 'System32\wscript.exe'); $s.Arguments='\"'+$d+'\friday-oculto.vbs\"' }; $s.WorkingDirectory=$d; $s.IconLocation=$d+'\bufalabs.ico'; $s.WindowStyle=7; $s.Description='FRIDAY'; $s.Save(); $start=[Environment]::GetFolderPath('Startup'); Copy-Item $lnk (Join-Path $start 'FRIDAY.lnk') -Force"
if exist "%USERPROFILE%\Desktop\FRIDAY.lnk" (
  echo   Listo! Ya tenes el icono de FRIDAY en el escritorio.
  echo.
  echo   - Abrila con doble clic en ese icono, como cualquier programa.
  echo   - Para anclarla a la barra de tareas: clic derecho en el icono ^> "Anclar a la barra de tareas".
  echo   - Se abre sola al prender la compu. Si no queres eso, deci "sacar del inicio".
  echo.
  echo   Ya podes cerrar esta ventana y abrir FRIDAY.
) else (
  echo   No se pudo crear el acceso directo. Avisale a Claude.
)
echo.
pause
