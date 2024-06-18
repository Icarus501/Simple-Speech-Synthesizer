from pathlib import Path
import simpleaudio
from synth_args import process_commandline
from nltk.corpus import cmudict
import re

class Synth:
    def __init__(self, wav_folder):
        self.diphones = self.get_wavs(wav_folder)

    def get_wavs(self, wav_folder):
        """Loads all the waveform data contained in WAV_FOLDER.
        Returns a dictionary, with unit names as the keys and the corresponding
        loaded audio data as values."""

        # crate a Audio Class
        my_audio = simpleaudio.Audio()
        # {"unit_name: loaded audio data"}
        diphones = {}

        for item in Path(wav_folder).iterdir():
            if item.is_file() and item.name not in diphones:
                my_audio.load(str(item))
                diphones[re.match(r"(.)*(?=\.)", item.name).group()] = my_audio.data
                self.rate = my_audio.rate
                self.nptye = my_audio.nptype
        return diphones

    def synthesise(self, phones, reverse=False, smooth_concat=False):
        """
        Synthesises a phone list into an audio utterance.
        :param phones: list of phones (list of strings)
        :param smooth_concat:
        :return: synthesised utterance (Audio instance)
        """

        # Get corresponding diphones sequence
        diphones_list = self.phones_to_diphones(phones)
        myaduio = simpleaudio.Audio()
        try:
            # insert an empty list if diphone doesn't exist in the diphone
            utt_data = list(
                map(lambda key: self.diphones[key.lower()] if self.diphones.get(key.lower()) is not None else [],
                    diphones_list))
            # change it into a flat list
            utt_data_flat = [diphone_data for sublist in utt_data for diphone_data in sublist]
            myaduio.data = simpleaudio.np.array(utt_data_flat, dtype=self.nptye)

            # use a temporal variable to store the final data file
            temp_data = utt_data[0]

            if smooth_concat:
                for n, item in enumerate(utt_data):
                    if n < len(utt_data) - 1:
                        temp_data = (overlap_list(temp_data, utt_data[n + 1], int(self.rate * 0.01)))
                # change float numbers into int
                int_temp_data = list(map(lambda number: int(number), temp_data))
                # dtype is important to be the same as diphones
                myaduio.data = simpleaudio.np.array(int_temp_data, dtype=self.nptye)

            if reverse == "signal":
                myaduio.data = simpleaudio.np.array(utt_data_flat[::-1])

        except KeyError:
            print("There is no corresponding diphone file!")

        return myaduio

    def phones_to_diphones(self, phones):
        """
        Converts a list of phones to the corresponding diphone units (to match units in diphones folder).
        :param phones: list of phones (list of strings)
        :return: list of diphones (list of strings)
        """
        diphones_list = [phones[n] + "-" + phones[n + 1] for n, item in enumerate(phones) if n < len(phones) - 1]
        return diphones_list


class Utterance:

    def __init__(self, phrase):
        """
        Constructor takes a phrase to process.
        :param phrase: a string which contains the phrase to process.
        """
        self.phrase = phrase

    def normalise_text(self, phrase):
        """
        Takes in the phrase and transform them into a sequence of words
        :param phrase: a phrase which have punctuations,etc.
        :return: a sequence of words
        """
        utt_tokens = [re.sub(r'[^\w\s^/\']', '', token.lower()) for token in phrase.split()]
        return utt_tokens

    def get_phone_seq(self, spell=False, reverse=None):
        """
        Returns the phone sequence corresponding to the text in this Utterance (i.e. self.phrase)
        :param spell:  Whether the text should be spelled out or not.
        :param reverse:  Whether to reverse something.  Either "words", "phones" or None
        :return: list of phones (as strings)
        """
        try:
            utt_tokens = self.normalise_text(self.phrase)
            # [[phone sequence 1],[phone sequence 2]...]
            if reverse == "words":
                utt_tokens = [item for item in reversed(self.normalise_text(self.phrase))]

            phones_string = list(
                map(lambda phrase: cmudict.dict().get(phrase)[0], utt_tokens))
            # turn it into a flat list, to remove some suffixes
            phone_sequence = [re.sub(r'[\d]', '', item) for sublist in phones_string for item in sublist]
            # Add silence to the beginning and end of the sequence
            phone_sequence[:0] = phone_sequence[len(phone_sequence):] = ["PAU"]
            if reverse == "phones":
                phone_sequence = [item for item in reversed(phone_sequence)]
            return phone_sequence

        except TypeError:
            print(f"There is no provided phonemes sequences for '{self.phrase}' in the cmudict")


def overlap_list(list1, list2, n):
    # generate a scale list
    scale = simpleaudio.np.linspace(0, 1, n)
    list1[-n:] = [x * y for x, y in zip(list1[-n:], reversed(scale))]
    list2[0:n] = [x * y for x, y in zip(list2[0:n], scale)]
    final_list = simpleaudio.np.zeros(len(list1) + len(list2) - n)
    final_list[0:len(list1) - n] = list1[0:len(list1) - n]
    final_list[len(list1):] = list2[n:]
    # overlapped part
    final_list[len(list1) - n:len(list1)] = [x + y for x, y in zip(list1[-n:], list2[0:n])]
    # don't exceed max_amp
    for index, item in enumerate(final_list):
        if item > simpleaudio.MAX_AMP:
            final_list[index] = simpleaudio.MAX_AMP
    return final_list


def process_file(textfile, args):
    """
    Takes the path to a text file and synthesises each sentence it contains
    :param textfile: the path to a text file (string)
    :param args:  the parsed command line argument object giving options
    :return: a list of Audio objects - one for each sentence in order.
    """
    # Extension C
    audio_obj = []
    with open(textfile) as f:
        for line in f:
            utt_out = Utterance(phrase=line)
            phone_seq_out = utt_out.get_phone_seq(spell=args.spell, reverse=args.reverse)
            diphone_synth_out = Synth(wav_folder=args.diphones)
            out_line = diphone_synth_out.synthesise(phone_seq_out, reverse=args.reverse)
            out_line.rate = diphone_synth_out.rate
            audio_obj.append(out_line)

            # Extension A : Amplitude change
            if args.volume:
                try:
                    out_line.rescale(val=args.volume / 100)
                except (ValueError, TypeError):
                    print("Expected scaling factor between 0 and 100")

            if args.play:
                out_line.play()

        if args.outfile:
            # a new audio class to store the "long" sentence
            my_audio = simpleaudio.Audio()
            # concatenate the sentences into one single waveform
            utt_data = [data for sublist in [obj.data for obj in audio_obj] for data in sublist]
            my_audio.data = simpleaudio.np.array(utt_data)
            # choose any sampling rate to be the rate of the single waveform
            my_audio.rate = audio_obj[0].rate
            my_audio.save(args.outfile)

    return audio_obj


# Make this the top-level "driver" function for your programme.  There are some hints here
# to get you going, but you will need to add all the code to make your programme behave
# correctly according to the commandline options given in args (and assignment description!).
def main(args):
    if args.phrase:
        utt = Utterance(phrase=args.phrase)
        phone_seq = utt.get_phone_seq(spell=args.spell, reverse=args.reverse)
        diphone_synth = Synth(wav_folder=args.diphones)

        # Extension B:
        out = diphone_synth.synthesise(phone_seq, reverse=args.reverse, smooth_concat=args.crossfade)
        # have the same sampling rate and
        out.rate = diphone_synth.rate

        # Extension A : Amplitude change
        if args.volume:
            try:
                out.rescale(val=args.volume / 100)
            except (ValueError, TypeError):
                print("Expected scaling factor between 0 and 100")

        if args.play:
            out.play()

        if args.outfile:
            out.save(args.outfile)

    # Extension C
    if args.fromfile:
        process_file(textfile=args.fromfile, args=args)

# DO NOT change or add anything below here
# (it just parses the commandline and calls your "main" function
# with the options given by the user)
if __name__ == "__main__":
    main(process_commandline())
