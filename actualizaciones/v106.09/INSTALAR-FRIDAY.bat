@echo off
cd /d "%~dp0"
if /i "%~1"=="isla" goto isla
tasklist /fi "imagename eq FRIDAY.exe" 2>nul | find /i "FRIDAY.exe" >nul && (start "" /min cmd /c ""%~f0" isla" & exit /b)
title Instalar FRIDAY
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
echo   Instalando la isla de arriba de la pantalla...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$log=Join-Path $env:LOCALAPPDATA 'FRIDAY\isla-instalar.txt'; try { $ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $ProgressPreference='SilentlyContinue'; function Huella($p){ $s=[Security.Cryptography.SHA256]::Create(); try { [BitConverter]::ToString($s.ComputeHash([IO.File]::ReadAllBytes($p))).Replace('-','') } finally { $s.Dispose() } }; $h='9FA2FB709BA378E36FD17BBBF5195560B75F56C27A2EF0BC5E371342A6887D8D'; $d=Join-Path $env:LOCALAPPDATA 'FRIDAY\isla'; New-Item -ItemType Directory -Force $d | Out-Null; $f=Join-Path $d 'FRIDAY-Isla-1.0.exe'; $aca=Join-Path (Get-Location).Path 'FRIDAY-Isla-1.0.exe'; if(-not (Test-Path $f) -or (Huella $f) -ne $h){ $t=$f+'.tmp'; if((Test-Path $aca) -and (Huella $aca) -eq $h){ Copy-Item $aca $t -Force } else { Invoke-WebRequest 'https://bufalabs-arg.github.io/descargas/FRIDAY-Isla-1.0.exe' -OutFile $t -UseBasicParsing }; if((Huella $t) -ne $h){ Remove-Item $t -Force; throw 'la isla bajada no coincide' }; Move-Item $t $f -Force }; Unblock-File $f -ErrorAction SilentlyContinue; Start-Process $f -ArgumentList '--fondo'; (Get-Date).ToString('s')+' isla instalada y abierta' | Out-File $log -Append } catch { (Get-Date).ToString('s')+' no pude instalar la isla: '+$_ | Out-File $log -Append }"
echo.
pause

exit /b

:isla
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "$log=Join-Path $env:LOCALAPPDATA 'FRIDAY\isla-instalar.txt'; try { $ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $ProgressPreference='SilentlyContinue'; function Huella($p){ $s=[Security.Cryptography.SHA256]::Create(); try { [BitConverter]::ToString($s.ComputeHash([IO.File]::ReadAllBytes($p))).Replace('-','') } finally { $s.Dispose() } }; $h='9FA2FB709BA378E36FD17BBBF5195560B75F56C27A2EF0BC5E371342A6887D8D'; $d=Join-Path $env:LOCALAPPDATA 'FRIDAY\isla'; New-Item -ItemType Directory -Force $d | Out-Null; $f=Join-Path $d 'FRIDAY-Isla-1.0.exe'; $aca=Join-Path (Get-Location).Path 'FRIDAY-Isla-1.0.exe'; if(-not (Test-Path $f) -or (Huella $f) -ne $h){ $t=$f+'.tmp'; if((Test-Path $aca) -and (Huella $aca) -eq $h){ Copy-Item $aca $t -Force } else { Invoke-WebRequest 'https://bufalabs-arg.github.io/descargas/FRIDAY-Isla-1.0.exe' -OutFile $t -UseBasicParsing }; if((Huella $t) -ne $h){ Remove-Item $t -Force; throw 'la isla bajada no coincide' }; Move-Item $t $f -Force }; Unblock-File $f -ErrorAction SilentlyContinue; Start-Process $f -ArgumentList '--fondo'; (Get-Date).ToString('s')+' isla instalada y abierta' | Out-File $log -Append } catch { (Get-Date).ToString('s')+' no pude instalar la isla: '+$_ | Out-File $log -Append }"
exit /b
