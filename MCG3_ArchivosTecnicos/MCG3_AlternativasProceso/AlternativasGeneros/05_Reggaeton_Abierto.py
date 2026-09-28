# -*- coding: utf-8 -*-
"""Alternativa editable para Jython 2.7 / JythonMusic.

Lee el MIDI original de la carpeta superior y reconstruye el arreglo.
No necesita los archivos Java ni los MIDI de alternativas para funcionar.
El ambiente procesado del WAV se conserva en el audio ya entregado;
la reverberacion MIDI depende del sintetizador y su soporte de CC91.
"""
import os
import sys
from java.io import File
from java.lang import Math, String
from java.util import Random
from javax.sound.midi import MidiSystem, Sequence, MidiEvent, ShortMessage, MetaMessage

NOMBRE = '05_Reggaeton_Abierto'
FUENTE = 'Reggaeton'
TIPO = 4
SEMILLA = 505
DROP = 228
SOLO = 232
REGRESO = 240
TEMPO = 124
REPRODUCIR = True


def carpeta_salida():
    # Funciona al ejecutar desde la raiz o desde AlternativasGeneros.
    ruta = globals().get('__file__')
    if ruta:
        return os.path.dirname(os.path.abspath(ruta))
    actual = os.getcwd()
    if os.path.basename(actual).lower() == 'alternativasgeneros':
        return actual
    candidata = os.path.join(actual, 'AlternativasGeneros')
    if os.path.isdir(candidata):
        return candidata
    raise IOError('Ejecuta el archivo desde el proyecto o AlternativasGeneros.')


def mensaje(pista, comando, canal, dato1, dato2, tick):
    m = ShortMessage()
    m.setMessage(comando, canal, int(dato1), int(dato2))
    pista.add(MidiEvent(m, long(tick)))


def marca(pista, tipo, texto, tick):
    datos = String(texto).getBytes('UTF-8')
    m = MetaMessage()
    m.setMessage(tipo, datos, len(datos))
    pista.add(MidiEvent(m, long(tick)))


def nota(pista, canal, altura, volumen, tiempo, duracion, ppq):
    mensaje(pista, 144, canal, altura, max(1, min(127, int(volumen))),
            Math.round(tiempo * ppq))
    mensaje(pista, 128, canal, altura, 0,
            Math.round((tiempo + duracion) * ppq))


def intensidad(tiempo):
    if DROP <= tiempo < REGRESO:
        return 0.0
    if DROP - 12 <= tiempo < DROP:
        return 1.0 - .78 * (tiempo - (DROP - 12)) / 12.0
    return 1.13 if tiempo >= REGRESO else 1.0


def activo(tiempo):
    return not DROP <= tiempo < REGRESO


def golpe(pista, altura, tiempo, volumen, ppq):
    if tiempo < 305 and activo(tiempo):
        nota(pista, 9, altura, int(volumen * intensidad(tiempo)), tiempo, .12, ppq)


def crear_arreglo():
    directorio = carpeta_salida()
    original = os.path.join(os.path.dirname(directorio),
                            'Grupo3_EX3_Piano_Generativo_' + FUENTE + '.mid')
    if not os.path.isfile(original):
        raise IOError('No se encuentra el MIDI original: ' + original)
    fuente = MidiSystem.getSequence(File(original))
    ppq = fuente.getResolution()
    arreglo = Sequence(Sequence.PPQ, ppq)
    conductor = arreglo.createTrack()
    pistas = fuente.getTracks()
    for i in range(pistas[0].size()):
        evento = pistas[0].get(i)
        m = evento.getMessage()
        if not isinstance(m, MetaMessage) or m.getType() != 47:
            conductor.add(MidiEvent(m.clone(), evento.getTick()))
    marca(conductor, 3, NOMBRE, 0)
    for titulo, tiempo in [('Bajada progresiva', DROP - 12),
                           ('DROP: corte del conjunto', DROP),
                           ('Piano solo', SOLO),
                           ('Regreso con toda la energia', REGRESO)]:
        marca(conductor, 6, titulo, tiempo * ppq)

    # Conservar la melodia y el bajo; retirar el pulso house original.
    reemplazados = (35, 36, 38, 40, 42, 44, 46, 70, 82)
    for indice in range(1, len(pistas)):
        entrada = pistas[indice]
        salida = arreglo.createTrack()
        for i in range(entrada.size()):
            evento = entrada.get(i)
            m = evento.getMessage()
            tiempo = evento.getTick() / float(ppq)
            if isinstance(m, MetaMessage):
                if m.getType() != 47:
                    salida.add(MidiEvent(m.clone(), evento.getTick()))
                continue
            if not isinstance(m, ShortMessage):
                continue
            canal, altura = m.getChannel(), m.getData1()
            if m.getCommand() == 128 or (m.getCommand() == 144 and m.getData2() == 0):
                continue
            if m.getCommand() != 144:
                salida.add(MidiEvent(m.clone(), evento.getTick()))
                continue
            if canal == 9 and altura in reemplazados:
                continue
            if DROP <= tiempo < REGRESO and (canal != 2 or tiempo < SOLO):
                continue
            fin = evento.getTick() + ppq // 4
            for j in range(i + 1, entrada.size()):
                siguiente = entrada.get(j)
                q = siguiente.getMessage()
                if (isinstance(q, ShortMessage) and q.getChannel() == canal
                        and q.getData1() == altura and
                        (q.getCommand() == 128 or
                         (q.getCommand() == 144 and q.getData2() == 0))):
                    fin = siguiente.getTick()
                    break
            if tiempo < DROP:
                fin = min(fin, DROP * ppq)
            ganancia = .88 if canal == 2 and SOLO <= tiempo < REGRESO else intensidad(tiempo)
            if canal == 9 and TIPO >= 2:
                ganancia *= .42
            volumen = min(120, max(1, int(Math.round(m.getData2() * ganancia))))
            mensaje(salida, 144, canal, altura, volumen, evento.getTick())
            mensaje(salida, 128, canal, altura, 0, fin)
        canal = 9 if indice == 1 else 1 if indice == 2 else 2
        reverb = 48 if canal == 2 else 24 if canal == 9 else 12
        mensaje(salida, 176, canal, 91, reverb, 0)
        mensaje(salida, 176, canal, 123, 0, DROP * ppq)

    ritmo = arreglo.createTrack()
    marca(ritmo, 3, 'Groove del genero', 0)
    if TIPO < 2:
        bombos, cajas = [0, 1.5, 2.5], [1, 3]
    elif TIPO == 2:
        bombos, cajas = [0, .75, 2, 3.5], [1, 2.5, 3.25]
    elif TIPO == 3:
        bombos, cajas = [0, 1.5, 2.75], [1, 2.5, 3.25]
    else:
        bombos, cajas = [0, 2], [.75, 1.5, 2.75, 3.5]
    for compas in range(0, 306, 4):
        for x in bombos:
            golpe(ritmo, 36, compas + x, 98, ppq)
        for x in cajas:
            golpe(ritmo, 37 if TIPO < 2 else 38, compas + x,
                  67 if TIPO < 2 else 91, ppq)
        for subdivision in range(8):
            x = subdivision * .5
            golpe(ritmo, 42, compas + x, 42 if x % 1 == 0 else 54, ppq)

    shaker = arreglo.createTrack()
    marca(shaker, 3, 'Shaker por tiempo - ambiente exterior', 0)
    azar = Random(SEMILLA)
    ataques = set()
    piano = arreglo.getTracks()[3]
    for i in range(piano.size()):
        evento = piano.get(i)
        m = evento.getMessage()
        if isinstance(m, ShortMessage) and m.getCommand() == 144:
            ataques.add(long(Math.round(evento.getTick() / float(ppq))))
    for tiempo in range(305):
        if activo(tiempo):
            acento = 14 if tiempo % 4 in (1, 3) else 0
            melodia = 9 if tiempo in ataques else 0
            volumen = int((65 + acento + melodia + azar.nextInt(7)) * intensidad(tiempo))
            nota(shaker, 9, 70, volumen, tiempo, .12, ppq)
            if TIPO in (1, 3) and tiempo % 4 == 3 and activo(tiempo + .5):
                nota(shaker, 9, 70, int(volumen * .38), tiempo + .5, .09, ppq)
    marca(conductor, 6, 'Fin', 306 * ppq)
    return arreglo


# Mantener referencias para detener una reproduccion previa desde el editor.
secuenciador = None
sintetizador = None


def detener():
    global secuenciador, sintetizador
    if secuenciador is not None:
        secuenciador.stop()
        secuenciador.close()
        secuenciador = None
    if sintetizador is not None:
        sintetizador.close()
        sintetizador = None


def ejecutar(reproducir=REPRODUCIR):
    global secuenciador, sintetizador
    detener()
    arreglo = crear_arreglo()
    # Sufijo propio para conservar los MIDI y WAV previamente entregados.
    destino = os.path.join(carpeta_salida(), NOMBRE + '_Jython.mid')
    MidiSystem.write(arreglo, 1, File(destino))
    print('Guardado: ' + destino)
    if reproducir:
        sintetizador = MidiSystem.getSynthesizer()
        sintetizador.open()
        secuenciador = MidiSystem.getSequencer(False)
        secuenciador.open()
        secuenciador.getTransmitter().setReceiver(sintetizador.getReceiver())
        secuenciador.setSequence(arreglo)
        secuenciador.start()
        print('Reproduciendo. Usa detener() para parar.')
    return arreglo


if __name__ == '__main__':
    ejecutar(REPRODUCIR and '--sin-audio' not in sys.argv)
