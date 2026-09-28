# EX3.MC - Alternativa 4.3 - Timbales y guiro
from music import *

# ---------- Configuracion general ----------
tempo = 124
repeticionesIntro = 4
repeticionesA = 12
repeticionesB = 8
repeticionesAprima = 12
repeticionesFinal = 4

score = Score("Alternativa 4.3 - Timbales y guiro", tempo)

# La percusion MIDI utiliza el canal 9.
drumsPart = Part("Percusion house", 0, 9)

# El bajo se mantiene en otra parte y otro canal.
bassPart = Part("Bajo house", ACOUSTIC_BASS, 1)


# Percusion General MIDI: tom de piso grave y tom medio.
FLOOR_TOM = 41
TOM_MEDIO = 47


def variarPercusion(bombo, hiHat, vuelta, repeticiones, seccion):
    """Entrada gradual en A, cambio en B y remates para preparar el regreso."""
    tomBase = [REST, TOM_MEDIO, REST, FLOOR_TOM, REST, REST, TOM_MEDIO, FLOOR_TOM] * 2
    tom = list(tomBase)
    if seccion == "A" and vuelta < 4:
        tom = [REST] * 16
    elif seccion == "A" and vuelta < 8:
        tom[:8] = [REST] * 8
    elif seccion == "Final" and vuelta >= 2:
        tom = [REST] * 16

    # Conserva el kick en cada pulso y refuerza el tom en B.
    # Remate cada ocho compases y antes del cambio; deja espacio al tambor.
    if seccion != "Final" and ((vuelta + 1) % 4 == 0 or vuelta == repeticiones - 1):
        tom[12:] = [TOM_MEDIO, TOM_MEDIO, FLOOR_TOM, FLOOR_TOM]
        bombo[14:] = [REST, REST]

    # Cerrado junto al tom, abierto como respuesta en la corchea siguiente.
    if seccion in ("B", "Aprima") or (seccion == "A" and vuelta >= 4):
        hiHat = [REST] * 16
        for paso in range(16):
            if tom[paso] != REST:
                hiHat[paso] = CHH
            elif paso > 0 and tom[paso - 1] != REST:
                hiHat[paso] = OHH
            elif paso % 2 == 0:
                hiHat[paso] = CHH
    fraseTom.addNoteList(tom, [EN] * 16)
    return bombo, hiHat


# Notas de percusion General MIDI en el canal 9.
# FX: crash (49/57), splash (55) y vibraslap (58).
# 32 semicorcheas = dos compases de 4/4.
# Timbales y guiro: kick sincopado y remate de timbales.
DOBLES = [11, 27]
ABIERTOS = [6, 12, 22, 28]
LATINA = [(4, 65), (10, 66), (14, 65), (20, 66), (26, 65), (30, 66)]
APOYO = [(0, 74), (6, 73), (8, 74), (14, 73), (16, 74), (22, 73), (24, 74), (30, 73)]
REMATE = [65, 65, 66, REST, 65, 66, 65, 66]
FX_ENTRADA = 57
FX_CIERRE = 55


def expandirCorcheas(notas):
    resultado = []
    for nota in notas:
        resultado.extend([nota, REST])
    return resultado


def patronLatino(golpes):
    notas = [REST] * 32
    for paso, instrumento in golpes:
        notas[paso] = instrumento
    return notas


def agregarSaborLatino(bombo, caja, hiHat, vuelta, repeticiones, seccion):
    bombo = expandirCorcheas(bombo)
    caja = expandirCorcheas(caja)
    hiHat = expandirCorcheas(hiHat)
    latina = patronLatino(LATINA)
    apoyo = patronLatino(APOYO)
    efectos = [REST] * 32
    remate = seccion != "Final" and ((vuelta + 1) % 4 == 0 or vuelta == repeticiones - 1)

    # Entrada gradual: deja libre el primer compas al comienzo de A.
    if seccion == "A" and vuelta < 4:
        latina[:16] = [REST] * 16
        apoyo[:16] = [REST] * 16

    # Dos kicks consecutivos separados por una semicorchea.
    if seccion in ("B", "Aprima") or vuelta % 2 == 1:
        for paso in DOBLES:
            bombo[paso - 1] = BDR
            bombo[paso] = BDR
    if 3 == 3 and seccion == "B":
        bombo[4] = REST
        bombo[20] = REST
        bombo[6] = BDR
        bombo[22] = BDR

    for paso in ABIERTOS:
        hiHat[paso] = OHH
        hiHat[paso + 1] = CHH
    if 3 == 4 and seccion == "Aprima":
        for paso in range(1, 32, 4):
            hiHat[paso] = CHH

    if remate:
        latina[24:] = REMATE
        caja[28:] = [SNR, REST, SNR, SNR]
        hiHat[28:] = [CHH, CHH, OHH, CHH]
        efectos[24] = FX_CIERRE
        bombo[28:] = [REST] * 4
    if vuelta == 0 and seccion in ("A", "B", "Aprima"):
        efectos[0] = FX_ENTRADA

    # Retira capas en el cierre.
    if seccion == "Final" and vuelta >= 2:
        latina = [REST] * 32
        apoyo = [REST] * 32
        bombo = [BDR if paso % 4 == 0 else REST for paso in range(32)]
        hiHat = [CHH if paso % 4 == 2 else REST for paso in range(32)]

    fraseLatina.addNoteList(latina, [EN / 2.0] * 32)
    fraseApoyo.addNoteList(apoyo, [EN / 2.0] * 32)
    fraseEfectos.addNoteList(efectos, [EN / 2.0] * 32)
    return bombo, caja, hiHat


def agregarPatron(frase, alturas, duraciones, repeticiones):
    """Agrega el mismo patron a una frase varias veces."""
    for vuelta in range(repeticiones):
        frase.addNoteList(alturas, duraciones)


def agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
                   bomboBase, cajaBase, hiHatBase, bajoBase,
                   durPercusion, durBajo, repeticiones,
                   abrirHiHat, golpeFinal, variarBajo, seccion):
    """Agrega house con variacion ciclica de hi-hat y bajo."""
    notasArmonia = [C2, E2, G2, A2]
    for vuelta in range(repeticiones):
        bombo = list(bomboBase)
        caja = list(cajaBase)
        hiHat = list(hiHatBase)
        bajo = list(bajoBase)

        if abrirHiHat and (vuelta + 1) % 4 == 0:
            hiHat[15] = OHH

        if golpeFinal and vuelta == repeticiones - 1:
            bombo[15] = BDR

        if variarBajo and vuelta % 2 == 0:
            bajo[9] = notasArmonia[vuelta % len(notasArmonia)]

        bombo, hiHat = variarPercusion(bombo, hiHat, vuelta, repeticiones, seccion)

        bombo, caja, hiHat = agregarSaborLatino(
            bombo, caja, hiHat, vuelta, repeticiones, seccion)
        fraseBombo.addNoteList(bombo, [EN / 2.0] * 32)
        fraseCaja.addNoteList(caja, [EN / 2.0] * 32)
        fraseHiHat.addNoteList(hiHat, [EN / 2.0] * 32)
        fraseBajo.addNoteList(bajo, durBajo)


# Cada patron dura 2 compases de 4/4: 16 corcheas.
durDosCompases = [EN] * 16

# ---------- Introduccion: solo pulso principal ----------
bomboIntro = [BDR, REST, BDR, REST, BDR, REST, BDR, REST,
              BDR, REST, BDR, REST, BDR, REST, BDR, REST]
cajaIntro = [REST] * 16
hiHatIntro = [REST, OHH, REST, OHH, REST, OHH, REST, OHH,
              REST, OHH, REST, OHH, REST, OHH, REST, OHH]
bajoIntro = [REST, C2, REST, C2, REST, C2, REST, C2,
             REST, C2, REST, C2, REST, C2, REST, C2]

# ---------- Seccion A: four-on-the-floor house ----------
bomboA = [BDR, REST, BDR, REST, BDR, REST, BDR, REST,
          BDR, REST, BDR, REST, BDR, REST, BDR, REST]
cajaA = [REST, REST, SNR, REST, REST, REST, SNR, REST,
         REST, REST, SNR, REST, REST, REST, SNR, REST]
hiHatA = [CHH, OHH, CHH, OHH, CHH, OHH, CHH, OHH,
          CHH, OHH, CHH, OHH, CHH, OHH, CHH, OHH]
bajoA = [REST, C2, REST, C2, REST, E2, REST, G2,
         REST, C2, REST, E2, REST, G2, REST, E2]

# ---------- Seccion B: menos caja y mas espacio ----------
bomboB = [BDR, REST, BDR, REST, BDR, REST, BDR, REST,
          BDR, REST, BDR, REST, BDR, REST, BDR, REST]
cajaB = [REST, REST, REST, REST, REST, REST, SNR, REST,
         REST, REST, REST, REST, REST, REST, SNR, REST]
hiHatB = [REST, OHH, CHH, OHH, REST, OHH, CHH, OHH,
          REST, OHH, CHH, OHH, REST, OHH, CHH, OHH]
bajoB = [REST, G2, REST, G2, REST, A2, REST, G2,
         REST, E2, REST, E2, REST, G2, REST, A2]

# ---------- Seccion A': regreso con bajo mas activo ----------
bomboAprima = bomboA
cajaAprima = cajaA
hiHatAprima = hiHatA
bajoAprima = [REST, C2, C2, REST, REST, E2, REST, G2,
              REST, C2, E2, REST, REST, G2, A2, REST]

# ---------- Ensamblaje ----------
fraseLatina = Phrase(0.0)
fraseApoyo = Phrase(0.0)
fraseEfectos = Phrase(0.0)
fraseTom = Phrase(0.0)
fraseBombo = Phrase(0.0)
fraseCaja = Phrase(0.0)
fraseHiHat = Phrase(0.0)
fraseBajo = Phrase(0.0)

for fraseNueva in (fraseLatina, fraseApoyo, fraseEfectos):
    agregarPatron(fraseNueva, [REST] * 16, durDosCompases, repeticionesIntro)

agregarPatron(fraseTom, [REST] * 16, durDosCompases, repeticionesIntro)

agregarPatron(fraseBombo, bomboIntro, durDosCompases, repeticionesIntro)
agregarPatron(fraseCaja, cajaIntro, durDosCompases, repeticionesIntro)
agregarPatron(fraseHiHat, hiHatIntro, durDosCompases, repeticionesIntro)
agregarPatron(fraseBajo, bajoIntro, durDosCompases, repeticionesIntro)

agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboA, cajaA, hiHatA, bajoA,
               durDosCompases, durDosCompases, repeticionesA,
               True, True, True, "A")

agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboB, cajaB, hiHatB, bajoB,
               durDosCompases, durDosCompases, repeticionesB,
               True, True, True, "B")

# Remate latino de dos tiempos antes del regreso de A'.
fraseLatina.addNoteList(REMATE, [EN / 2.0] * 8)
fraseApoyo.addNoteList([REST] * 8, [EN / 2.0] * 8)
fraseEfectos.addNoteList([FX_CIERRE] + [REST] * 7, [EN / 2.0] * 8)
fraseTom.addNoteList([TOM_MEDIO, TOM_MEDIO, FLOOR_TOM, FLOOR_TOM], [EN] * 4)
fraseBombo.addNoteList([REST, REST], [QN, QN])
fraseCaja.addNoteList([REST, REST], [QN, QN])
fraseHiHat.addNoteList([REST, REST], [QN, QN])
fraseBajo.addNoteList([REST, REST], [QN, QN])

agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboAprima, cajaAprima, hiHatAprima, bajoAprima,
               durDosCompases, durDosCompases, repeticionesAprima,
               True, True, True, "Aprima")

agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboA, cajaA, hiHatA, bajoA,
               durDosCompases, durDosCompases, repeticionesFinal,
               True, True, True, "Final")

drumsPart.addPhrase(fraseLatina)
drumsPart.addPhrase(fraseApoyo)
drumsPart.addPhrase(fraseEfectos)
drumsPart.addPhrase(fraseTom)
drumsPart.addPhrase(fraseBombo)
drumsPart.addPhrase(fraseCaja)
drumsPart.addPhrase(fraseHiHat)
bassPart.addPhrase(fraseBajo)

score.addPart(drumsPart)
score.addPart(bassPart)

View.sketch(score)
Play.midi(score)
Write.midi(score, "Grupo3_EX3_PrototipoRitmico_alterativa4_3.mid")
