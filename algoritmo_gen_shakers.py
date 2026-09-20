# -*- coding: utf-8 -*-
import random
import math


# ============================================================
# CONFIGURACION DEL SHAKER
# ============================================================

BPM = 127

# Misma semilla y parametros = mismo patron en la misma version de Jython.
SEED = 42

# Intro corta
BARS = 2

# 16 semicorcheas por compas en 4/4
STEPS_PER_BAR = 16

# Parametros del algoritmo genetico
POP_SIZE = 100
GENERATIONS = 150
SELECTION_RATE = 0.25
MUTATION_RATE = 0.05


# ============================================================
# REPRESENTACION DEL CROMOSOMA
# ============================================================
#
# Cada gen representa una semicorchea:
#
# 0 = silencio
# 1 = shaker suave
# 2 = shaker acentuado
#
# Ejemplo:
#
# [1,0,2,0, 1,0,2,0, 1,0,2,0, 1,0,2,0]
#
# Visualmente:
#
# x - X - | x - X - | x - X - | x - X -
#
# ============================================================


# ============================================================
# 1. CREAR UN INDIVIDUO
# ============================================================

def create_individual(rng=random):

    total_steps = BARS * STEPS_PER_BAR

    pattern = []

    for i in range(total_steps):

        r = rng.random()

        # Generamos principalmente golpes suaves.
        # Hay menos silencios y todavía menos acentos.

        if r < 0.30:
            pattern.append(0)

        elif r < 0.90:
            pattern.append(1)

        else:
            pattern.append(2)

    return pattern


# ============================================================
# 2. CREAR POBLACION
# ============================================================

def create_population(size, rng=random):

    population = []

    for i in range(size):
        population.append(create_individual(rng))

    return population


# ============================================================
# 3. FITNESS
# ============================================================

def fitness_function(pattern):

    score = 0.0

    # --------------------------------------------------------
    # EVALUAR CADA COMPAS
    # --------------------------------------------------------

    for bar in range(BARS):

        start = bar * STEPS_PER_BAR
        end = start + STEPS_PER_BAR

        current_bar = pattern[start:end]

        hits = sum(
            1 for gene in current_bar
            if gene > 0
        )

        accents = sum(
            1 for gene in current_bar
            if gene == 2
        )

        density = float(hits) / STEPS_PER_BAR


        # ====================================================
        # CRECIMIENTO DE LA INTRO
        # ====================================================
        #
        # Queremos:
        #
        # Compas 1 -> relativamente simple
        # Compas 2 -> mas movimiento
        #
        # ====================================================

        if bar == 0:
            target_density = 0.50

        else:
            target_density = 0.75


        # Mientras mas cerca este de la densidad deseada,
        # mayor puntuacion obtiene.

        score += 10.0 * (
            1.0 - abs(density - target_density)
        )


        # ====================================================
        # POSICIONES RITMICAS
        # ====================================================
        #
        # En 16 semicorcheas:
        #
        # 0  1  2  3
        # 1  e  &  a
        #
        # 4  5  6  7
        # 2  e  &  a
        #
        # etc.
        #
        # Los indices:
        #
        # 0,4,8,12 = pulsos principales
        # 2,6,10,14 = "&"
        #
        # Para un shaker nos interesan bastante los offbeats.
        # ====================================================

        for step, gene in enumerate(current_bar):

            if gene > 0:

                # Golpes en pulsos principales
                if step in [0, 4, 8, 12]:
                    score += 0.6

                # Offbeats
                if step in [2, 6, 10, 14]:
                    score += 1.0

                # Un acento en un offbeat recibe mas puntos
                if gene == 2 and step in [2, 6, 10, 14]:
                    score += 1.2


        # ====================================================
        # CONTROL DE ACENTOS
        # ====================================================

        # No queremos que todo sea acentuado.

        if accents <= 4:
            score += 2.0

        else:
            score -= (accents - 4) * 0.8


        # ====================================================
        # EVITAR SILENCIOS MUY LARGOS
        # ====================================================

        consecutive_silences = 0

        for gene in current_bar:

            if gene == 0:

                consecutive_silences += 1

                if consecutive_silences >= 4:
                    score -= 1.0

            else:

                consecutive_silences = 0


    # ========================================================
    # HACER QUE EL SEGUNDO COMPAS SEA MAS INTENSO
    # ========================================================

    first_bar_hits = sum(
        1 for x in pattern[:STEPS_PER_BAR]
        if x > 0
    )

    second_bar_hits = sum(
        1 for x in pattern[STEPS_PER_BAR:]
        if x > 0
    )


    if second_bar_hits >= first_bar_hits:

        score += 5.0

    else:

        score -= 5.0


    # ========================================================
    # PREPARAR LA ENTRADA DE LA CANCION
    # ========================================================
    #
    # Queremos actividad en las ultimas 4 semicorcheas
    # para que la intro no termine vacia.
    #
    # ========================================================

    final_steps = pattern[-4:]

    final_hits = sum(
        1 for x in final_steps
        if x > 0
    )

    score += final_hits * 1.5


    return score


# ============================================================
# 4. SELECCION
# ============================================================

def select_population(population):

    evaluated = []

    for individual in population:

        fitness = fitness_function(individual)

        evaluated.append(
            (individual, fitness)
        )


    # Ordenar de mayor a menor fitness
    evaluated.sort(
        key=lambda x: x[1],
        reverse=True
    )


    # Numero de individuos que sobreviven
    keep = int(
        math.ceil(
            len(population) * SELECTION_RATE
        )
    )

    # Como minimo conservar 2
    keep = max(2, keep)


    selected = []

    for item in evaluated[:keep]:

        selected.append(item[0])


    return selected


# ============================================================
# 5. CROSSOVER
# ============================================================

def crossover(parent1, parent2, rng=random):

    # Elegimos un punto aleatorio donde cortar
    # los cromosomas.

    point = rng.randint(
        1,
        len(parent1) - 1
    )


    # Primera parte del padre 1
    # +
    # segunda parte del padre 2

    child = (
        parent1[:point]
        +
        parent2[point:]
    )


    return child


# ============================================================
# 6. MUTACION
# ============================================================

def mutate(pattern, rng=random):

    new_pattern = pattern[:]


    for i in range(len(new_pattern)):

        if rng.random() < MUTATION_RATE:

            # Puede convertirse en:
            #
            # 0 = silencio
            # 1 = suave
            # 2 = acentuado

            new_pattern[i] = rng.randint(
                0,
                2
            )


    return new_pattern


# ============================================================
# 7. ALGORITMO GENETICO
# ============================================================

def genetic_shaker_intro(seed=SEED):

    # Generador local: otras llamadas a random no alteran este resultado.
    rng = random.Random(seed)

    population = create_population(
        POP_SIZE, rng
    )


    for generation in range(GENERATIONS):

        # --------------------------------------------
        # SELECCION
        # --------------------------------------------

        selected = select_population(
            population
        )


        # --------------------------------------------
        # ELITISMO
        # --------------------------------------------
        #
        # El mejor individuo pasa directamente
        # a la siguiente generacion.
        #

        best = max(
            selected,
            key=fitness_function
        )


        new_population = [
            best[:]
        ]


        # --------------------------------------------
        # CREAR RESTO DE LA POBLACION
        # --------------------------------------------

        while len(new_population) < POP_SIZE:

            parent1 = rng.choice(
                selected
            )

            parent2 = rng.choice(
                selected
            )


            child = crossover(
                parent1,
                parent2,
                rng
            )


            child = mutate(
                child, rng
            )


            new_population.append(
                child
            )


        population = new_population


    # ========================================================
    # OBTENER MEJOR PATRON FINAL
    # ========================================================

    best_pattern = max(
        population,
        key=fitness_function
    )


    return best_pattern


# ============================================================
# 8. MOSTRAR EL PATRON
# ============================================================

def print_pattern(pattern):

    print("")
    print("INTRO DE SHAKER")
    print("================")


    for bar in range(BARS):

        start = bar * STEPS_PER_BAR
        end = start + STEPS_PER_BAR

        current_bar = pattern[start:end]


        visual = []


        for gene in current_bar:

            if gene == 0:

                visual.append("-")

            elif gene == 1:

                visual.append("x")

            else:

                visual.append("X")


        print(
            "Compas {0}: {1}".format(
                bar + 1,
                " ".join(visual)
            )
        )


    print("")
    print("Leyenda:")
    print("- = silencio")
    print("x = shaker suave")
    print("X = shaker acentuado")

    print("")
    print(
        "Fitness: {0}".format(
            fitness_function(pattern)
        )
    )


# ============================================================
# 9. CONVERTIR LOS GENES A TIEMPO
# ============================================================
#
# Esto despues nos servira para convertir el patron
# en MIDI o audio.
#
# ============================================================

def pattern_to_events(pattern, bpm=BPM):

    # Duracion de una negra
    seconds_per_beat = 60.0 / bpm

    # Cada gen representa una semicorchea
    seconds_per_step = (
        seconds_per_beat / 4.0
    )


    events = []


    for i, gene in enumerate(pattern):

        # Si es silencio no hacemos nada
        if gene == 0:
            continue


        # Diferente intensidad dependiendo
        # del tipo de golpe.

        if gene == 1:

            velocity = 75

        else:

            velocity = 110


        events.append({

            "step": i,

            "time_seconds":
                round(
                    i * seconds_per_step,
                    3
                ),

            "velocity": velocity

        })


    return events


# ============================================================
# 10. EXPORTAR Y ESCUCHAR CON JYTHON (JAVA MIDI)
# ============================================================

def create_midi(pattern, bpm=BPM):
    from javax.sound.midi import Sequence, MidiEvent, ShortMessage, MetaMessage
    from jarray import array

    sequence = Sequence(Sequence.PPQ, 480)
    track = sequence.createTrack()
    ticks_per_step = 120
    # Maracas General MIDI: aproximacion al sonido de un shaker.
    shaker_note = 70
    percussion_channel = 9

    microseconds_per_beat = int(round(60000000.0 / bpm))
    tempo_bytes = [(microseconds_per_beat >> shift) & 255 for shift in (16, 8, 0)]
    tempo_bytes = array([b if b < 128 else b - 256 for b in tempo_bytes], 'b')
    tempo_message = MetaMessage()
    tempo_message.setMessage(0x51, tempo_bytes, 3)
    track.add(MidiEvent(tempo_message, 0))

    for event in pattern_to_events(pattern, bpm):
        tick = event['step'] * ticks_per_step
        note_on = ShortMessage()
        note_on.setMessage(ShortMessage.NOTE_ON, percussion_channel,
                           shaker_note, event['velocity'])
        note_off = ShortMessage()
        note_off.setMessage(ShortMessage.NOTE_OFF, percussion_channel,
                            shaker_note, 0)
        track.add(MidiEvent(note_on, tick))
        track.add(MidiEvent(note_off, tick + ticks_per_step // 2))

    # Conserva los silencios finales para repetir exactamente dos compases.
    end = MetaMessage()
    end.setMessage(0x2F, array([], 'b'), 0)
    track.add(MidiEvent(end, len(pattern) * ticks_per_step))
    return sequence


def play_midi(sequence, repetitions=4):
    import time
    from javax.sound.midi import MidiSystem

    sequencer = MidiSystem.getSequencer()
    try:
        sequencer.open()
        sequencer.setSequence(sequence)
        sequencer.setLoopCount(repetitions - 1)
        print("Reproduciendo {0} veces. Ctrl+C para detener.".format(repetitions))
        sequencer.start()
        while sequencer.isRunning():
            time.sleep(0.05)
    finally:
        sequencer.close()


def main():
    import argparse
    import os
    from java.io import File
    from javax.sound.midi import MidiSystem, MidiUnavailableException

    parser = argparse.ArgumentParser(description="Genera y reproduce una intro de shaker.")
    parser.add_argument('--seed', type=int, default=SEED,
                        help='Semilla reproducible (por defecto: {0}).'.format(SEED))
    parser.add_argument('--sin-audio', action='store_true',
                        help='Solo genera el MIDI, sin reproducirlo.')
    parser.add_argument('--repeticiones', type=int, default=4,
                        help='Veces que se escucha el patron (por defecto: 4).')
    args = parser.parse_args()
    if args.repeticiones < 1:
        parser.error('--repeticiones debe ser al menos 1')

    print("Seed: {0}".format(args.seed))
    best_intro = genetic_shaker_intro(args.seed)
    print_pattern(best_intro)
    print("\nEVENTOS:")
    for event in pattern_to_events(best_intro):
        print(event)

    sequence = create_midi(best_intro)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'algoritmo_gen_shakers.mid')
    MidiSystem.write(sequence, 0, File(output_path))
    print("\nMIDI guardado: {0}".format(output_path))
    if not args.sin_audio:
        try:
            play_midi(sequence, args.repeticiones)
        except MidiUnavailableException as error:
            print("No se pudo abrir la salida de audio: {0}".format(error))
            print("Puedes abrir el MIDI guardado en tu reproductor o editor musical.")


if __name__ == '__main__':
    main()
