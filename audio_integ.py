import os
import argparse
# [video to text]
import moviepy.editor as mp
#import speech_recognition as sr
# [audio analysis]
import librosa
import numpy as np
# [split audio]
from pydub import AudioSegment
from pydub.silence import split_on_silence
# [START speech_transcribe_async_word_time_offsets_gcs]
from google.cloud import speech_v1
# [Upload file to bucket]
from google.cloud import storage

# [speech recognizer]
#r = sr.Recognizer()
total_duration = 0
# [audio segment class - duration, list of words]
class AudioClass:
    def __init__(self, duration):
        self.duration = duration
        self.word_lst = []
        self.laugh_time = []

# [audio segment class - text, st, et, db, freq]
class WordClass:
    def __init__(self, text, st, et):
        self.text = text
        self.start_time = st
        self.end_time = et
        self.dbfs = 0
        self.freq_s = 0
        self.freq_e = 0

# [UPLOAD FILE TO Google_Storage]
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


# [WORD TIME STAMP]
def sample_long_running_recognize(storage_uri):
    """
    Print start and end time of each word spoken in audio file from Cloud Storage
    Args:
      storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
    """
    words = []

    client = speech_v1.SpeechClient()

    # storage_uri = 'gs://cloud-samples-data/speech/brooklyn_bridge.flac'

    # The number of channels in the input audio file (optional)
    audio_channel_count = 2
    # When set to true, each audio channel will be recognized separately.
    # The recognition result will contain a channel_tag field to state which
    # channel that result belongs to
    enable_separate_recognition_per_channel = True

    # When enabled, the first result returned by the API will include a list
    # of words and the start and end time offsets (timestamps) for those words.
    enable_word_time_offsets = True

    # The language of the supplied audio
    language_code = "en-US"
    config = {
        "audio_channel_count": audio_channel_count,
        "enable_separate_recognition_per_channel": enable_separate_recognition_per_channel,
        "enable_word_time_offsets": enable_word_time_offsets,
        "language_code": language_code,
    }
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(config, audio)

    print(u"Waiting for operation to complete...")
    response = operation.result()
    if len(response.results) != 0:
        # The first result includes start and end time word offsets
        result = response.results[0]
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))
        # Print the start and end time of each word

        for word in alternative.words:
            st = word.start_time.seconds * 1000 + word.start_time.nanos * 0.000001
            et = word.end_time.seconds*1000 + word.end_time.nanos * 0.000001
            print(u"Word: {}".format(word.word))
            print(
                u"Start time: {} miliseconds".format(st)
            )
            print(
                u"End time: {} miliseconds".format(et)
            )
            w = WordClass(word.word, st, et)
            words.append(w)
    else:
        print("no word input")
        print()
    return words

# [END speech_transcribe_async_word_time_offsets_gcs]


# [AUDIO ANAlYZE]
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

def audio_analyze_word(audio, word_list):
    for w in word_list:
        word_audio = audio[w.start_time:w.end_time + 1]
        w.dbfs = word_audio.dBFS
        #print("dB: ", w.dbfs)
        samples = word_audio.get_array_of_samples()
        arr = np.array(samples)
        w.freq_s = arr[0]
        w.freq_e = arr[-1]
        # 12000 이상 차이가 나면 글씨 높이 적용
        #print(type(arr))
        #print(arr)

        #print("freq: ", samples)
        #w.frequency =
        #print("hz: ", w.frequency)

    '''ten_seconds = 10 * 1000
    one_min = ten_seconds * 6

    first_10_seconds = song[:ten_seconds]
    last_5_seconds = song[-5000:]

    # up/down volumn
    beginning = first_10_seconds + 6

    # Save the result
    # can give parameters-quality, channel, etc 
    beginning.exoprt('result.flac', format='flac', parameters=["-q:a", "10", "-ac", "1"])'''
    return word_list


def find_laughter(seg, audio_seg, word_list):
    j = 0
    laugh_st = 0
    laugh_et = 0
    is_laugh = False
    dB = 0
    for i in range(len(audio_seg)-1):
        """if word_list[j].start_time <= i <= word_list[j].end_time:
            is_laugh = False
            continue"""
        """else: 
            if i > word_list[j].end_time:
                j += 1"""
        #print(i)
        if audio_seg[i].max_dBFS >= -17:  # laugh false
            if is_laugh == False:
                is_laugh = True
                laugh_st = i
                laugh_et = i
            else:
                laugh_et += 1
            dB = audio_seg[i].max_dBFS

        elif audio_seg[i].max_dBFS < -17:
            if is_laugh == True:
                if laugh_et - laugh_st >= 800:
                   seg.laugh_time.append((dB, laugh_st, laugh_et))
                is_laugh = False
    print(len(seg.laugh_time))
    for i in range(len(seg.laugh_time)):
        print(seg.laugh_time[i])


def audio_analyze_sliced(out_file, i):
    y, sr = librosa.load(out_file)
    audio = AudioSegment.from_wav(out_file)
    #print(audio.rms)
    duration = librosa.get_duration(y=y, sr=sr) * 1000

    #print(len(audio))
    #print("duration", duration)

    global total_duration
    total_duration += duration
    seg = AudioClass(duration)

    # word time stamps
    upload_blob("changseul2", out_file, out_file)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--storage_uri",
        type=str,
        default="gs://changseul2/split_audio_{}.wav".format(i)
        # default="audio.wav",
    )
    args = parser.parse_args()
    word_list = sample_long_running_recognize(args.storage_uri)

    #analyze words - dB
    seg.word_lst = audio_analyze_word(audio, word_list)

    """for w in word_list:
        print("text: ", w.text)
        print("start_time: ", w.start_time)
        print("end_time :", w.end_time)
        print("dB : ", w.dbfs)
        print("freq_start: ", w.freq_s)
        print("freq_end: ", w.freq_e)
        print()
    """
    # 웃음소리 찾기
    find_laughter(seg, audio, seg.word_lst)
    return seg


def audio_analysis_main(inputfile_name):
    #video_to_audio
    clip = mp.VideoFileClip(inputfile_name)
    clip.audio.write_audiofile("audio.wav")

    # audio_chunk
    sound_file = AudioSegment.from_wav("audio.wav")
    dBFS = sound_file.dBFS
    audio_chunks = split_on_silence(sound_file, min_silence_len=500, silence_thresh=-30, keep_silence=300) # oh hi hi hi -> 400, -30, 400

    audio_list = []

    #for all audio_segments
    for i, chunk in enumerate(audio_chunks):
        out_file = "split_audio_{}.wav".format(i)
        print("exporting", out_file)
        chunk.export(out_file, format="wav")

        audio_list.append(audio_analyze_sliced(out_file, i))

        os.remove("split_audio_{}.wav".format(i))

    global total_duration
    print(total_duration)
    return audio_list

if __name__ == "__main__":
    audio_analysis_main('input_video/bigbang.mp4')