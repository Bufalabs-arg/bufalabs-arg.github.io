# FRIDAY para Android (el APK)

Esta carpeta arma **FRIDAY.apk**: la app de Android de FRIDAY.

Por dentro es una **ventana de Chrome sin barra de dirección** (lo que Google llama *Trusted Web
Activity*) que abre <https://bufalabs-arg.github.io/app/>. O sea: es la misma FRIDAY de siempre,
con el motor de Chrome, así que la voz, el micrófono, la cámara, los avisos y todo lo demás andan
igual que en el navegador. La app no guarda nada adentro: todo vive en la página.

## Las piezas

| Dónde | Qué hace |
| --- | --- |
| `android/` | el proyecto de Android (Gradle) |
| `app/` | el espejo de FRIDAY Móvil, que es lo que abre la app |
| `.well-known/assetlinks.json` | acá el dominio dice «esta app es mía», y por eso se abre sin barra |
| `.github/workflows/apk.yml` | arma el APK **sin firmar** |
| `.github/workflows/espejo-movil.yml` | mantiene `/app/` al día con FRIDAY Móvil |
| `descargas/FRIDAY.apk` | el APK firmado que se baja la gente |

## Cómo se arma

1. GitHub arma el APK sin firmar (`apk.yml`) y lo deja como resultado de la corrida
   (`friday-apk`: `FRIDAY-sin-firmar.apk` y `apksigner.jar`).
2. BufaLabs lo firma aparte, con su clave:

   ```sh
   java -jar apksigner.jar sign --ks friday-android.p12 --ks-key-alias friday \
        --out FRIDAY.apk FRIDAY-sin-firmar.apk
   java -jar apksigner.jar verify -v FRIDAY.apk
   ```

3. El APK firmado se guarda en `descargas/FRIDAY.apk`.

**La clave de firma no está en este repositorio ni en GitHub**, y no se publica nunca. Si se
cambiara, habría que poner la huella nueva en `.well-known/assetlinks.json` (se pueden tener
varias a la vez, así las apps ya instaladas siguen andando).

## Cómo saber que el APK es el nuestro

Android revisa solo la firma: si alguien te pasa otro FRIDAY.apk firmado con otra clave, no se
instala encima del nuestro. La huella de la firma de BufaLabs es

    3C:3F:12:91:DA:AA:9B:55:56:16:E8:C4:56:98:04:4D:C6:C8:3A:A9:BC:39:9A:FB:6C:13:0A:3F:6F:D8:2F:98

(la misma que está en `.well-known/assetlinks.json`), y se mira con
`java -jar apksigner.jar verify -v --print-certs FRIDAY.apk`.

## Si algún día cambia la dirección

`android/app/build.gradle` tiene `launchUrl` y `hostName`, y el `AndroidManifest.xml` usa ese
mismo host para que los enlaces de FRIDAY abran la app. Cambiá los dos y volvé a armar.
