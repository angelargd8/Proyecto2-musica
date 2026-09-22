# EX3.MC - Alternativa 4.2 - Bongos, campana y Melodias GA A/B en Piano
from music import *
import random
import math

# =========================================================
# 1. ALGORITMO GENÉTICO PARA MELODÍAS (Adaptado sin Numpy)
# =========================================================

notas_idx = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}
idx_notas = {v: k for k, v in notas_idx.items()}

# Mapeo a constantes de alturas en JythonMusic (Octava 5 para A, Octava 6 para B)
notas_pitch_A = {
    'C': C5, 'C#': CS5, 'D': D5, 'D#': DS5, 'E': E5, 'F': F5, 
    'F#': FS5, 'G': G5, 'G#': GS5, 'A': A5, 'A#': AS5, 'B': B5
}

# Subimos una octava para la melodía B para darle variación y contraste
notas_pitch_B = {
    'C': C6, 'C#': CS6, 'D': D6, 'D#': DS6, 'E': E6, 'F': F6, 
    'F#': FS6, 'G': G6, 'G#': GS6, 'A': A6, 'A#': AS6, 'B': B6
}

escala_C = [0, 2, 4, 5, 7, 9, 11]

# Matriz 12x12 en Python puro
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
        nota = random.choice(list(notas_idx.keys()))
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
                melodia[i]['nota'] = random.choice(list(notas_idx.keys()))
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

# Asegura que la melodía encaje exactamente en el bloque de 8 tiempos (2 compases) para no desfasar el ritmo
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
        
    # Si la melodía quedó corta, rellenamos con silencio
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

score = Score("Alternativa GA - House Latino A/B", tempo)

drumsPart = Part("Percusion house", 0, 9)
bassPart = Part("Bajo house", ACOUSTIC_BASS, 1)
pianoPart = Part("Melodia Piano", PIANO, 2) # Corregida la constante del Piano

FLOOR_TOM = 41
TOM_MEDIO = 47

def variarPercusion(bombo, hiHat, vuelta, repeticiones, seccion):
    tomBase = [REST, TOM_MEDIO, REST, FLOOR_TOM, REST, REST, TOM_MEDIO, FLOOR_TOM] * 2
    tom = list(tomBase)
    if seccion == "A" and vuelta < 4:
        tom = [REST] * 16
    elif seccion == "A" and vuelta < 8:
        tom[:8] = [REST] * 8
    elif seccion == "Final" and vuelta >= 2:
        tom = [REST] * 16

    if seccion != "Final" and ((vuelta + 1) % 4 == 0 or vuelta == repeticiones - 1):
        tom[12:] = [TOM_MEDIO, TOM_MEDIO, FLOOR_TOM, FLOOR_TOM]
        bombo[14:] = [REST, REST]

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

    if seccion == "A" and vuelta < 4:
        latina[:16] = [REST] * 16
        apoyo[:16] = [REST] * 16

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

def agregarPatron(frase, alturas, duraciones, repeticiones):
    for vuelta in range(repeticiones):
        frase.addNoteList(alturas, duraciones)

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


durDosCompases = [EN] * 16

durIntro = [EN] * 8
bomboIntro = [BDR, REST, BDR, REST, BDR, REST, BDR, REST]
cajaIntro = [REST] * 8
hiHatIntro = [REST, OHH, REST, OHH, REST, OHH, REST, OHH]
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

# =========================================================
# 3. GENERACIÓN DE MELODÍAS A y B
# =========================================================

print "Generando melodía A..."
melodia_ga_A, score_A = ga_compositor_melodias(
    pop_size=40, iterations=50, num_notas=16, bpm=tempo, 
    compass='4/4', selection_rate=0.3, mutation_rate=0.05
)

print "Generando melodía B (contraste)..."
melodia_ga_B, score_B = ga_compositor_melodias(
    pop_size=40, iterations=50, num_notas=16, bpm=tempo, 
    compass='4/4', selection_rate=0.3, mutation_rate=0.05
)

# Ajustar las melodías para que duren exactamente 8.0 tiempos (2 compases enteros)
alturas_A, duraciones_A = ajustar_melodia_a_beats(melodia_ga_A, notas_pitch_A, 8.0)
alturas_B, duraciones_B = ajustar_melodia_a_beats(melodia_ga_B, notas_pitch_B, 8.0)

# =========================================================
# 4. COMPOSICIÓN CRONOLÓGICA DE SECCIONES (Incluye el Piano)
# =========================================================

# --- INTRODUCCIÓN ---
for fraseNueva in (fraseLatina, fraseApoyo, fraseEfectos, fraseTom, fraseBombo, fraseCaja, fraseHiHat, fraseBajo):
    # La intro usa arrays distintos, ver código arriba
    pass

agregarPatron(fraseLatina, [REST] * 8, durIntro, repeticionesIntro)
agregarPatron(fraseApoyo, [REST] * 8, durIntro, repeticionesIntro)
agregarPatron(fraseEfectos, [REST] * 8, durIntro, repeticionesIntro)
agregarPatron(fraseTom, [REST] * 8, durIntro, repeticionesIntro)
agregarPatron(fraseBombo, bomboIntro, durIntro, repeticionesIntro)
agregarPatron(fraseCaja, cajaIntro, durIntro, repeticionesIntro)
agregarPatron(fraseHiHat, hiHatIntro, durIntro, repeticionesIntro)
agregarPatron(fraseBajo, bajoIntro, durIntro, repeticionesIntro)

# En la intro el piano permanece en silencio (4 tiempos por cada repeticion)
for _ in range(repeticionesIntro):
    frasePiano.addNoteList([REST], [4.0])


# --- SECCIÓN A ---
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboA, cajaA, hiHatA, bajoA,
               durDosCompases, durDosCompases, repeticionesA,
               True, True, True, "A")
# Agregamos la Melodía A
for _ in range(repeticionesA):
    frasePiano.addNoteList(alturas_A, duraciones_A)


# --- SECCIÓN B ---
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboB, cajaB, hiHatB, bajoB,
               durDosCompases, durDosCompases, repeticionesB,
               True, True, True, "B")
# Agregamos la Melodía B
for _ in range(repeticionesB):
    frasePiano.addNoteList(alturas_B, duraciones_B)


# --- REMATE LATINO ---
fraseLatina.addNoteList(REMATE, [EN / 2.0] * 8)
fraseApoyo.addNoteList([REST] * 8, [EN / 2.0] * 8)
fraseEfectos.addNoteList([FX_CIERRE] + [REST] * 7, [EN / 2.0] * 8)
fraseTom.addNoteList([TOM_MEDIO, TOM_MEDIO, FLOOR_TOM, FLOOR_TOM], [EN] * 4)
fraseBombo.addNoteList([REST, REST], [QN, QN])
fraseCaja.addNoteList([REST, REST], [QN, QN])
fraseHiHat.addNoteList([REST, REST], [QN, QN])
fraseBajo.addNoteList([REST, REST], [QN, QN])
# El remate dura 2 tiempos en total. El piano guarda silencio.
frasePiano.addNoteList([REST], [2.0])


# --- SECCIÓN A PRIMA ---
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboAprima, cajaAprima, hiHatAprima, bajoAprima,
               durDosCompases, durDosCompases, repeticionesAprima,
               True, True, True, "Aprima")
# Regresa la Melodía A
for _ in range(repeticionesAprima):
    frasePiano.addNoteList(alturas_A, duraciones_A)


# --- SECCIÓN FINAL ---
agregarSeccion(fraseBombo, fraseCaja, fraseHiHat, fraseBajo,
               bomboA, cajaA, hiHatA, bajoA,
               durDosCompases, durDosCompases, repeticionesFinal,
               True, True, True, "Final")
# La Melodía A permanece hasta el final
for _ in range(repeticionesFinal):
    frasePiano.addNoteList(alturas_A, duraciones_A)


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
bassPart.addPhrase(fraseBajo)
pianoPart.addPhrase(frasePiano) 

score.addPart(drumsPart)
score.addPart(bassPart)
score.addPart(pianoPart)

View.sketch(score)
Play.midi(score)
Write.midi(score, "Grupo3_EX3_PrototipoRitmico_Melodias_A_y_B.mid")