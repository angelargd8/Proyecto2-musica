# EX3.MC - Alternativa 4.2 - House Latino con Synth y Voces
from music import *
import random
import math

# =========================================================
# SEMILLAS PARA RESULTADOS REPRODUCIBLES
# =========================================================
SEMILLA_A = 42
SEMILLA_B = 84

# =========================================================
# 1. ALGORITMO GENÉTICO PARA MELODÍAS
# =========================================================

notas_idx = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}
idx_notas = {v: k for k, v in notas_idx.items()}

# Mapeo a constantes de alturas en JythonMusic
notas_pitch_A = {
    'C': C5, 'C#': CS5, 'D': D5, 'D#': DS5, 'E': E5, 'F': F5, 
    'F#': FS5, 'G': G5, 'G#': GS5, 'A': A5, 'A#': AS5, 'B': B5
}

notas_pitch_B = {
    'C': C6, 'C#': CS6, 'D': D6, 'D#': DS6, 'E': E6, 'F': F6, 
    'F#': FS6, 'G': G6, 'G#': GS6, 'A': A6, 'A#': AS6, 'B': B6
}

escala_C = [0, 2, 4, 5, 7, 9, 11]

# Notas permitidas para la melodia generativa:
# Do mayor = C, D, E, F, G, A, B
notas_C_mayor = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

M_melodia_C = [[0] * 12 for _ in range(12)]

for i in escala_C:
    for j in escala_C:
        M_melodia_C[i][j] = 1

for i in escala_C:
    M_melodia_C[i][0] = 2  
    M_melodia_C[i][4] = 2  
    M_melodia_C[i][7] = 2  

duraciones_validas = [0.25, 0.5, 1.0, 2.0]

def generar_melodia(num_notas):
    melodia = []
    for _ in range(num_notas):
        nota = random.choice(notas_C_mayor)
        duracion = random.choice(duraciones_validas)
        melodia.append({'nota': nota, 'duracion': duracion})
    return melodia

def fitness_melodia(melodia, bpm, compass):
    score_val = 0
    num, den = map(int, compass.split('/'))
    tiempos_por_compas = num * (4.0/den)
    tiempo_total = 0

    for i in range(len(melodia)):
        nota_actual = melodia[i]['nota']
        idx_actual = notas_idx[nota_actual]
        tiempo_total += melodia[i]['duracion']

        if idx_actual in escala_C:
            score_val += 1
        else:
            score_val -= 1 

        if i < len(melodia) - 1:
            nota_sig = melodia[i+1]['nota']
            idx_sig = notas_idx[nota_sig]
            score_val += M_melodia_C[idx_actual][idx_sig]

    resto = tiempo_total % tiempos_por_compas
    if resto == 0:
        score_val += 5  
    else:
        score_val -= 2  

    if bpm > 140 and any(n['duracion'] == 0.25 for n in melodia):
        score_val -= 1

    return score_val

def crossover_melodia(mel1, mel2):
    corte = len(mel1) // 2
    return mel1[:corte] + mel2[corte:]

def mutation_melodia(melodia, mutation_rate):
    for i in range(len(melodia)):
        if random.random() < mutation_rate:
            if random.random() < 0.5:
                melodia[i]['nota'] = random.choice(notas_C_mayor)
            else:
                melodia[i]['duracion'] = random.choice(duraciones_validas)
    return melodia

def ga_compositor_melodias(pop_size, iterations, num_notas, bpm, compass, selection_rate, mutation_rate):
    population = []
    sup_index = int(math.ceil(pop_size * selection_rate))

    for _ in range(pop_size):
        ind = generar_melodia(num_notas)
        population.append((ind, fitness_melodia(ind, bpm, compass)))

    for count in range(iterations):
        population = sorted(population, key=lambda x: x[1], reverse=True)[:sup_index]

        while len(population) < pop_size:
            parent1 = random.choice(population[:sup_index])[0]
            parent2 = random.choice(population[:sup_index])[0]
            child = crossover_melodia(parent1, parent2)
            population.append((child, fitness_melodia(child, bpm, compass)))

        for i in range(len(population)):
            ind = population[i][0]
            mutated = mutation_melodia(ind, mutation_rate)
            population[i] = (mutated, fitness_melodia(mutated, bpm, compass))

    best_melodia = sorted(population, key=lambda x: x[1], reverse=True)[0]
    return best_melodia

def ajustar_melodia_a_beats(melodia, dict_pitch, beats_objetivo):
    alturas = []
    duraciones = []
    tiempo_actual = 0.0
    for nota in melodia:
        if tiempo_actual >= beats_objetivo:
            break
        dur = nota['duracion']
        if tiempo_actual + dur > beats_objetivo:
            dur = beats_objetivo - tiempo_actual
        alturas.append(dict_pitch[nota['nota']])
        duraciones.append(dur)
        tiempo_actual += dur
    if tiempo_actual < beats_objetivo:
        alturas.append(REST)
        duraciones.append(beats_objetivo - tiempo_actual)
    return alturas, duraciones

# =========================================================
# 2. PROTOTIPO RÍTMICO Y ENSAMBLAJE GENERAL
# =========================================================

tempo = 124
repeticionesIntro = 4
repeticionesA = 12
repeticionesB = 8
repeticionesAprima = 12
repeticionesFinal = 4

score = Score("House Latino - Piano Salsa GM", tempo)

drumsPart = Part("Percusion house", 0, 9)
bassPart = Part("Bajo house", ACOUSTIC_BASS, 1)
pianoPart = Part("Piano Acustico GM", PIANO, 2)            # Corregido: Synth Square Lead
guitarPart = Part("Guitarra Acustica", 24, 3)       # Corregido: Número de Guitarra
celloPart = Part("Cello Acustico", CELLO, 4)        
vocalsPart = Part("Voces Oohs", 53, 5)              # NUEVO: Voice Oohs

FLOOR_TOM = 41
TOM_MEDIO = 47
SHAKER = 82

def variarPercusion(bombo, hiHat, vuelta, repeticiones, seccion):
    tomBase = [REST, TOM_MEDIO, REST, FLOOR_TOM, REST, REST, TOM_MEDIO, FLOOR_TOM] * 2
    tom = list(tomBase)
    if seccion == "A" and vuelta < 8:
        tom = [REST] * 16
    elif seccion == "Final" and vuelta >= 2:
        tom = [REST] * 16

    if seccion != "Final" and ((vuelta + 1) % 4 == 0 or vuelta == repeticiones - 1):
        tom[12:] = [TOM_MEDIO, TOM_MEDIO, FLOOR_TOM, FLOOR_TOM]
        bombo[14:] = [REST, REST]

    if seccion in ("B", "Aprima") or (seccion == "A" and vuelta >= 8):
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

DOBLES = [7, 23]
ABIERTOS = [2, 10, 18, 26]
LATINA = [(0, 60), (3, 61), (6, 60), (10, 61), (14, 60), (16, 61), (19, 60), (22, 61), (26, 60), (30, 61)]
APOYO = [(0, 56), (6, 56), (10, 56), (16, 56), (22, 56), (28, 56)]
REMATE = [60, 61, REST, 60, 61, 60, 61, REST]
FX_ENTRADA = 55
FX_CIERRE = 58

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

    if seccion == "A" and vuelta < 8:
        latina[:32] = [REST] * 32
        apoyo[:32] = [REST] * 32

    if seccion in ("B", "Aprima") or vuelta % 2 == 1:
        for paso in DOBLES:
            bombo[paso - 1] = BDR
            bombo[paso] = BDR

    for paso in ABIERTOS:
        hiHat[paso] = OHH
        hiHat[paso + 1] = CHH

    if remate:
        latina[24:] = REMATE
        caja[28:] = [SNR, REST, SNR, SNR]
        hiHat[28:] = [CHH, CHH, OHH, CHH]
        efectos[24] = FX_CIERRE
        bombo[28:] = [REST] * 4
    if vuelta == 0 and seccion in ("A", "B", "Aprima"):
        efectos[0] = FX_ENTRADA

    if seccion == "Final" and vuelta >= 2:
        latina = [REST] * 32
        apoyo = [REST] * 32
        bombo = [BDR if paso % 4 == 0 else REST for paso in range(32)]
        hiHat = [CHH if paso % 4 == 2 else REST for paso in range(32)]

    fraseLatina.addNoteList(latina, [EN / 2.0] * 32)
    fraseApoyo.addNoteList(apoyo, [EN / 2.0] * 32)
    fraseEfectos.addNoteList(efectos, [EN / 2.0] * 32)
    return bombo, caja, hiHat

def agregarPatron(frase, alturas, duraciones, repeticiones, dinamica=85):
    for vuelta in range(repeticiones):
        frase.addNoteList(alturas, duraciones, [dinamica]*len(alturas))

def agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
                   bomboBase, cajaBase, hiHatBase, bajoBase,
                   durPercusion, durBajo, repeticiones,
                   abrirHiHat, golpeFinal, variarBajo, seccion):
    notasArmonia = [C2, E2, G2, A2]
    for vuelta in range(repeticiones):
        bombo = list(bomboBase)
        caja = list(cajaBase)
        hiHat = list(hiHatBase)
        bajo = list(bajoBase)

        if seccion == "A":
            if vuelta < 4:
                caja = [REST] * 16
                hiHat = [REST] * 16
            elif vuelta < 8:
                caja = [REST] * 16

        if abrirHiHat and (vuelta + 1) % 4 == 0:
            hiHat[15] = OHH

        if golpeFinal and vuelta == repeticiones - 1:
            bombo[15] = BDR

        if variarBajo and vuelta % 2 == 0:
            bajo[9] = notasArmonia[vuelta % len(notasArmonia)]

        bombo, hiHat = variarPercusion(bombo, hiHat, vuelta, repeticiones, seccion)
        bombo, caja, hiHat = agregarSaborLatino(bombo, caja, hiHat, vuelta, repeticiones, seccion)
        
        fraseBombo.addNoteList(bombo, [EN / 2.0] * 32)
        fraseCaja.addNoteList(caja, [EN / 2.0] * 32)
        fraseHiHat.addNoteList(hiHat, [EN / 2.0] * 32)
        fraseBajo.addNoteList(bajo, durBajo)

# Función para agregar los coros "oooh oooh" en ritmo de blancas (HN)
def agregarCoros(frase, repeticiones, acordes):
    for _ in range(repeticiones):
        # Compás 1: "Oooh" "Oooh"
        frase.addChord(acordes[0], HN)
        frase.addChord(acordes[0], HN)
        # Compás 2: "Oooh" "Oooh"
        frase.addChord(acordes[1], HN)
        frase.addChord(acordes[1], HN)

durDosCompases = [EN] * 16

durIntro = [EN] * 8
bomboIntro = [BDR, REST, REST, REST, BDR, REST, REST, REST] 
cajaIntro = [REST, REST, SNR, REST, REST, REST, SNR, REST]
hiHatIntro = [REST] * 8
shakerIntro = [SHAKER, REST, SHAKER, REST, SHAKER, REST, SHAKER, REST] 
bajoIntro = [REST, C2, REST, C2, REST, C2, REST, C2]

bomboA = [BDR, REST, BDR, REST, BDR, REST, BDR, REST,
          BDR, REST, BDR, REST, BDR, REST, BDR, REST]
cajaA = [REST, REST, SNR, REST, REST, REST, SNR, REST,
         REST, REST, SNR, REST, REST, REST, SNR, REST]
hiHatA = [CHH, OHH, CHH, OHH, CHH, OHH, CHH, OHH,
          CHH, OHH, CHH, OHH, CHH, OHH, CHH, OHH]
bajoA = [REST, C2, REST, C2, REST, E2, REST, G2,
         REST, C2, REST, E2, REST, G2, REST, E2]

bomboB = [BDR, REST, BDR, REST, BDR, REST, BDR, REST,
          BDR, REST, BDR, REST, BDR, REST, BDR, REST]
cajaB = [REST, REST, REST, REST, REST, REST, SNR, REST,
         REST, REST, REST, REST, REST, REST, SNR, REST]
hiHatB = [REST, OHH, CHH, OHH, REST, OHH, CHH, OHH,
          REST, OHH, CHH, OHH, REST, OHH, CHH, OHH]
bajoB = [REST, G2, REST, G2, REST, A2, REST, G2,
         REST, E2, REST, E2, REST, G2, REST, A2]

bomboAprima = bomboA
cajaAprima = cajaA
hiHatAprima = hiHatA
bajoAprima = [REST, C2, C2, REST, REST, E2, REST, G2,
              REST, C2, E2, REST, REST, G2, A2, REST]

fraseLatina = Phrase(0.0)
fraseApoyo = Phrase(0.0)
fraseEfectos = Phrase(0.0)
fraseTom = Phrase(0.0)
fraseBombo = Phrase(0.0)
fraseCaja = Phrase(0.0)
fraseHiHat = Phrase(0.0)
fraseBajo = Phrase(0.0)
frasePiano = Phrase(0.0)
fraseShaker = Phrase(0.0)
fraseGuitarra = Phrase(0.0)
fraseCello = Phrase(0.0)
fraseVoces = Phrase(0.0)

# =========================================================
# 3. GENERACIÓN DE MELODÍAS A y B
# =========================================================

print "Generando melodía A..."
print "Semilla A:", SEMILLA_A
random.seed(SEMILLA_A)

melodia_ga_A, score_A = ga_compositor_melodias(
    pop_size=40, iterations=50, num_notas=16, bpm=tempo, compass='4/4', selection_rate=0.3, mutation_rate=0.05)

print "Generando melodía B (contraste)..."
print "Semilla B:", SEMILLA_B
random.seed(SEMILLA_B)

melodia_ga_B, score_B = ga_compositor_melodias(
    pop_size=40, iterations=50, num_notas=16, bpm=tempo, compass='4/4', selection_rate=0.3, mutation_rate=0.05)

alturas_A, duraciones_A = ajustar_melodia_a_beats(melodia_ga_A, notas_pitch_A, 8.0)
alturas_B, duraciones_B = ajustar_melodia_a_beats(melodia_ga_B, notas_pitch_B, 8.0)

# =========================================================
# PIANO SALSA GENERATIVO
# =========================================================
#
# Conservamos las melodias A y B creadas por el algoritmo
# genetico con las semillas 42 y 84, pero cambiamos su ritmo
# para que el piano tenga una sensacion tipo montuno/salsa.
#
# Patron de 2 compases en corcheas:
#
# X . X X . X . X | X . X X . X . X
#
# El piano empieza en la cuarta corchea de la cancion.

INICIO_PIANO = 3 * EN

GOLPES_PIANO_SALSA = [
    0, 2, 3, 5, 7,
    8, 10, 11, 13, 15
]

PASOS_PIANO_SALSA = 16
DURACION_PASO_PIANO_SALSA = EN


def obtener_alturas_piano(melodia, dict_pitch):
    alturas = []

    for nota in melodia:
        alturas.append(
            dict_pitch[nota['nota']]
        )

    return alturas


def agregarPianoSalsa(
        frase,
        melodia,
        dict_pitch,
        beats_objetivo,
        desplazamiento=0):

    alturas = obtener_alturas_piano(
        melodia,
        dict_pitch
    )

    if len(alturas) == 0:
        frase.addNoteList(
            [REST],
            [beats_objetivo]
        )
        return

    indiceNota = 0
    paso = 0
    tiempoRestante = float(beats_objetivo)

    while tiempoRestante > 0.0001:

        duracion = DURACION_PASO_PIANO_SALSA

        if duracion > tiempoRestante:
            duracion = tiempoRestante

        posicionPatron = (
            paso % PASOS_PIANO_SALSA
        )

        if posicionPatron in GOLPES_PIANO_SALSA:

            indiceReal = (
                desplazamiento + indiceNota
            ) % len(alturas)

            pitch = alturas[indiceReal]
            indiceNota += 1

        else:
            pitch = REST

        frase.addNoteList(
            [pitch],
            [duracion]
        )

        tiempoRestante -= duracion
        paso += 1


# =========================================================
# 4. COMPOSICIÓN CRONOLÓGICA DE SECCIONES
# =========================================================

# Acordes tipo Jazz/Indie para las voces
acordes_voces_A = [[C4, E4, G4, B4], [A3, C4, E4, G4]]  # CMaj7 y Am7
acordes_voces_B = [[F4, A4, C5, E5], [G4, B4, D5, F5]]  # FMaj7 y G7

fraseGuitarra.addNoteList([REST], [176.0])
fraseCello.addNoteList([REST], [176.0])

# --- INTRODUCCIÓN ---
agregarPatron(fraseLatina, [REST] * 8, durIntro, repeticionesIntro)
agregarPatron(fraseApoyo, [REST] * 8, durIntro, repeticionesIntro)
agregarPatron(fraseEfectos, [REST] * 8, durIntro, repeticionesIntro)
agregarPatron(fraseTom, [REST] * 8, durIntro, repeticionesIntro)
agregarPatron(fraseBombo, bomboIntro, durIntro, repeticionesIntro, 40)
agregarPatron(fraseCaja, cajaIntro, durIntro, repeticionesIntro, 40)
agregarPatron(fraseHiHat, hiHatIntro, durIntro, repeticionesIntro, 40)
agregarPatron(fraseBajo, bajoIntro, durIntro, repeticionesIntro, 40)
agregarPatron(fraseShaker, shakerIntro, durIntro, repeticionesIntro, 45)

# Piano salsa: entra en la cuarta corchea.
frasePiano.addNoteList(
    [REST],
    [INICIO_PIANO]
)

duracionIntro = repeticionesIntro * 4.0
duracionPianoIntro = duracionIntro - INICIO_PIANO

agregarPianoSalsa(
    frasePiano,
    melodia_ga_A,
    notas_pitch_A,
    duracionPianoIntro,
    0
)

fraseVoces.addNoteList([REST], [32.0]) # Silencio de voces en la intro

# --- SECCIÓN A (Crescendo) ---
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboA, cajaA, hiHatA, bajoA, durDosCompases, durDosCompases, repeticionesA, True, True, True, "A")
for vuelta in range(repeticionesA):
    agregarPianoSalsa(
        frasePiano,
        melodia_ga_A,
        notas_pitch_A,
        8.0,
        vuelta * 2
    )

# Voces: Entran hasta el compás 9 de la sección A para acompañar el crescendo
fraseVoces.addNoteList([REST], [32.0]) # Silencio las primeras 4 repeticiones (8 compases)
agregarCoros(fraseVoces, 8, acordes_voces_A)

# --- SECCIÓN B (Coro / Clímax) ---
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboB, cajaB, hiHatB, bajoB, durDosCompases, durDosCompases, repeticionesB, True, True, True, "B")
for vuelta in range(repeticionesB):
    agregarPianoSalsa(
        frasePiano,
        melodia_ga_B,
        notas_pitch_B,
        8.0,
        vuelta * 3
    )

agregarCoros(fraseVoces, 8, acordes_voces_B)

# --- SECCIÓN ACÚSTICA (Descanso) ---
for pistaElect in (fraseLatina, fraseApoyo, fraseEfectos, fraseTom, fraseBombo, fraseCaja, fraseHiHat, fraseBajo, fraseShaker):
    pistaElect.addNoteList([REST], [32.0])
frasePiano.addNoteList([REST], [32.0])

acordes_acusticos = [[C4, E4, G4], [G3, B3, D4], [A3, C4, E4], [F3, A3, C4]]
linea_cello = [C3, G2, A2, F2]

# Progresión envolvente de 8 compases con Guitarra, Cello y Voces
for _ in range(2):
    for acorde in acordes_acusticos:
        fraseGuitarra.addChord(acorde, WN)
        # Las voces acompañan a la guitarra diciendo "Oooh Oooh" por acorde
        fraseVoces.addChord(acorde, HN)
        fraseVoces.addChord(acorde, HN)
    fraseCello.addNoteList(linea_cello, [WN, WN, WN, WN])

# --- REMATE LATINO ---
fraseLatina.addNoteList(REMATE, [EN / 2.0] * 8)
fraseApoyo.addNoteList([REST] * 8, [EN / 2.0] * 8)
fraseEfectos.addNoteList([FX_CIERRE] + [REST] * 7, [EN / 2.0] * 8)
fraseTom.addNoteList([TOM_MEDIO, TOM_MEDIO, FLOOR_TOM, FLOOR_TOM], [EN] * 4)
fraseBombo.addNoteList([REST, REST], [QN, QN])
fraseCaja.addNoteList([REST, REST], [QN, QN])
fraseHiHat.addNoteList([REST, REST], [QN, QN])
fraseBajo.addNoteList([REST, REST], [QN, QN])
frasePiano.addNoteList([REST], [2.0])
fraseVoces.addNoteList([REST], [2.0])

# --- SECCIÓN A PRIMA ---
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboAprima, cajaAprima, hiHatAprima, bajoAprima, durDosCompases, durDosCompases, repeticionesAprima, True, True, True, "Aprima")
for vuelta in range(repeticionesAprima):
    agregarPianoSalsa(
        frasePiano,
        melodia_ga_A,
        notas_pitch_A,
        8.0,
        4 + vuelta * 3
    )
agregarCoros(fraseVoces, repeticionesAprima, acordes_voces_A)

# --- SECCIÓN FINAL ---
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboA, cajaA, hiHatA, bajoA, durDosCompases, durDosCompases, repeticionesFinal, True, True, True, "Final")
for vuelta in range(repeticionesFinal):
    agregarPianoSalsa(
        frasePiano,
        melodia_ga_A,
        notas_pitch_A,
        8.0,
        2 + vuelta * 4
    )
agregarCoros(fraseVoces, repeticionesFinal, acordes_voces_A)

# =========================================================
# 5. ENSAMBLAJE FINAL
# =========================================================
drumsPart.addPhrase(fraseLatina)
drumsPart.addPhrase(fraseApoyo)
drumsPart.addPhrase(fraseEfectos)
drumsPart.addPhrase(fraseTom)
drumsPart.addPhrase(fraseBombo)
drumsPart.addPhrase(fraseCaja)
drumsPart.addPhrase(fraseHiHat)
drumsPart.addPhrase(fraseShaker) 
bassPart.addPhrase(fraseBajo)
pianoPart.addPhrase(frasePiano) 
guitarPart.addPhrase(fraseGuitarra)
celloPart.addPhrase(fraseCello)
vocalsPart.addPhrase(fraseVoces) # Agregando las voces a la partitura

score.addPart(drumsPart)
score.addPart(bassPart)
score.addPart(pianoPart)
score.addPart(guitarPart)
score.addPart(celloPart)
#score.addPart(vocalsPart)

View.sketch(score)
Play.midi(score)
#Write.midi(score, "Grupo3_EX3_HouseLatino_PianoSalsa_GM_Seeded.mid")


# # =========================================================
# # STEM DE TODA LA BATERIA
# # =========================================================

# drumsStemScore = Score(
#     "Stem Bateria Completa",
#     tempo
# )

# drumsStemPart = Part(
#     "Bateria Completa",
#     0,
#     9
# )

# drumsStemPart.addPhrase(fraseLatina)
# drumsStemPart.addPhrase(fraseApoyo)
# drumsStemPart.addPhrase(fraseEfectos)
# drumsStemPart.addPhrase(fraseTom)
# drumsStemPart.addPhrase(fraseBombo)
# drumsStemPart.addPhrase(fraseCaja)
# drumsStemPart.addPhrase(fraseHiHat)
# drumsStemPart.addPhrase(fraseShaker)

# drumsStemScore.addPart(
#     drumsStemPart
# )

# Write.midi(
#     drumsStemScore,
#     "Stem_Bateria_Completa.mid"
# )