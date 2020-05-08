import moviepy.editor as mp
import speech_recognition as sr
import librosa
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
import matplotlib.pyplot as plt

# input video
inputfile_name = "bigbang.mp4"

# speech recognizer
r = sr.Recognizer()

# audio segment class - length, text, db, freq
# frame 별로
class Audio_Segment:
    def __init__(self):
        self.length = 0
        self.text = None
        self.dB = []
        #self.freq


# analyze audio length db freq
def audio_length_db_freq(audio_file):
    n_fft = 2048
    y, s = librosa.load(audio_file)
    stft = np.abs(librosa.stft(y, n_fft=n_fft))
    #fft = np.abs(librosa.fft_frequencies(s, n_fft=n_fft))
    #db_median = (librosa.amplitude_to_db(fft, ref=np.median))
    tempo, beats = librosa.beat.beat_track(y, s)
    length = librosa.frames_to_time(beats, s)
    db_median = librosa.amplitude_to_db(stft, ref=np.median)
    freq = librosa.fft_frequencies(s, n_fft=n_fft)
    print(length, ", ", db_median, ", ", freq)

    #mean_dB = np.mean(db_median)
    #print(db_median)



def main():
    # video to audio
    clip = mp.VideoFileClip(inputfile_name)
    clip.audio.write_audiofile("audio.wav")
    sound_file = AudioSegment.from_wav("audio.wav")

    # audio_chunk
    audio_chunks = split_on_silence(sound_file, min_silence_len=400, silence_thresh=-35, keep_silence=200)


    for i, chunk in enumerate(audio_chunks):
        out_file = "split_audio_{}.wav".format(i)
        print("exporting", out_file)
        chunk.export(out_file, format="wav")
        with sr.AudioFile(out_file) as source:
            audio = r.listen(source)
            try:
                r.recognize_google(audio)
                print("Converted Audio Is : \n" + r.recognize_google(audio))

            except Exception as e:
                print("Error {} : ".format(e))
            audio_length_db_freq(out_file)

if __name__ == "__main__":
    main()
