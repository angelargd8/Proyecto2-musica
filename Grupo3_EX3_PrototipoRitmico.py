# EX3.MC - Prototipo ritmico: House
from music import *

# ---------- Configuracion general ----------
tempo = 124
repeticionesIntro = 4
repeticionesA = 12
repeticionesB = 8
repeticionesAprima = 12
repeticionesFinal = 4

score = Score("Prototipo ritmico house para P2.MC", tempo)

# La percusion MIDI utiliza el canal 9.
drumsPart = Part("Percusion house", 0, 9)

# El bajo se mantiene en otra parte y otro canal.
bassPart = Part("Bajo house", ACOUSTIC_BASS, 1)

marimbaPart = Part("Marimba", MARIMBA, 2)

rhodesPart = Part("Rhodes", RHODES, 3)


def agregarPatron(frase, alturas, duraciones, repeticiones):
    """Agrega el mismo patron a una frase varias veces."""
    for vuelta in range(repeticiones):
        frase.addNoteList(alturas, duraciones)


def agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
                   bomboBase, cajaBase, hiHatBase, bajoBase,
                   durPercusion, durBajo, repeticiones,
                   abrirHiHat, golpeFinal, variarBajo):
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

        fraseBombo.addNoteList(bombo, durPercusion)
        fraseCaja.addNoteList(caja, durPercusion)
        fraseHiHat.addNoteList(hiHat, durPercusion)
        fraseBajo.addNoteList(bajo, durBajo)


# Cada patron dura 2 compases de 4/4: 16 corcheas.
durDosCompases = [EN] * 16

# ---------- Armonia ----------
acordeC = [G4, C5, E5]
acordeG = [G4, B4, D5]
acordeAm = [A4, C5, E5]
acordeF = [A4, C5, F5]
acordeC_R = [E4, G4, C5]
acordeG_R = [D4, G4, B4]
acordeAm_R = [E4, A4, C5]
acordeF_R = [C4, F4, A4]

# ---------- Introduccion: solo pulso principal ----------
marimbaIntro1 = [C5, REST, REST, REST, E5, REST, REST, REST,
                 G5, REST, REST, REST, E5, REST, REST, REST]
marimbaIntro2 = [C5, REST, E5, REST, G5, REST, E5, REST,
                 C5, E5, G5, E5, D5, REST, E5, REST]
marimbaIntro3 = [C5, E5, G5, E5, C5, E5, G5, B5, 
                 A5, E5, C5, E5, A5, C5, E5, G5]

# ---------- Seccion A: four-on-the-floor house ----------
bomboA = [BDR, REST, BDR, REST, BDR, REST, BDR, REST,
          BDR, REST, BDR, REST, BDR, REST, BDR, REST]
cajaA = [REST, REST, SNR, REST, REST, REST, SNR, REST,
         REST, REST, SNR, REST, REST, REST, SNR, REST]
hiHatA = [CHH, OHH, CHH, OHH, CHH, OHH, CHH, OHH,
          CHH, OHH, CHH, OHH, CHH, OHH, CHH, OHH]
bajoA = [REST, C2, REST, C2, REST, E2, REST, G2,
         REST, C2, REST, E2, REST, G2, REST, E2]
marimbaRespuestaA = [REST, REST, REST, REST, REST, REST, REST, REST, 
                    G5, REST, E5, REST, C5, REST, E5, REST]
rhodesA1 = [
    REST, acordeC_R, REST, REST,
    REST, acordeC_R, REST, REST,
    REST, acordeG_R, REST, REST,
    REST, acordeG_R, REST, REST
]

rhodesA2 = [
    REST, acordeAm_R, REST, REST,
    REST, acordeAm_R, REST, REST,
    REST, acordeF_R, REST, REST,
    REST, acordeF_R, REST, REST
]

# ---------- Seccion B: menos caja y mas espacio ----------
bomboB = [BDR, REST, BDR, REST, BDR, REST, BDR, REST,
          BDR, REST, BDR, REST, BDR, REST, BDR, REST]
cajaB = [REST, REST, REST, REST, REST, REST, SNR, REST,
         REST, REST, REST, REST, REST, REST, SNR, REST]
hiHatB = [REST, OHH, CHH, OHH, REST, OHH, CHH, OHH,
          REST, OHH, CHH, OHH, REST, OHH, CHH, OHH]
bajoB = [REST, G2, REST, G2, REST, A2, REST, G2,
         REST, E2, REST, E2, REST, G2, REST, A2]
marimbaRespuestaB = [A4, REST, C5, REST, E5, C5, REST, REST, 
            F4, REST, A4, REST, C5, A4, REST, REST]
rhodesB1 = [acordeAm_R, REST, REST, REST, acordeAm_R, REST, REST, REST,
            acordeF_R, REST, REST, REST, acordeF_R, REST, REST, REST]
rhodesB2 = [acordeC_R, REST, REST, REST, acordeC_R, REST, REST, REST,
            acordeG_R, REST, REST, REST, acordeG_R, REST, REST, REST]

# ---------- Seccion A': regreso con bajo mas activo ----------
bomboAprima = bomboA
cajaAprima = cajaA
hiHatAprima = hiHatA
bajoAprima = [REST, C2, C2, REST, REST, E2, REST, G2,
              REST, C2, E2, REST, REST, G2, A2, REST]
marimbaRespuestaAprima = [REST, REST, REST, REST, E5, REST, G5, REST,
                          A5, REST, G5, E5, C5, REST, E5, G5]
rhodesAprima1 = [
    REST, acordeC_R, REST, REST,
    acordeC_R, REST, REST, REST,
    REST, acordeG_R, REST, REST,
    acordeG_R, REST, REST, REST
]

rhodesAprima2 = [
    REST, acordeAm_R, REST, REST,
    acordeAm_R, REST, REST, REST,
    REST, acordeF_R, REST, REST,
    acordeF_R, REST, REST, REST
]

# ---------- Ensamblaje ----------
fraseBombo = Phrase(0.0)
fraseCaja = Phrase(0.0)
fraseHiHat = Phrase(0.0)
fraseBajo = Phrase(0.0)
fraseMarimba = Phrase(0.0)
fraseRhodes = Phrase(0.0)

# ---------- INTRO ----------

# El resto de instrumentos permanece en silencio durante 8 compases.
silencioIntro = [REST] * 16

agregarPatron(fraseBombo, silencioIntro, durDosCompases, 4)
agregarPatron(fraseCaja, silencioIntro, durDosCompases, 4)
agregarPatron(fraseHiHat, silencioIntro, durDosCompases, 4)
agregarPatron(fraseBajo, silencioIntro, durDosCompases, 4)
agregarPatron(fraseRhodes, silencioIntro, durDosCompases, 4)

agregarPatron(fraseMarimba, marimbaIntro1, durDosCompases, 1)
agregarPatron(fraseMarimba, marimbaIntro2, durDosCompases, 3)

# ---------- SECCION A ----------
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboA, cajaA, hiHatA, bajoA,
               durDosCompases, durDosCompases, repeticionesA,
               True, True, True)
for i in range(repeticionesA):
    if (i + 1) % 3 == 0:
        agregarPatron(
            fraseMarimba,
            marimbaRespuestaA,
            durDosCompases,
            1
        )
    else:
        agregarPatron(
            fraseMarimba,
            silencioIntro,
            durDosCompases,
            1
        )
for i in range(6):
    agregarPatron(fraseRhodes, rhodesA1, durDosCompases, 1)
    agregarPatron(fraseRhodes, rhodesA2, durDosCompases, 1)

# ---------- SECCION B ----------
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboB, cajaB, hiHatB, bajoB,
               durDosCompases, durDosCompases, repeticionesB,
               True, True, True)
for i in range(repeticionesB):
    if (i + 1) % 2 == 0:
        agregarPatron(
            fraseMarimba,
            marimbaRespuestaB,
            durDosCompases,
            1
        )
    else:
        agregarPatron(
            fraseMarimba,
            silencioIntro,
            durDosCompases,
            1
        )
for i in range(4):
    agregarPatron(fraseRhodes, rhodesB1, durDosCompases, 1)
    agregarPatron(fraseRhodes, rhodesB2, durDosCompases, 1)

# Breve silencio antes del regreso de A'.
fraseBombo.addNoteList([REST, REST], [QN, QN])
fraseCaja.addNoteList([REST, REST], [QN, QN])
fraseHiHat.addNoteList([REST, REST], [QN, QN])
fraseBajo.addNoteList([REST, REST], [QN, QN])
fraseMarimba.addNoteList([REST, REST], [QN, QN])
fraseRhodes.addNoteList([REST, REST], [QN, QN])

# ---------- SECCION A' ----------
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboAprima, cajaAprima, hiHatAprima, bajoAprima,
               durDosCompases, durDosCompases, repeticionesAprima,
               True, True, True)
for i in range(repeticionesAprima):
    if (i + 1) % 2 == 0:
        agregarPatron(
            fraseMarimba,
            marimbaRespuestaAprima,
            durDosCompases,
            1
        )
    else:
        agregarPatron(
            fraseMarimba,
            silencioIntro,
            durDosCompases,
            1
        )
for i in range(6):
    agregarPatron(fraseRhodes, rhodesAprima1, durDosCompases, 1)
    agregarPatron(fraseRhodes, rhodesAprima2, durDosCompases, 1)

# ---------- SECCION FINAL ----------
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboA, cajaA, hiHatA, bajoA,
               durDosCompases, durDosCompases, repeticionesFinal,
               True, True, True)
for i in range(repeticionesFinal):
    if i == repeticionesFinal - 1:
        agregarPatron(
            fraseMarimba,
            marimbaRespuestaA,
            durDosCompases,
            1
        )
    else:
        agregarPatron(
            fraseMarimba,
            silencioIntro,
            durDosCompases,
            1
        )
for i in range(2):
    agregarPatron(fraseRhodes, rhodesA1, durDosCompases, 1)
    agregarPatron(fraseRhodes, rhodesA2, durDosCompases, 1)

drumsPart.addPhrase(fraseBombo)
drumsPart.addPhrase(fraseCaja)
drumsPart.addPhrase(fraseHiHat)
bassPart.addPhrase(fraseBajo)
marimbaPart.addPhrase(fraseMarimba)
rhodesPart.addPhrase(fraseRhodes)
fraseRhodes.setDynamic(35)

score.addPart(drumsPart)
score.addPart(bassPart)
score.addPart(marimbaPart)
score.addPart(rhodesPart)
View.sketch(score)
# Play.midi(score)
Write.midi(score, "Grupo3_EX3_PrototipoRitmico_Prueba_Rhodes1.mid")
