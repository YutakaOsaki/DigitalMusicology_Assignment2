import music21
from music21 import interval, midi, note, duration


def adjust_note_in_measures(s, start_measure: int, end_measure: int, note_index: int, pitch_interval: int):
    """
    Adjusts the pitch of a specific note in a given range of measures.

    Parameters:
        s (music21.stream.Stream): The music stream to modify.
        start_measure (int): The starting measure number.
        end_measure (int): The ending measure number.
        note_index (int): The index of the note in its measure to adjust (0-based index).
        pitch_interval (int): The number of semitones to transpose the note (positive or negative).

    Returns:
        music21.stream.Stream: The modified music stream.
    """
    for measure_number in range(start_measure, end_measure + 1):
        measure = s.measure(measure_number)  # Get the specific measure
        if measure:
            notes = [n for n in measure.notes]  # Get all notes in the measure
            if len(notes) > note_index:  # Check if the note index is within the range of available notes
                target_note = notes[note_index]
                target_note.transpose(interval.ChromaticInterval(pitch_interval), inPlace=True)
    return s


def accentuate_highest_note_in_measure(s, measure_number: int, accent_factor: float = 1.2):
    """
    Increases the velocity of all notes with the highest pitch in the specified measure.

    :param s: music21 stream object
    :param measure_number: the measure number to find and accentuate the highest notes
    :param accent_factor: the factor by which to increase the velocity (e.g., 1.2 for 20% increase)
    :return: modified music21 stream
    """
    measure = s.measure(measure_number)
    if measure is None:
        print(f"No measure found with the number {measure_number}.")
        return s

    highest_pitch = None
    notes_to_accentuate = []

    # Ensure to only handle note and chord objects
    for element in measure.recurse().notesAndRests:
        if hasattr(element, 'isNote') and element.isNote:
            if highest_pitch is None or element.pitch.midi > highest_pitch:
                highest_pitch = element.pitch.midi
                notes_to_accentuate = [element]
            elif element.pitch.midi == highest_pitch:
                notes_to_accentuate.append(element)
        elif hasattr(element, 'isChord') and element.isChord:
            for p in element.pitches:
                if highest_pitch is None or p.midi > highest_pitch:
                    highest_pitch = p.midi
                    notes_to_accentuate = [element]
                elif p.midi == highest_pitch:
                    notes_to_accentuate.append(element)

    # Increase the velocity of all notes/chords with the highest pitch
    for n in notes_to_accentuate:
        if hasattr(n, 'isNote') and n.isNote:
            n.volume.velocity = min(max(int(n.volume.velocity * accent_factor), 0), 127)
        elif hasattr(n, 'isChord') and n.isChord:
            for note in n.notes:
                note.volume.velocity = min(max(int(note.volume.velocity * accent_factor), 0), 127)

    return s


def increase_volume_of_highest_note_in_triples(score, start_measure_number: int, end_measure_number: int,
                                               track_number=0,
                                               volume_increase=10):
    """
    Increases the volume of the highest-pitched note in triples of thirty-second notes within specified measures
    in a specific track of a score.

    Params:
        score (music21.stream.Score): The Score object to be processed.
        track_number (int): The track number to process (0-indexed).
        start_measure_number (int): The measure number to start processing (inclusive).
        end_measure_number (int): The measure number to end processing (inclusive).
        volume_increase (int): The amount by which to increase the volume of the highest-pitched note.

    Returns:
        music21.stream.Score: The modified Score object with increased volumes for the highest-pitched notes in the specified measures of the specified track.
    """

    target_part = score.parts[track_number]

    for i in range(start_measure_number, end_measure_number + 1):
        target_measure = target_part.measure(i)
        notes = target_measure.notes
        # Iterate through each triple group of notes in the measure
        for j in range(len(notes) - 2):
            note1, note2, note3 = notes[j], notes[j + 1], notes[j + 2]
            if note1.duration.quarterLength == 0.125 and note2.duration.quarterLength == 0.125 and note3.duration.quarterLength == 0.125:
                # Determine the highest note
                pitches = [note1.pitch.midi, note2.pitch.midi, note3.pitch.midi]
                max_pitch = max(pitches)
                if note1.pitch.midi == max_pitch:
                    highest_note = note1
                elif note2.pitch.midi == max_pitch:
                    highest_note = note2
                else:
                    highest_note = note3

                # Increase the volume of the highest note
                highest_note.volume.velocity = min(highest_note.volume.velocity + volume_increase, 127)

        print(f"Measure {i} adjusted.")

    return score


def increase_volume_of_higher_notes_in_track(score, start_measure_number: int, end_measure_number: int, track_number=0,
                                             volume_increase=10):
    """
    Increases the volume of the higher-pitched note in pairs of sixteenth notes within specified measures in a specific track of a score.

    Params:
        score (music21.stream.Score): The Score object to be processed.
        track_number (int): The track number to process (1-indexed).
        start_measure_number (int): The measure number to start processing (inclusive).
        end_measure_number (int): The measure number to end processing (inclusive).
        volume_increase (int): The amount by which to increase the volume of the higher-pitched note.

    Returns:
        music21.stream.Score: The modified Score object with increased volumes for higher-pitched notes in the specified measures of the specified track.
    """

    target_part = score.parts[track_number]

    for i in range(start_measure_number, end_measure_number + 1):
        target_measure = target_part.measure(i)
        for note1, note2 in zip(target_measure.notes[:-1], target_measure.notes[1:]):
            if note1.duration.quarterLength == 0.25 and note2.duration.quarterLength == 0.25:
                # Extract pitches; handle both Note and Chord objects
                pitch1 = note1.pitches[-1] if isinstance(note1, music21.chord.Chord) else note1.pitch
                pitch2 = note2.pitches[-1] if isinstance(note2, music21.chord.Chord) else note2.pitch

                # Increase volume of the higher-pitched note
                if pitch1 > pitch2:
                    note1.volume.velocity += volume_increase
                else:
                    note2.volume.velocity += volume_increase

        print(f"Measure {i} adjusted.")

    return score


def add_pedal_event(s, measure, beat, is_pedal_down, measure_offset):
    """
    Adds a pedal event to the stream at a specified beat within a measure.

    Parameters:
        s (music21.stream.Stream): The music stream to add the event to.
        measure (music21.stream.Measure): The measure where the event is added.
        beat (float): The beat within the measure to add the pedal event.
        is_pedal_down (bool): True if the pedal is pressed, False if released.
        measure_offset (float): The offset of the measure within the stream.
    """
    pedal_event = midi.ControlChange()
    pedal_event.channel = 1
    pedal_event.control = 64  # Sustain pedal control number
    pedal_event.value = 127 if is_pedal_down else 0
    pedal_event.time = measure_offset + (beat - 1) * measure.quarterLength / measure.timeSignature.beatCount

    s.events.append(pedal_event)
    return s


def apply_pedal_to_measures(s, start_measure, end_measure):
    """
    Applies the sustain pedal to specific measures in a 6/8 time signature stream.
    Pedal is pressed at 1/8 and released at 3/8, then pressed again at 4/8 and released at 6/8.

    Parameters:
        s (music21.stream.Stream): The music stream to modify.
        start_measure (int): The starting measure number (1-indexed).
        end_measure (int): The ending measure number (1-indexed).
    """
    for m in s.getElementsByClass('Measure'):
        if start_measure <= m.measureNumber <= end_measure:
            measure_offset = m.offset

            add_pedal_event(s, m, 1, True, measure_offset)  # Pedal down at 1/8
            add_pedal_event(s, m, 3, False, measure_offset)  # Pedal up at 3/8
            add_pedal_event(s, m, 4, True, measure_offset)  # Pedal down at 4/8
            add_pedal_event(s, m, 6, False, measure_offset)  # Pedal up at 6/8
    return s


def apply_trill_to_hand_note(s, hand, measure_number, note_index, semitones, trill_speed, trill_duration):
    """
    Applies a custom trill effect to a specific note within a specified measure and specific hand part
    in a music21 stream.

    Parameters:
        s (music21.stream.Stream): The music stream containing the measures and parts.
        hand (str): The hand part to apply the trill, 'left' or 'right'.
        measure_number (int): The measure number to find the note to trill.
        note_index (int): The index of the note within the specified measure to apply the trill.
        semitones (int): The number of semitones to transpose the original note by for the trill effect.
        trill_speed (float): The duration of each individual note in the trill, in quarter lengths.
        trill_duration (float): The total duration of the trill effect, in quarter lengths.
    """
    part = s.parts[0 if hand == 'right' else 1]
    target_measure = part.measure(measure_number)
    notes_in_measure = list(target_measure.flatten().notes)
    if note_index < len(notes_in_measure):
        trill_start_note = notes_in_measure[note_index]
        start_offset = trill_start_note.offset
        num_trills = int(trill_duration / trill_speed)
        trill_interval = interval.ChromaticInterval(semitones)
        trill_start_note.duration.quarterLength = trill_speed
        for i in range(1, num_trills):
            if i % 2 == 0:
                new_note = note.Note(trill_start_note.pitch,
                                     duration=duration.Duration(trill_speed))
            else:
                trill_pitch = trill_start_note.pitch.transpose(trill_interval)
                new_note = note.Note(trill_pitch,
                                     duration=duration.Duration(trill_speed))
            target_measure.insert(start_offset + i * trill_speed, new_note)
    return s
