# Cinco alternativas con shaker y drop

## Versiones Jython

Cada alternativa tiene ahora un archivo `.py` independiente, compatible con
Jython 2.7 y ejecutable desde JythonMusic. Abre el archivo deseado y ejecútalo.
Los scripts usan la biblioteca MIDI de Java incluida en Jython; no necesitan
compilar ni ejecutar los archivos `.java`.

- `01_Salsa_Patio.py`
- `02_Salsa_Horizonte.py`
- `03_Funk_Brasileno_Aire.py`
- `04_Funk_Brasileno_Eco.py`
- `05_Reggaeton_Abierto.py`

Cada script reconstruye su arreglo desde el MIDI original de la carpeta superior,
lo guarda como `NOMBRE_Jython.mid` y lo reproduce. Puedes editar `DROP`, `SOLO`,
`REGRESO`, `SEMILLA` y los patrones de percusión. Los tiempos están en pulsos de
negra. El tempo se conserva del MIDI original (124 BPM).
Usa `detener()` en el intérprete para parar la reproducción, o configura
`REPRODUCIR = False` para exportar sin escuchar.

Ejemplo desde la raíz del proyecto con la instalación local:

```powershell
java '-Dpython.cachedir.skip=true' -jar C:/Users/angel/Jython272/jython.jar AlternativasGeneros/01_Salsa_Patio.py --sin-audio
```

Los scripts Jython generan MIDI, no vuelven a renderizar los WAV. La reverberación
del MIDI depende del reproductor; el ambiente estéreo procesado está en los WAV
entregados. Los archivos originales y los WAV se conservan.

## Archivos de audio

Escuchar los WAV en orden del 01 al 05. Cada WAV tiene su MIDI editable.
Se conservan las melodías y el bajo de las versiones originales; la percusión
se adapta a cada alternativa. Tempo: 124 BPM. «3/4 de la canción» se interpreta
como el 75 % de su duración, conservando el compás original.

| Archivo | Carácter | Drop | Piano solo | Regreso |
| --- | --- | --- | --- | --- |
| 01_Salsa_Patio | Salsa, shaker firme y ambiente moderado | 1:50.32 | 1:51.29 | 1:55.16 |
| 02_Salsa_Horizonte | Salsa más espaciosa, respuesta suave del shaker | 1:50.32 | 1:52.26 | 1:58.06 |
| 03_Funk_Brasileno_Aire | Funk brasileño, bombo sincopado y regreso rápido | 1:50.32 | 1:51.29 | 1:55.16 |
| 04_Funk_Brasileno_Eco | Funk brasileño, otro patrón y pausa más larga | 1:50.32 | 1:52.26 | 1:58.06 |
| 05_Reggaeton_Abierto | Dembow y shaker amplio | 1:50.32 | 1:52.26 | 1:56.13 |

En todas las versiones la intensidad disminuye desde 1:44.52 hasta el drop.
Después del corte y la caída de la reverberación queda únicamente el piano;
el bajo y toda la percusión vuelven con mayor intensidad.

El shaker marca cada tiempo, con acentos de caja en 2 y 4 y acentos adicionales
que siguen los ataques del piano. Los WAV usan un shaker de ruido filtrado,
reflexiones estéreo y colas sincronizadas al tempo para sugerir un espacio abierto.
El piano comparte ambiente mediante la reverberación del sintetizador.

Los MIDI incluyen marcadores de estructura, maracas GM como representación del
shaker y control de reverberación CC91. Su sonido depende del reproductor: el
efecto estéreo específico del WAV se procesa al renderizar y no queda incrustado
en el MIDI. Los WAV son estéreo PCM de 16 bits, 22050 Hz, de aproximadamente
2:31.56 incluida la cola final; pico normalizado a aproximadamente -1 dBFS.

## Regeneración

Desde la raíz del proyecto, con Java 11 o posterior en Windows:

```powershell
javac --add-exports java.desktop/com.sun.media.sound=ALL-UNNAMED -d AlternativasGeneros/.build AlternativasGeneros/GenerarAlternativas.java AlternativasGeneros/VerificarAlternativas.java
java --add-exports java.desktop/com.sun.media.sound=ALL-UNNAMED -cp AlternativasGeneros/.build GenerarAlternativas
java -cp AlternativasGeneros/.build VerificarAlternativas
```

Usa los tres MIDI originales de la raíz y el banco de sonido de Windows
`C:/Windows/System32/drivers/gm.dls`. Las semillas fijas permiten reproducir
los resultados. Este comando reemplaza únicamente los cinco pares generados.
