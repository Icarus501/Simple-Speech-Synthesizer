# Speech Synthesizer

This project is a simple speech synthesizer that converts text input into an audio waveform of intelligible speech. It uses a basic waveform concatenation system with pre-recorded diphone sounds.

# Features
- **Text Normalization:** Converts input text to lowercase and removes punctuation.
- **Phonetic Expansion:** Transforms words into phonetic sequences using the nltk.corpus.cmudict pronunciation lexicon.
- **Diphone Concatenation:** Generates a waveform by concatenating diphone recordings in the correct order.
- **Audio Playback and Saving:** Plays the synthesized speech and optionally saves it to a file.
- **Volume Control:** Allows adjustment of the output volume.
- **Reverse Synthesis:** Provides options to reverse the speech in three ways: signal, words, and phones.
- **File Synthesis:** Reads text from a file and synthesizes each sentence sequentially.
- **Smooth Concatenation:** Implements cross-fading between diphones to reduce glitches.

# Usage
### Command Line Arguments
- **-p, --phrase:** The text phrase to synthesize.
- **-o, --outfile:** The output file to save the synthesized audio.
- **-v, --volume:** Volume level (0 to 100).
- **--crossfade:** Enable slightly smoother concatenation by cross-fading between diphone units.
- **--reverse signal:** Reverse the entire waveform signal.
- **--reverse words:** Reverse the order of words.
- **--reverse phones:** Reverse the order of phonetic sequences.
- **--fromfile:** Synthesize text from a specified file.

