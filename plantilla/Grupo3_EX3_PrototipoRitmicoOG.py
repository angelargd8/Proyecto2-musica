# EX3.MC - Codigo base para percusion y bajo
from music import *

# ---------- Configuracion general ----------
tempo = 120
repeticionesA = 4  # el patron de 2 compases sonara 4 veces

score = Score("Prototipo ritmico para P2.MC", tempo)

# La percusion MIDI utiliza el canal 9.
drumsPart = Part("Percusion", 0, 9)

# El bajo se mantiene en otra parte y otro canal.
bassPart = Part("Bajo", ACOUSTIC_BASS, 1)


def agregarPatron(frase, alturas, duraciones, repeticiones):
    """Agrega el mismo patron a una frase varias veces."""
    for vuelta in range(repeticiones):
        frase.addNoteList(alturas, duraciones)


# ---------- Seccion A: ejemplo de 2 compases en 4/4 ----------
bomboA = [BDR, REST] * 4
durBomboA = [QN, QN] * 4

cajaA = [REST, SNR] * 4
durCajaA = [QN, QN] * 4

hiHatA = [CHH] * 15 + [OHH]
durHiHatA = [EN] * 16

bajoA = [C2, REST, C2, E2, G2, REST, E2, G2]
durBajoA = [QN] * 8

fraseBombo = Phrase(0.0)
fraseCaja = Phrase(0.0)
fraseHiHat = Phrase(0.0)
fraseBajo = Phrase(0.0)

agregarPatron(fraseBombo, bomboA, durBomboA, repeticionesA)
agregarPatron(fraseCaja, cajaA, durCajaA, repeticionesA)
agregarPatron(fraseHiHat, hiHatA, durHiHatA, repeticionesA)
agregarPatron(fraseBajo, bajoA, durBajoA, repeticionesA)


# ---------- Trabajo del equipo ----------
# 1. Sustituir la seccion A por el patron del estilo investigado.
# 2. Crear las secciones B y A' con cambios audibles.
# 3. Incluir una variacion controlada mediante una regla,
#    condicion o eleccion entre posibilidades definidas.
# 4. Extender la estructura completa hasta superar 2 minutos.


# ---------- Ensamblaje y exportacion ----------
drumsPart.addPhrase(fraseBombo)
drumsPart.addPhrase(fraseCaja)
drumsPart.addPhrase(fraseHiHat)
bassPart.addPhrase(fraseBajo)

score.addPart(drumsPart)
score.addPart(bassPart)

View.sketch(score)
Play.midi(score)
#Write.midi(score, "NombreEquipo_EX3_PrototipoRitmico.mid")