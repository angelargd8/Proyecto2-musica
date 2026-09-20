# EX3.MC - Alternativa 1: Floor tom grave
from music import *

# ---------- Configuracion general ----------
tempo = 124
repeticionesIntro = 4
repeticionesA = 12
repeticionesB = 8
repeticionesAprima = 12
repeticionesFinal = 4

score = Score("Alternativa 1: Floor tom grave", tempo)

# La percusion MIDI utiliza el canal 9.
drumsPart = Part("Percusion house", 0, 9)

# El bajo se mantiene en otra parte y otro canal.
bassPart = Part("Bajo house", ACOUSTIC_BASS, 1)


# Percusion General MIDI: tom de piso grave y tom medio.
FLOOR_TOM = 41
TOM_MEDIO = 47


def variarPercusion(bombo, hiHat, vuelta, repeticiones, seccion):
    """Entrada gradual en A, cambio en B y remates para preparar el regreso."""
    tomBase = [REST, REST, REST, FLOOR_TOM, REST, REST, FLOOR_TOM, REST] * 2
    tom = list(tomBase)
    if seccion == "A" and vuelta < 4:
        tom = [REST] * 16
    elif seccion == "A" and vuelta < 8:
        tom[:8] = [REST] * 8
    elif seccion == "Final" and vuelta >= 2:
        tom = [REST] * 16

    # Conserva el kick en cada pulso y refuerza el tom en B.
    if seccion in ("B", "Aprima"):
        tom[7] = FLOOR_TOM
        tom[15] = FLOOR_TOM
    # Remate cada ocho compases y antes del cambio; deja espacio al tambor.
    if seccion != "Final" and ((vuelta + 1) % 4 == 0 or vuelta == repeticiones - 1):
        tom[12:] = [FLOOR_TOM, REST, FLOOR_TOM, FLOOR_TOM]
        bombo[14:] = [REST, REST]

    # Conserva los hi-hats del prototipo.
    fraseTom.addNoteList(tom, [EN] * 16)
    return bombo, hiHat


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

        fraseBombo.addNoteList(bombo, durPercusion)
        fraseCaja.addNoteList(caja, durPercusion)
        fraseHiHat.addNoteList(hiHat, durPercusion)
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
fraseTom = Phrase(0.0)
fraseBombo = Phrase(0.0)
fraseCaja = Phrase(0.0)
fraseHiHat = Phrase(0.0)
fraseBajo = Phrase(0.0)

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

# Remate de dos tiempos antes del regreso de A'.
fraseTom.addNoteList([FLOOR_TOM, REST, FLOOR_TOM, FLOOR_TOM], [EN] * 4)
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

drumsPart.addPhrase(fraseTom)
drumsPart.addPhrase(fraseBombo)
drumsPart.addPhrase(fraseCaja)
drumsPart.addPhrase(fraseHiHat)
bassPart.addPhrase(fraseBajo)

score.addPart(drumsPart)
score.addPart(bassPart)

View.sketch(score)
Play.midi(score)
Write.midi(score, "Grupo3_EX3_PrototipoRitmico_alterativa1.mid")
