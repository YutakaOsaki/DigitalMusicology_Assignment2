import random

from music21 import dynamics


def change_dynamics_decrescendo_measure(my_stream, measure: int, start_dynamic: str = "f",
                                        end_dynamic: str = "p"):
    """
    Create a decrescendo in the given measure
    :param my_stream:
    :param measure:
    :param start_dynamic:
    :param end_dynamic:
    :return:
    """
    for part in my_stream.parts:
        # Calculate the total number of notes which have a different offset
        full_measure = part.measure(measure)
        if full_measure is None:
            continue
        offsets = set([n.offset for n in full_measure.flatten().notes])
        number_of_notes = len(offsets)

        # Create a decrescendo
        decrescendo = dynamics.Diminuendo()
        decrescendo.number_of_notes = number_of_notes
        decrescendo.number_of_measures = 1
        decrescendo.start_measure = measure
        decrescendo.start_offset = 0
        decrescendo.end_measure = measure
        decrescendo.end_offset = max(offsets) if len(offsets) > 0 else 0
        decrescendo.start_dynamic = dynamics.Dynamic(start_dynamic)
        decrescendo.end_dynamic = dynamics.Dynamic(end_dynamic)

        # Add the decrescendo to the stream
        part.insert(0, decrescendo)
    return my_stream


import math
import numpy as np


def classical_dynamics_shape(my_stream, measure: int, min_volume: int = 40, max_volume: int = 100):
    """
    Create a classical dynamics shape for the given my_stream
    :param my_stream:
    :param measure:
    :param min_volume:
    :param max_volume:
    :return:
    """
    for part in my_stream.parts:
        # Create a round shape for the dynamics low - high - low
        full_measure = part.measure(measure)
        if full_measure is None:
            continue
        offsets = set([n.offset for n in full_measure.flatten().notes])
        number_of_notes = len(offsets)
        half_notes = math.ceil(number_of_notes / 2)

        # Create a smoothed crescendo
        def smoothed_crescendo(max_note, current_index, minimum_dynamic, maximum_dynamic):
            x = current_index / max_note
            return minimum_dynamic + (maximum_dynamic - minimum_dynamic) * x ** 2

        # Create a smoothed decrescendo
        def smoothed_decrescendo(max_note, current_index, minimum_dynamic, maximum_dynamic):
            x = current_index / max_note
            return minimum_dynamic + (maximum_dynamic - minimum_dynamic) * (1 - (1 - x) ** 2)

        if half_notes == 0 and number_of_notes > 0:
            half_notes = 1
        elif half_notes == 0 and number_of_notes == 0:
            continue

        # Create a crescendo
        for counter, n in enumerate(full_measure.flatten().notes):
            if counter < half_notes:
                n.volume.velocity = int(smoothed_crescendo(half_notes, counter, min_volume, max_volume))
            else:
                n.volume.velocity = int(smoothed_decrescendo(half_notes, counter - half_notes, min_volume, max_volume))
            n.volume.velocity += np.random.randint(-2, 3)
    return my_stream


def change_dynamics_crescendo_measure(my_stream, measure: int, start_dynamic: str = "p", end_dynamic: str = "f"):
    """
    Create a crescendo in the given measure
    :param my_stream:
    :param measure:
    :param start_dynamic:
    :param end_dynamic:
    :return:
    """
    for part in my_stream.parts:
        # Calculate the total number of notes which have a different offset
        full_measure = part.measure(measure)
        if full_measure is None:
            continue
        offsets = set([n.offset for n in full_measure.flatten().notes])
        number_of_notes = len(offsets)

        # Create a crescendo
        crescendo = dynamics.Crescendo()
        crescendo.number_of_notes = number_of_notes
        crescendo.number_of_measures = 1
        crescendo.start_measure = measure
        crescendo.start_offset = 0
        crescendo.end_measure = measure
        crescendo.end_offset = max(offsets) if len(offsets) > 0 else 0
        crescendo.start_dynamic = dynamics.Dynamic(start_dynamic)
        crescendo.end_dynamic = dynamics.Dynamic(end_dynamic)

        # Add the crescendo to the my_stream
        part.insert(0, crescendo)
    return my_stream


def change_dynamics_for_whole_piece(my_stream):
    """
    Change the dynamics for the whole piece
    :param my_stream:
    :return: stream
    """
    for i in range(19):
        my_stream = classical_dynamics_shape(my_stream, i, 20 + i * 2, 50 + i * 2)

    my_stream = change_dynamics_decrescendo_measure(my_stream, 19)
    my_stream = change_dynamics_crescendo_measure(my_stream, 20)
    my_stream = change_dynamics_crescendo_measure(my_stream, 21)
    my_stream = change_dynamics_decrescendo_measure(my_stream, 22)
    my_stream = change_dynamics_decrescendo_measure(my_stream, 23)
    my_stream = classical_dynamics_shape(my_stream, 24)
    my_stream = change_dynamics_crescendo_measure(my_stream, 25)
    my_stream = change_dynamics_crescendo_measure(my_stream, 26)
    for i in range(26, 42):
        my_stream = classical_dynamics_shape(my_stream, i)
    my_stream = change_dynamics_decrescendo_measure(my_stream, 43)
    my_stream = change_dynamics_decrescendo_measure(my_stream, 44)
    for i in range(45, 48):
        my_stream = classical_dynamics_shape(my_stream, i)
    my_stream = change_dynamics_crescendo_measure(my_stream, 48)
    my_stream = change_dynamics_decrescendo_measure(my_stream, 49)
    for i in range(50, 52):
        my_stream = classical_dynamics_shape(my_stream, i, 40, 60)
    my_stream = classical_dynamics_shape(my_stream, 52, 20, 30)
    my_stream = change_dynamics_decrescendo_measure(my_stream, 53, "mp", "p")
    j = 0
    for i in range(54, 68):
        my_stream = classical_dynamics_shape(my_stream, i, int(57 - j * 1.5), 100 - j * 2)
        j += 1
    my_stream = change_dynamics_decrescendo_measure(my_stream, 68, "mp", "p")
    my_stream = change_dynamics_decrescendo_measure(my_stream, 69, "pp", "ppp")

    return my_stream


def change_velocity_measures_in_stream(s, start_measure: int, end_measure: int, velocity_factor: float):
    """
    Change the velocity of notes in a stream for a range of measures.
    :param s:
    :param start_measure:
    :param end_measure:
    :param velocity_factor:
    :return:
    """
    for measure_number in range(start_measure, end_measure + 1):
        measure = s.measure(measure_number)
        if measure is not None:
            # modify intensity
            for n in measure.recurse().notes:
                # Calculate the new tone intensity and make sure it is in the range of the MIDI standard (0-127)
                n.volume.velocity = min(max(int(n.volume.velocity * velocity_factor), 0), 127)
    return s


def randomize_velocity_in_measures(s, start_measure: int, end_measure: int, delta_range: int):
    """
    Randomly adjusts the velocity of each note within a specified range in a music stream,
    limited to a specific range of measures.

    Parameters:
        s (music21.stream.Stream): The music stream to modify.
        start_measure (int): The starting measure number.
        end_measure (int): The ending measure number.
        delta_range (int): The maximum change (up or down) that can be applied to the velocity.

    Returns:
        music21.stream.Stream: The modified music stream.
    """
    for measure_number in range(start_measure, end_measure + 1):
        measure = s.measure(measure_number)
        if measure:
            for n in measure.notes:  # Only adjust notes directly in the measure
                if n.volume.velocity is not None:  # Check if velocity is defined
                    change = random.randint(-delta_range, delta_range)  # Random change within the specified range
                    new_velocity = max(0, min(127, n.volume.velocity + change))  # Apply the change and clamp the result
                    n.volume.velocity = new_velocity  # Set the new velocity
                else:
                    n.volume.velocity = random.randint(64 - delta_range, 64 + delta_range)  # Default value if None
    return s

