import soundfile as sf
import simpleaudio as sa

from models import TextToSpeech, VideoToText


if __name__ == "__main__":
    v2t = VideoToText()
    t2s = TextToSpeech()
    for text in v2t.get_text("example.webm"):
        print(text)
        audio = t2s.get_audio(text)
        # play audio
        sf.write("audio.wav", audio["audio"], audio["sampling_rate"])
        wave_obj = sa.WaveObject.from_wave_file("audio.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing
