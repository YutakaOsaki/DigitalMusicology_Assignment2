def change_duration_specific_beats_in_stream(s, start_measure: int, end_measure: int, target_beats: list,
                                             duration_factor: float):
    """
    Change the duration of notes in a stream at specific beats.
    :param s:  Stream
    :param start_measure: int
    :param end_measure: int
    :param target_beats: should be a list of beats where duration needs to be changed, e.g., [1, 3]
    :param duration_factor: float
    :return:
    """
    for measure_number in range(start_measure, end_measure + 1):
        measure = s.measure(measure_number)
        if measure is not None:
            for n in measure.notes:  # Iterating over notes directly
                if n.beat in target_beats:  # Check if the note's beat is in the list of target beats
                    n.duration.quarterLength *= duration_factor
    return s


def adjust_durations_for_specific_measure(score, measure_number, track1_new_durations=None):
    """
    Adjusts the durations of notes in a specific measure of a score and ensures that the durations
    of notes in another track are updated proportionally to match the total duration of the modified measure.

    Parameters:
        score (music21.stream.Score): The score containing the music parts.
        measure_number (int): The measure number to adjust durations for.
        track1_new_durations (list[float]): List of new durations for notes in track1.

    Returns:
        music21.stream.Score: The score with adjusted durations.
    """
    # Get the relevant tracks from the score
    if track1_new_durations is None:
        track1_new_durations = [0.75, 0.4, 0.3, 0.3, 1.25]
    track1 = score.parts[1]
    track0 = score.parts[0]

    # Get the specific measure from each track
    track1_measure = track1.measure(measure_number)
    track0_measure = track0.measure(measure_number)

    # Update durations of notes in track1
    for note, new_duration in zip(track1_measure.notes, track1_new_durations):
        note.duration.quarterLength = new_duration

    # Calculate total new duration of the modified track1 measure
    total_new_duration = sum(track1_new_durations)

    # Update durations of notes in track0 proportionally
    track0_notes = track0_measure.notes
    total_original_duration = sum(note.duration.quarterLength for note in track0_notes)
    scale_factor = total_new_duration / total_original_duration if total_original_duration != 0 else 0

    for note in track0_notes:
        note.duration.quarterLength *= scale_factor

    return score


def execute_adjust_durations_for_specific_measure(score, start_measure_number, end_measure_number):
    """
    Adjust the durations of notes in a range of measures of a score.
    :param score:
    :param start_measure_number:
    :param end_measure_number:
    :return:
    """
    for i in range(start_measure_number, end_measure_number + 1):
        score = adjust_durations_for_specific_measure(score, i)
        print(f"Measure {i} adjusted.")

    return score


def change_duration_in_measure(score, measure_number, target_duration, new_duration, track_number=0):
    """
    Changes the duration of notes with a specific duration in a specified measure of a specified track within a MIDI file.

    Params:
        midi_file_path (str): Path to the MIDI file to be processed.
        track_number (int): The track number to process (0-indexed).
        measure_number (int): The measure number where notes' duration will be changed (1-indexed).
        target_duration (float): The duration of the notes to be changed.
        new_duration (float): The new duration to be applied to the notes.

    Returns:
        music21.stream.Score: The modified Score object with updated note durations in the specified measure.
    """
    # Access the specific part (track)
    target_part = score.parts[track_number]

    # Access the specific measure
    target_measure = target_part.measure(measure_number)
    # Iterate over all notes in the measure
    for note in target_measure.notes:
        # Check if the note's duration matches the target duration
        if note.duration.quarterLength == target_duration:
            # Change the note's duration to the new specified duration
            note.duration.quarterLength = new_duration

    return score


def execute_change_duration_in_measure(score, start_measure_number, end_measure_number):
    # Adjust durations from start_measure_number to end_measure_number
    for i in range(start_measure_number, end_measure_number + 1):
        score = change_duration_in_measure(score, 15, 0.5, 0.3, 0)
        print(f"Measure {i} adjusted.")

    return score


def accelerate_measure(score, measure_number, accelerate_rate, track_numbers=[0, 1]):
    """
    Accelerates the durations of notes within a specified measure by adjusting their lengths relative to the first note's duration, such that the last note's duration is accelerate_rate times faster than the first note's duration.

    Parameters:
        score (music21.stream.Score): The score object containing the measure to be accelerated.
        measure_number (int): The number of the measure to be accelerated.
        accelerate_rate (float): The rate at which the durations should accelerate.
            means the last note's duration will be half of the first note's duration.
        track_numbers (list of int): List of track numbers to process (0 or 1).

    Returns:
        music21.stream.Score: The modified score object with the accelerated measure.
    """
    for track_number in track_numbers:
        track = score.parts[track_number]
        measure = track.measure(measure_number)
        if measure is None:
            continue
        notes = measure.recurse().notes
        base_duration = notes[0].duration.quarterLength
        num_notes = len(notes)
        for i, note in enumerate(notes):
            if i == 0:
                continue
            accelerate_factor = accelerate_rate ** ((i + 1) / num_notes)
            note.duration.quarterLength = base_duration / accelerate_factor

    return score