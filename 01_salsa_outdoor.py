# EX3.MC - Alternativa 01 - SALSA OUTDOOR
#
# Salsa: montuno generativo, shaker en cada tiempo y eco espacial suave.
# Mantiene semillas 42/84 y el GA original.
# Shaker: golpe en cada beat + eco retrasado para simular espacio/reverb.
# Transicion 3/4: baja de energia -> drop -> piano solo -> regreso completo.
#
from music import *
import random
import math


# =========================================================
# CONFIGURACION DE SEMILLAS
# =========================================================

# Si mantienes estos numeros, siempre obtendras
# exactamente las mismas melodias.
SEMILLA_A = 42
SEMILLA_B = 84


# =========================================================
# 1. ALGORITMO GENETICO PARA MELODIAS
# =========================================================

notas_idx = {
    'C': 0,
    'C#': 1,
    'D': 2,
    'D#': 3,
    'E': 4,
    'F': 5,
    'F#': 6,
    'G': 7,
    'G#': 8,
    'A': 9,
    'A#': 10,
    'B': 11
}

idx_notas = {v: k for k, v in notas_idx.items()}


# Orden fijo de notas.
# Esto ayuda a que las semillas sean consistentes.
notas_disponibles = [
    'C', 'C#', 'D', 'D#', 'E', 'F',
    'F#', 'G', 'G#', 'A', 'A#', 'B'
]


# Mapeo de alturas para la melodia A
notas_pitch_A = {
    'C': C5,
    'C#': CS5,
    'D': D5,
    'D#': DS5,
    'E': E5,
    'F': F5,
    'F#': FS5,
    'G': G5,
    'G#': GS5,
    'A': A5,
    'A#': AS5,
    'B': B5
}


# Melodia B una octava arriba para generar contraste
notas_pitch_B = {
    'C': C6,
    'C#': CS6,
    'D': D6,
    'D#': DS6,
    'E': E6,
    'F': F6,
    'F#': FS6,
    'G': G6,
    'G#': GS6,
    'A': A6,
    'A#': AS6,
    'B': B6
}


# Escala de C mayor
escala_C = [0, 2, 4, 5, 7, 9, 11]


# Matriz 12x12
M_melodia_C = [[0] * 12 for _ in range(12)]


# Premiar transiciones dentro de C mayor
for i in escala_C:
    for j in escala_C:
        M_melodia_C[i][j] = 1


# Premiar C, E y G
for i in escala_C:
    M_melodia_C[i][0] = 2
    M_melodia_C[i][4] = 2
    M_melodia_C[i][7] = 2


duraciones_validas = [0.25, 0.5, 1.0, 2.0]


# =========================================================
# GENERACION DE INDIVIDUOS
# =========================================================

def generar_melodia(num_notas):

    melodia = []

    for _ in range(num_notas):

        nota = random.choice(notas_disponibles)
        duracion = random.choice(duraciones_validas)

        melodia.append({
            'nota': nota,
            'duracion': duracion
        })

    return melodia


# =========================================================
# FITNESS
# =========================================================

def fitness_melodia(melodia, bpm, compass):

    score_val = 0

    num, den = map(int, compass.split('/'))

    tiempos_por_compas = num * (4.0 / den)

    tiempo_total = 0


    for i in range(len(melodia)):

        nota_actual = melodia[i]['nota']

        idx_actual = notas_idx[nota_actual]

        tiempo_total += melodia[i]['duracion']


        # Premiar notas pertenecientes a C mayor
        if idx_actual in escala_C:
            score_val += 1

        else:
            score_val -= 1


        # Evaluar transicion entre notas
        if i < len(melodia) - 1:

            nota_sig = melodia[i + 1]['nota']

            idx_sig = notas_idx[nota_sig]

            score_val += M_melodia_C[idx_actual][idx_sig]


    # Premiar que la melodia cierre correctamente
    # dentro del compas
    resto = tiempo_total % tiempos_por_compas

    if resto == 0:
        score_val += 5

    else:
        score_val -= 2


    # Penalizacion ligera para demasiadas notas
    # muy rapidas a tempos altos
    if bpm > 140 and any(
        n['duracion'] == 0.25
        for n in melodia
    ):
        score_val -= 1


    return score_val


# =========================================================
# CROSSOVER
# =========================================================

def crossover_melodia(mel1, mel2):

    corte = len(mel1) // 2

    return mel1[:corte] + mel2[corte:]


# =========================================================
# MUTACION
# =========================================================

def mutation_melodia(melodia, mutation_rate):

    for i in range(len(melodia)):

        if random.random() < mutation_rate:

            # 50% probabilidad de cambiar nota
            if random.random() < 0.5:

                melodia[i]['nota'] = random.choice(
                    notas_disponibles
                )

            # 50% probabilidad de cambiar duracion
            else:

                melodia[i]['duracion'] = random.choice(
                    duraciones_validas
                )

    return melodia


# =========================================================
# ALGORITMO GENETICO
# =========================================================

def ga_compositor_melodias(
        pop_size,
        iterations,
        num_notas,
        bpm,
        compass,
        selection_rate,
        mutation_rate):

    population = []

    sup_index = int(
        math.ceil(pop_size * selection_rate)
    )


    # Crear poblacion inicial
    for _ in range(pop_size):

        ind = generar_melodia(num_notas)

        population.append(
            (
                ind,
                fitness_melodia(
                    ind,
                    bpm,
                    compass
                )
            )
        )


    # Generaciones
    for count in range(iterations):

        # Seleccionar mejores individuos
        population = sorted(
            population,
            key=lambda x: x[1],
            reverse=True
        )[:sup_index]


        # Crear nuevos individuos
        while len(population) < pop_size:

            parent1 = random.choice(
                population[:sup_index]
            )[0]

            parent2 = random.choice(
                population[:sup_index]
            )[0]


            child = crossover_melodia(
                parent1,
                parent2
            )


            population.append(
                (
                    child,
                    fitness_melodia(
                        child,
                        bpm,
                        compass
                    )
                )
            )


        # Mutacion
        for i in range(len(population)):

            ind = population[i][0]

            mutated = mutation_melodia(
                ind,
                mutation_rate
            )

            population[i] = (
                mutated,
                fitness_melodia(
                    mutated,
                    bpm,
                    compass
                )
            )


    best_melodia = sorted(
        population,
        key=lambda x: x[1],
        reverse=True
    )[0]


    return best_melodia


# =========================================================
# AJUSTAR MELODIA A NUMERO EXACTO DE BEATS
# =========================================================

def ajustar_melodia_a_beats(
        melodia,
        dict_pitch,
        beats_objetivo):

    alturas = []
    duraciones = []

    tiempo_actual = 0.0


    for nota in melodia:

        if tiempo_actual >= beats_objetivo:
            break


        dur = nota['duracion']


        if tiempo_actual + dur > beats_objetivo:

            dur = beats_objetivo - tiempo_actual


        alturas.append(
            dict_pitch[nota['nota']]
        )

        duraciones.append(dur)

        tiempo_actual += dur


    # Si quedo corta, completar con silencio
    if tiempo_actual < beats_objetivo:

        alturas.append(REST)

        duraciones.append(
            beats_objetivo - tiempo_actual
        )


    return alturas, duraciones


# =========================================================
# 2. PROTOTIPO RITMICO
# =========================================================

tempo = 124

repeticionesIntro = 4
repeticionesA = 12
repeticionesB = 8
repeticionesAprima = 12
repeticionesFinal = 4


score = Score(
    "Alternativa 01 - SALSA OUTDOOR",
    tempo
)


drumsPart = Part(
    "Percusion house",
    0,
    9
)


bassPart = Part(
    "Bajo house",
    ACOUSTIC_BASS,
    1
)


pianoPart = Part(
    "Melodia Piano",
    PIANO,
    2
)


shakerPart = Part(
    "Shaker Outdoor Reverb",
    0,
    9
)


FLOOR_TOM = 41
TOM_MEDIO = 47


# =========================================================
# VARIACION DE PERCUSION
# =========================================================

def variarPercusion(
        bombo,
        hiHat,
        vuelta,
        repeticiones,
        seccion):


    tomBase = [
        REST, TOM_MEDIO,
        REST, FLOOR_TOM,
        REST, REST,
        TOM_MEDIO, FLOOR_TOM
    ] * 2


    tom = list(tomBase)


    if seccion == "A" and vuelta < 4:

        tom = [REST] * 16


    elif seccion == "A" and vuelta < 8:

        tom[:8] = [REST] * 8


    elif seccion == "Final" and vuelta >= 2:

        tom = [REST] * 16


    if (
        seccion != "Final"
        and (
            (vuelta + 1) % 4 == 0
            or vuelta == repeticiones - 1
        )
    ):

        tom[12:] = [
            TOM_MEDIO,
            TOM_MEDIO,
            FLOOR_TOM,
            FLOOR_TOM
        ]

        bombo[14:] = [
            REST,
            REST
        ]


    if (
        seccion in ("B", "Aprima")
        or (
            seccion == "A"
            and vuelta >= 4
        )
    ):

        hiHat = [REST] * 16


        for paso in range(16):

            if tom[paso] != REST:

                hiHat[paso] = CHH


            elif (
                paso > 0
                and tom[paso - 1] != REST
            ):

                hiHat[paso] = OHH


            elif paso % 2 == 0:

                hiHat[paso] = CHH


    fraseTom.addNoteList(
        tom,
        [EN] * 16
    )


    return bombo, hiHat


# =========================================================
# ELEMENTOS LATINOS
# =========================================================

DOBLES = [7, 23]


ABIERTOS = [
    2, 10,
    18, 26
]


LATINA = [
    (0, 60),
    (3, 61),
    (6, 60),
    (10, 61),
    (14, 60),
    (16, 61),
    (19, 60),
    (22, 61),
    (26, 60),
    (30, 61)
]


APOYO = [
    (0, 56),
    (6, 56),
    (10, 56),
    (16, 56),
    (22, 56),
    (28, 56)
]


REMATE = [
    60,
    61,
    REST,
    60,
    61,
    60,
    61,
    REST
]


FX_ENTRADA = 55
FX_CIERRE = 58


def expandirCorcheas(notas):

    resultado = []

    for nota in notas:

        resultado.extend([
            nota,
            REST
        ])

    return resultado


def patronLatino(golpes):

    notas = [REST] * 32


    for paso, instrumento in golpes:

        notas[paso] = instrumento


    return notas


def agregarSaborLatino(
        bombo,
        caja,
        hiHat,
        vuelta,
        repeticiones,
        seccion):


    bombo = expandirCorcheas(bombo)

    caja = expandirCorcheas(caja)

    hiHat = expandirCorcheas(hiHat)


    latina = patronLatino(LATINA)

    apoyo = patronLatino(APOYO)

    efectos = [REST] * 32


    remate = (
        seccion != "Final"
        and (
            (vuelta + 1) % 4 == 0
            or vuelta == repeticiones - 1
        )
    )


    if seccion == "A" and vuelta < 4:

        latina[:16] = [REST] * 16

        apoyo[:16] = [REST] * 16


    if (
        seccion in ("B", "Aprima")
        or vuelta % 2 == 1
    ):

        for paso in DOBLES:

            bombo[paso - 1] = BDR

            bombo[paso] = BDR


    for paso in ABIERTOS:

        hiHat[paso] = OHH

        hiHat[paso + 1] = CHH


    if remate:

        latina[24:] = REMATE

        caja[28:] = [
            SNR,
            REST,
            SNR,
            SNR
        ]

        hiHat[28:] = [
            CHH,
            CHH,
            OHH,
            CHH
        ]

        efectos[24] = FX_CIERRE

        bombo[28:] = [
            REST
        ] * 4


    if (
        vuelta == 0
        and seccion in (
            "A",
            "B",
            "Aprima"
        )
    ):

        efectos[0] = FX_ENTRADA


    if (
        seccion == "Final"
        and vuelta >= 2
    ):

        latina = [
            REST
        ] * 32


        apoyo = [
            REST
        ] * 32


        bombo = [
            BDR if paso % 4 == 0
            else REST
            for paso in range(32)
        ]


        hiHat = [
            CHH if paso % 4 == 2
            else REST
            for paso in range(32)
        ]


    fraseLatina.addNoteList(
        latina,
        [EN / 2.0] * 32
    )


    fraseApoyo.addNoteList(
        apoyo,
        [EN / 2.0] * 32
    )


    fraseEfectos.addNoteList(
        efectos,
        [EN / 2.0] * 32
    )


    return bombo, caja, hiHat


# =========================================================
# AGREGAR PATRON
# =========================================================

def agregarPatron(
        frase,
        alturas,
        duraciones,
        repeticiones):


    for vuelta in range(repeticiones):

        frase.addNoteList(
            alturas,
            duraciones
        )


# =========================================================
# AGREGAR SECCION
# =========================================================

# En la seccion A Prima, las vueltas 6 y 7 ocurren aproximadamente
# alrededor del 3/4 de la duracion total de la pieza.
#
# vuelta 6 = baja de energia
# vuelta 7 = golpe de drop + silencio; el piano hara el solo aparte
# vuelta 8 en adelante = regreso de toda la energia


def agregarBloqueBajaEnergia(
        fraseBombo,
        fraseCaja,
        fraseHiHat,
        fraseBajo):

    latina = [REST] * 32
    apoyo = [REST] * 32
    efectos = [REST] * 32
    tom = [REST] * 16

    # Dejamos muy pocos elementos latinos para que se sienta
    # claramente la reduccion de energia.
    latina[0] = 60
    latina[16] = 61

    bombo = [REST] * 32
    caja = [REST] * 32
    hiHat = [REST] * 32
    bajo = [REST] * 16

    # Un golpe fuerte al inicio de cada compas.
    bombo[0] = BDR
    bombo[16] = BDR

    # Caja muy ligera al final de cada compas.
    caja[12] = SNR
    caja[28] = SNR

    # Hi-hat espaciado.
    hiHat[4] = CHH
    hiHat[12] = CHH
    hiHat[20] = CHH
    hiHat[28] = CHH

    # Bajo reducido.
    bajo[1] = C2
    bajo[9] = G2

    fraseLatina.addNoteList(
        latina,
        [EN / 2.0] * 32
    )

    fraseApoyo.addNoteList(
        apoyo,
        [EN / 2.0] * 32
    )

    fraseEfectos.addNoteList(
        efectos,
        [EN / 2.0] * 32
    )

    fraseTom.addNoteList(
        tom,
        [EN] * 16
    )

    fraseBombo.addNoteList(
        bombo,
        [EN / 2.0] * 32
    )

    fraseCaja.addNoteList(
        caja,
        [EN / 2.0] * 32
    )

    fraseHiHat.addNoteList(
        hiHat,
        [EN / 2.0] * 32
    )

    fraseBajo.addNoteList(
        bajo,
        [EN] * 16
    )



def agregarBloqueDropYSolo(
        fraseBombo,
        fraseCaja,
        fraseHiHat,
        fraseBajo):

    latina = [REST] * 32
    apoyo = [REST] * 32
    efectos = [REST] * 32
    tom = [REST] * 16

    bombo = [REST] * 32
    caja = [REST] * 32
    hiHat = [REST] * 32
    bajo = [REST] * 16

    # Un unico impacto abre el drop.
    bombo[0] = BDR
    efectos[0] = FX_CIERRE

    # Despues del impacto, percusion y bajo desaparecen por
    # todo el bloque. El piano maneja por separado 4 beats
    # de silencio y 4 beats completamente solo.
    fraseLatina.addNoteList(
        latina,
        [EN / 2.0] * 32
    )

    fraseApoyo.addNoteList(
        apoyo,
        [EN / 2.0] * 32
    )

    fraseEfectos.addNoteList(
        efectos,
        [EN / 2.0] * 32
    )

    fraseTom.addNoteList(
        tom,
        [EN] * 16
    )

    fraseBombo.addNoteList(
        bombo,
        [EN / 2.0] * 32
    )

    fraseCaja.addNoteList(
        caja,
        [EN / 2.0] * 32
    )

    fraseHiHat.addNoteList(
        hiHat,
        [EN / 2.0] * 32
    )

    fraseBajo.addNoteList(
        bajo,
        [EN] * 16
    )



def agregarSeccion(
        fraseBombo,
        fraseCaja,
        fraseHiHat,
        fraseBajo,
        bomboBase,
        cajaBase,
        hiHatBase,
        bajoBase,
        durPercusion,
        durBajo,
        repeticiones,
        abrirHiHat,
        golpeFinal,
        variarBajo,
        seccion):


    notasArmonia = [
        C2,
        E2,
        G2,
        A2
    ]


    for vuelta in range(repeticiones):

        # -------------------------------------------------
        # TRANSICION ESPECIAL CERCA DEL 3/4 DE LA CANCION
        # -------------------------------------------------

        if seccion == "Aprima" and vuelta == 6:

            agregarBloqueBajaEnergia(
                fraseBombo,
                fraseCaja,
                fraseHiHat,
                fraseBajo
            )

            continue


        if seccion == "Aprima" and vuelta == 7:

            agregarBloqueDropYSolo(
                fraseBombo,
                fraseCaja,
                fraseHiHat,
                fraseBajo
            )

            continue


        # -------------------------------------------------
        # COMPORTAMIENTO NORMAL
        # -------------------------------------------------

        bombo = list(bomboBase)
        caja = list(cajaBase)
        hiHat = list(hiHatBase)
        bajo = list(bajoBase)


        if (
            abrirHiHat
            and (vuelta + 1) % 4 == 0
        ):

            hiHat[15] = OHH


        if (
            golpeFinal
            and vuelta == repeticiones - 1
        ):

            bombo[15] = BDR


        if (
            variarBajo
            and vuelta % 2 == 0
        ):

            bajo[9] = notasArmonia[
                vuelta % len(notasArmonia)
            ]


        bombo, hiHat = variarPercusion(
            bombo,
            hiHat,
            vuelta,
            repeticiones,
            seccion
        )


        bombo, caja, hiHat = agregarSaborLatino(
            bombo,
            caja,
            hiHat,
            vuelta,
            repeticiones,
            seccion
        )


        fraseBombo.addNoteList(
            bombo,
            [EN / 2.0] * 32
        )


        fraseCaja.addNoteList(
            caja,
            [EN / 2.0] * 32
        )


        fraseHiHat.addNoteList(
            hiHat,
            [EN / 2.0] * 32
        )


        fraseBajo.addNoteList(
            bajo,
            durBajo
        )


# =========================================================
# PATRONES BASE
# =========================================================

durDosCompases = [
    EN
] * 16


durIntro = [
    EN
] * 8


bomboIntro = [
    BDR,
    REST,
    BDR,
    REST,
    BDR,
    REST,
    BDR,
    REST
]


cajaIntro = [
    REST
] * 8


hiHatIntro = [
    REST,
    OHH,
    REST,
    OHH,
    REST,
    OHH,
    REST,
    OHH
]


bajoIntro = [
    REST,
    C2,
    REST,
    C2,
    REST,
    C2,
    REST,
    C2
]


# SECCION A

bomboA = [
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST
]


cajaA = [
    REST, REST,
    SNR, REST,
    REST, REST,
    SNR, REST,
    REST, REST,
    SNR, REST,
    REST, REST,
    SNR, REST
]


hiHatA = [
    CHH, OHH,
    CHH, OHH,
    CHH, OHH,
    CHH, OHH,
    CHH, OHH,
    CHH, OHH,
    CHH, OHH,
    CHH, OHH
]


bajoA = [
    REST, C2,
    REST, C2,
    REST, E2,
    REST, G2,
    REST, C2,
    REST, E2,
    REST, G2,
    REST, E2
]


# SECCION B

bomboB = [
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST,
    BDR, REST
]


cajaB = [
    REST, REST,
    REST, REST,
    REST, REST,
    SNR, REST,
    REST, REST,
    REST, REST,
    REST, REST,
    SNR, REST
]


hiHatB = [
    REST, OHH,
    CHH, OHH,
    REST, OHH,
    CHH, OHH,
    REST, OHH,
    CHH, OHH,
    REST, OHH,
    CHH, OHH
]


bajoB = [
    REST, G2,
    REST, G2,
    REST, A2,
    REST, G2,
    REST, E2,
    REST, E2,
    REST, G2,
    REST, A2
]


# A PRIMA

bomboAprima = bomboA
cajaAprima = cajaA
hiHatAprima = hiHatA


bajoAprima = [
    REST, C2,
    C2, REST,
    REST, E2,
    REST, G2,
    REST, C2,
    E2, REST,
    REST, G2,
    A2, REST
]


# =========================================================
# CREAR FRASES
# =========================================================

fraseLatina = Phrase(0.0)

fraseApoyo = Phrase(0.0)

fraseEfectos = Phrase(0.0)

fraseTom = Phrase(0.0)

fraseBombo = Phrase(0.0)

fraseCaja = Phrase(0.0)

fraseHiHat = Phrase(0.0)

fraseBajo = Phrase(0.0)

frasePiano = Phrase(0.0)

# Shaker principal y eco retrasado.
fraseShaker = Phrase(0.0)
fraseShakerEco = Phrase(0.18)


# =========================================================
# 3. GENERACION DE MELODIA A CON SEMILLA
# =========================================================

print "-------------------------------------"
print "Generando melodia A..."
print "Semilla A:", SEMILLA_A
print "-------------------------------------"


# IMPORTANTE:
# Reiniciamos el generador aleatorio con la semilla A
random.seed(SEMILLA_A)


melodia_ga_A, score_A = ga_compositor_melodias(

    pop_size=40,

    iterations=50,

    num_notas=16,

    bpm=tempo,

    compass='4/4',

    selection_rate=0.3,

    mutation_rate=0.05
)


print "Fitness A:", score_A

print "Melodia A:", melodia_ga_A


# =========================================================
# GENERACION DE MELODIA B CON OTRA SEMILLA
# =========================================================

print "-------------------------------------"
print "Generando melodia B..."
print "Semilla B:", SEMILLA_B
print "-------------------------------------"


# Reiniciamos nuevamente el generador,
# ahora usando otra semilla.
random.seed(SEMILLA_B)


melodia_ga_B, score_B = ga_compositor_melodias(

    pop_size=40,

    iterations=50,

    num_notas=16,

    bpm=tempo,

    compass='4/4',

    selection_rate=0.3,

    mutation_rate=0.05
)


print "Fitness B:", score_B

print "Melodia B:", melodia_ga_B


# =========================================================
# AJUSTAR LAS MELODIAS A 8 BEATS
# =========================================================

alturas_A, duraciones_A = ajustar_melodia_a_beats(
    melodia_ga_A,
    notas_pitch_A,
    8.0
)


alturas_B, duraciones_B = ajustar_melodia_a_beats(
    melodia_ga_B,
    notas_pitch_B,
    8.0
)



# =========================================================
# CONFIGURACION DEL PIANO GENERATIVO POR GENERO
# =========================================================

# La intro utiliza corcheas (EN). Para que el piano empiece
# en la cuarta posicion de corchea dejamos sonar primero
# tres corcheas completas:
INICIO_PIANO = 3 * EN

# El algoritmo genetico original puede producir notas cromaticas.
# Para mantener SOLO la parte de piano estrictamente en Do mayor,
# normalizamos cualquier nota cromatica al grado diatonico siguiente.
NORMALIZAR_C_MAYOR = {
    'C': 'C',
    'C#': 'D',
    'D': 'D',
    'D#': 'E',
    'E': 'E',
    'F': 'F',
    'F#': 'G',
    'G': 'G',
    'G#': 'A',
    'A': 'A',
    'A#': 'B',
    'B': 'B'
}


def obtener_alturas_piano(melodia, dict_pitch):
    alturas = []

    for nota in melodia:
        nombre = NORMALIZAR_C_MAYOR[nota['nota']]
        alturas.append(dict_pitch[nombre])

    return alturas



# =========================================================
# ALTERNATIVA 1 - PIANO SALSA
# =========================================================
#
# Patron de 2 compases en corcheas.
# X = nota generada por el GA
# . = silencio
#
# X . X X . X . X | X . X X . X . X

GOLPES_PIANO_SALSA = [
    0, 2, 3, 5, 7,
    8, 10, 11, 13, 15
]

PASOS_PIANO_SALSA = 16
DURACION_PASO_PIANO_SALSA = EN


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
# TRANSICIONES DEL PIANO PARA EL 3/4 DE LA CANCION
# =========================================================


def agregarPianoReducido(
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

    tiempo = 0.0
    indice = desplazamiento

    # Una nota cada dos beats. Deja bastante aire antes del drop.
    while tiempo < beats_objetivo - 0.0001:

        durNota = 1.0
        durSilencio = 1.0

        if tiempo + durNota > beats_objetivo:
            durNota = beats_objetivo - tiempo

        frase.addNoteList(
            [alturas[indice % len(alturas)]],
            [durNota]
        )

        tiempo += durNota
        indice += 1

        if tiempo >= beats_objetivo - 0.0001:
            break

        if tiempo + durSilencio > beats_objetivo:
            durSilencio = beats_objetivo - tiempo

        frase.addNoteList(
            [REST],
            [durSilencio]
        )

        tiempo += durSilencio



def agregarPianoSolo(
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

    tiempo = 0.0
    indice = desplazamiento

    # Piano completamente solo: notas de un beat para que se
    # perciba claramente la melodia antes del regreso completo.
    while tiempo < beats_objetivo - 0.0001:

        duracion = 1.0

        if tiempo + duracion > beats_objetivo:
            duracion = beats_objetivo - tiempo

        frase.addNoteList(
            [alturas[indice % len(alturas)]],
            [duracion]
        )

        tiempo += duracion
        indice += 1


# =========================================================
# 4. COMPOSICION CRONOLOGICA
# =========================================================


# ---------------------------------------------------------
# INTRODUCCION
# ---------------------------------------------------------

agregarPatron(
    fraseLatina,
    [REST] * 8,
    durIntro,
    repeticionesIntro
)


agregarPatron(
    fraseApoyo,
    [REST] * 8,
    durIntro,
    repeticionesIntro
)


agregarPatron(
    fraseEfectos,
    [REST] * 8,
    durIntro,
    repeticionesIntro
)


agregarPatron(
    fraseTom,
    [REST] * 8,
    durIntro,
    repeticionesIntro
)


agregarPatron(
    fraseBombo,
    bomboIntro,
    durIntro,
    repeticionesIntro
)


agregarPatron(
    fraseCaja,
    cajaIntro,
    durIntro,
    repeticionesIntro
)


agregarPatron(
    fraseHiHat,
    hiHatIntro,
    durIntro,
    repeticionesIntro
)


agregarPatron(
    fraseBajo,
    bajoIntro,
    durIntro,
    repeticionesIntro
)


# Piano: entra en la cuarta corchea de la cancion.
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


# ---------------------------------------------------------
# SECCION A
# ---------------------------------------------------------

agregarSeccion(

    fraseBombo,
    fraseCaja,
    fraseHiHat,
    fraseBajo,

    bomboA,
    cajaA,
    hiHatA,
    bajoA,

    durDosCompases,
    durDosCompases,

    repeticionesA,

    True,
    True,
    True,

    "A"
)


for vuelta in range(repeticionesA):

    agregarPianoSalsa(
        frasePiano,
        melodia_ga_A,
        notas_pitch_A,
        8.0,
        vuelta * 2
    )


# ---------------------------------------------------------
# SECCION B
# ---------------------------------------------------------

agregarSeccion(

    fraseBombo,
    fraseCaja,
    fraseHiHat,
    fraseBajo,

    bomboB,
    cajaB,
    hiHatB,
    bajoB,

    durDosCompases,
    durDosCompases,

    repeticionesB,

    True,
    True,
    True,

    "B"
)


for vuelta in range(repeticionesB):

    agregarPianoSalsa(
        frasePiano,
        melodia_ga_B,
        notas_pitch_B,
        8.0,
        vuelta * 3
    )


# ---------------------------------------------------------
# REMATE LATINO
# ---------------------------------------------------------

fraseLatina.addNoteList(
    REMATE,
    [EN / 2.0] * 8
)


fraseApoyo.addNoteList(
    [REST] * 8,
    [EN / 2.0] * 8
)


fraseEfectos.addNoteList(
    [FX_CIERRE] + [REST] * 7,
    [EN / 2.0] * 8
)


fraseTom.addNoteList(
    [
        TOM_MEDIO,
        TOM_MEDIO,
        FLOOR_TOM,
        FLOOR_TOM
    ],
    [EN] * 4
)


fraseBombo.addNoteList(
    [REST, REST],
    [QN, QN]
)


fraseCaja.addNoteList(
    [REST, REST],
    [QN, QN]
)


fraseHiHat.addNoteList(
    [REST, REST],
    [QN, QN]
)


fraseBajo.addNoteList(
    [REST, REST],
    [QN, QN]
)


frasePiano.addNoteList(
    [REST],
    [2.0]
)


# ---------------------------------------------------------
# SECCION A PRIMA
# ---------------------------------------------------------

agregarSeccion(

    fraseBombo,
    fraseCaja,
    fraseHiHat,
    fraseBajo,

    bomboAprima,
    cajaAprima,
    hiHatAprima,
    bajoAprima,

    durDosCompases,
    durDosCompases,

    repeticionesAprima,

    True,
    True,
    True,

    "Aprima"
)


for vuelta in range(repeticionesAprima):

    if vuelta == 6:

        # Bajada de energia justo antes del drop.
        agregarPianoReducido(
            frasePiano,
            melodia_ga_A,
            notas_pitch_A,
            8.0,
            4 + vuelta * 3
        )

    elif vuelta == 7:

        # DROP: 4 beats de silencio total.
        frasePiano.addNoteList(
            [REST],
            [4.0]
        )

        # SOLO: durante los siguientes 4 beats queda solo el piano.
        agregarPianoSolo(
            frasePiano,
            melodia_ga_A,
            notas_pitch_A,
            4.0,
            7
        )

    else:

        # Antes y despues del drop funciona el patron completo.
        agregarPianoSalsa(
            frasePiano,
            melodia_ga_A,
            notas_pitch_A,
            8.0,
            4 + vuelta * 3
        )


# ---------------------------------------------------------
# SECCION FINAL
# ---------------------------------------------------------

agregarSeccion(

    fraseBombo,
    fraseCaja,
    fraseHiHat,
    fraseBajo,

    bomboA,
    cajaA,
    hiHatA,
    bajoA,

    durDosCompases,
    durDosCompases,

    repeticionesFinal,

    True,
    True,
    True,

    "Final"
)


for vuelta in range(repeticionesFinal):

    agregarPianoSalsa(
        frasePiano,
        melodia_ga_A,
        notas_pitch_A,
        8.0,
        2 + vuelta * 4
    )



# =========================================================
# SHAKER OUTDOOR + REVERB SIMULADO
# =========================================================
#
# General MIDI no garantiza un control de reverb igual en todos
# los reproductores. Para mantener compatibilidad con JythonMusic,
# simulamos el espacio exterior con una segunda frase retrasada
# 0.18 beats y bastante mas suave.
#
# El golpe principal del shaker aparece en cada tiempo, como una caja.
# Los ghost hits cambian segun la alternativa.

SHAKER = 82
CABASA = 69

PASO_SHAKER = 0.5
GOLPES_PRINCIPALES_SHAKER = [0, 2, 4, 6]
GHOSTS_SHAKER = [5]
DINAMICA_SHAKER = 86
DINAMICA_ECO_SHAKER = 42
BOOST_FINAL_SHAKER = 10


def agregarNotaConDinamica(
        frase,
        pitch,
        duracion,
        dinamica):

    if pitch == REST:
        frase.addNote(
            Note(REST, duracion)
        )
    else:
        frase.addNote(
            Note(pitch, duracion, dinamica)
        )



def acentoDesdeMelodia(
        melodia,
        indice):

    if len(melodia) == 0:
        return 0

    nombre = melodia[
        indice % len(melodia)
    ]['nota']

    # C, E y G ya reciben una recompensa mayor en el fitness.
    # Hacemos que el shaker tambien respire un poco con esas notas.
    if nombre in ('C', 'E', 'G'):
        return 8

    if nombre in ('D', 'F', 'A', 'B'):
        return 4

    return 2



def agregarShakerBloque(
        beats,
        melodia,
        modo="normal",
        boost=0):

    pasos = int(round(beats / PASO_SHAKER))

    for paso in range(pasos):

        posicion = paso % 8
        acento = acentoDesdeMelodia(
            melodia,
            paso / 2
        )

        principal = (
            posicion in GOLPES_PRINCIPALES_SHAKER
        )

        ghost = (
            posicion in GHOSTS_SHAKER
        )

        # ---------------------------------------------
        # DROP / SOLO: sin shaker
        # ---------------------------------------------
        if modo == "silencio":

            agregarNotaConDinamica(
                fraseShaker,
                REST,
                PASO_SHAKER,
                0
            )

            agregarNotaConDinamica(
                fraseShakerEco,
                REST,
                PASO_SHAKER,
                0
            )

            continue


        # ---------------------------------------------
        # BAJA DE ENERGIA
        # Solo beats 1 y 3, mucho mas suaves.
        # ---------------------------------------------
        if modo == "baja":

            principal = posicion in (0, 4)
            ghost = False


        if principal:

            dinamica = DINAMICA_SHAKER + acento + boost

            if modo == "baja":
                dinamica -= 28

            if dinamica > 120:
                dinamica = 120

            agregarNotaConDinamica(
                fraseShaker,
                SHAKER,
                PASO_SHAKER,
                dinamica
            )

            # Eco retrasado: misma respiracion que la melodia,
            # pero considerablemente mas suave.
            dinamicaEco = DINAMICA_ECO_SHAKER + (acento / 2)

            agregarNotaConDinamica(
                fraseShakerEco,
                SHAKER,
                PASO_SHAKER,
                dinamicaEco
            )


        elif ghost and modo != "baja":

            agregarNotaConDinamica(
                fraseShaker,
                CABASA,
                PASO_SHAKER,
                42 + (acento / 2)
            )

            agregarNotaConDinamica(
                fraseShakerEco,
                SHAKER,
                PASO_SHAKER,
                28 + (acento / 3)
            )


        else:

            agregarNotaConDinamica(
                fraseShaker,
                REST,
                PASO_SHAKER,
                0
            )

            agregarNotaConDinamica(
                fraseShakerEco,
                REST,
                PASO_SHAKER,
                0
            )



def construirShakerCompleto():

    # INTRO: entra desde el inicio para establecer la sensacion
    # exterior y el pulso constante.
    agregarShakerBloque(
        repeticionesIntro * 4.0,
        melodia_ga_A,
        "normal",
        -6
    )

    # A
    for _ in range(repeticionesA):
        agregarShakerBloque(
            8.0,
            melodia_ga_A,
            "normal",
            0
        )

    # B
    for _ in range(repeticionesB):
        agregarShakerBloque(
            8.0,
            melodia_ga_B,
            "normal",
            3
        )

    # Remate latino de 2 beats
    agregarShakerBloque(
        2.0,
        melodia_ga_B,
        "normal",
        0
    )

    # A Prima: misma ubicacion que la bajada/drop del resto
    # de instrumentos.
    for vuelta in range(repeticionesAprima):

        if vuelta == 6:
            agregarShakerBloque(
                8.0,
                melodia_ga_A,
                "baja",
                -10
            )

        elif vuelta == 7:
            # 4 beats de drop + 4 beats de piano solo.
            # El shaker permanece fuera durante ambos.
            agregarShakerBloque(
                8.0,
                melodia_ga_A,
                "silencio",
                0
            )

        else:
            agregarShakerBloque(
                8.0,
                melodia_ga_A,
                "normal",
                0
            )

    # FINAL: vuelve con mas energia.
    for _ in range(repeticionesFinal):
        agregarShakerBloque(
            8.0,
            melodia_ga_A,
            "normal",
            BOOST_FINAL_SHAKER
        )



# Construimos el shaker despues de tener A y B generadas.
construirShakerCompleto()


# =========================================================
# 5. ENSAMBLAJE FINAL
# =========================================================

drumsPart.addPhrase(
    fraseLatina
)

drumsPart.addPhrase(
    fraseApoyo
)

drumsPart.addPhrase(
    fraseEfectos
)

drumsPart.addPhrase(
    fraseTom
)

drumsPart.addPhrase(
    fraseBombo
)

drumsPart.addPhrase(
    fraseCaja
)

drumsPart.addPhrase(
    fraseHiHat
)

bassPart.addPhrase(
    fraseBajo
)

pianoPart.addPhrase(
    frasePiano
)

shakerPart.addPhrase(
    fraseShaker
)

shakerPart.addPhrase(
    fraseShakerEco
)


score.addPart(
    drumsPart
)

score.addPart(
    bassPart
)

score.addPart(
    pianoPart
)

score.addPart(
    shakerPart
)


# =========================================================
# MOSTRAR, REPRODUCIR Y EXPORTAR
# =========================================================

print "====================================="
print "COMPOSICION TERMINADA"
print "Semilla A:", SEMILLA_A
print "Semilla B:", SEMILLA_B
print "Fitness A:", score_A
print "Fitness B:", score_B
print "====================================="


View.sketch(score)

Play.midi(score)

Write.midi(
    score,
    "Alternativa_01_Salsa_Outdoor.mid"
)
