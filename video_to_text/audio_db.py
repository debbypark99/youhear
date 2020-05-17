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

# [input video]
inputfile_name = "bigbang.mp4"

# [speech recognizer]
#r = sr.Recognizer()

# [audio segment class - duration, list of words]
class AudioClass:
    def __init__(self, duration):
        self.duration = duration
        self.word_list = []

# [audio segment class - text, st, et, db, freq]
class WordClass:
    def __init__(self, text, st, et):
        self.text = text
        self.start_time = st
        self.end_time = et
        self.dbfs = 0

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
        st = 0
        et = 0
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


def audio_analyze_word(out_file, word_list):
    audio = AudioSegment.from_wav(out_file)

    for w in word_list:
        print(w.text)
        word_audio = audio[w.start_time:w.end_time + 1]
        w.dbfs = word_audio.dBFS
        print("dB: ", w.dbfs)

    return word_list


def audio_analyze_sliced(out_file, i):
    y, s = librosa.load(out_file)
    duration = librosa.get_duration(y=y, sr=s) * 1000  # miliseconds
    print(duration)
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

    # analyze words - dB
    word_list = audio_analyze_word(out_file, word_list)

    # 테스트 확인용 print
    for w in word_list:
        print(w.text)
        print(w.start_time)
        print(w.end_time)
        print(w.dbfs)
        print()
    return seg


# [main function]

def audio_analysis_main():
    #video_to_audio
    clip = mp.VideoFileClip(inputfile_name)
    clip.audio.write_audiofile("audio.wav")

    # audio_chunk
    sound_file = AudioSegment.from_wav("audio.wav")
    audio_chunks = split_on_silence(sound_file, min_silence_len=400, silence_thresh=-30, keep_silence=400) # oh hi hi hi -> 400, -30, 400

    audio_list = []

    #for all audio_segments
    for i, chunk in enumerate(audio_chunks):
        out_file = "split_audio_{}.wav".format(i)
        print("exporting", out_file)
        chunk.export(out_file, format="wav")

        audio_list.append(audio_analyze_sliced(out_file, i))

    return audio_list



if __name__ == "__main__":
    audio_analysis_main()