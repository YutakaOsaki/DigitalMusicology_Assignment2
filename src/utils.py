from music21 import converter, stream


def get_stream(filename: str = "./Berceuse_op_57/corrected_midi_score.mid") -> 'music21.stream.Stream':
    """
    Get a music21 stream from a midi file.
    :param filename: str
    :return: music21.stream.Stream
    """
    my_stream = converter.parse(filename, format='midi', forceSource=True,
                                quantizePost=False, quarterLengthDivisors=(128, 48))
    return my_stream


def save_midi(my_stream: 'stream.Stream', filename: str = "./Berceuse_op_57/generated_midi_score.mid"):
    """
    Save a music21 stream to a midi file.
    :param my_stream: music21.stream.Stream
    :param filename: str
    """
    my_stream.write('midi', fp=filename)


def extract_measures_and_save(input_stream, output_midi_path: str, start_measure: int, end_measure: int):
    """
    Extracts specified measures from a given music21 stream and saves them to a new MIDI file.

    :param input_stream: music21 stream object that contains the music data.
    :param output_midi_path: path where the new MIDI file will be saved.
    :param start_measure: the first measure to include in the extraction.
    :param end_measure: the last measure to include in the extraction.
    """
    new_stream = stream.Score()

    for part in input_stream.parts:
        # Extracts a specified range of bars
        extracted_measures = part.measures(start_measure, end_measure)

        new_part = stream.Part()
        for measure in extracted_measures:
            new_part.append(measure)
        new_stream.append(new_part)

    # save
    new_stream.write('midi', fp=output_midi_path)


def count_notes_in_measure(score, measure_number):
    """
    Calculate the number of notes in a specific measure of a score.

    Parameters:
        score (music21.stream.Score): The score object to analyze.
        measure_number (int): The measure number to analyze.
    """
    for part_index, part in enumerate(score.parts):
        measure = part.measure(measure_number)
        notes = measure.notes
        print(f"Part {part_index + 1}: {len(notes)} notes in measure {measure_number}")
