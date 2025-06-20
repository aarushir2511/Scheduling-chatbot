import whisper
import pyttsx3
import sounddevice as sd
import scipy.io.wavfile as wav

model = whisper.load_model("base")

def record_audio(filename="input.wav", duration=5):
    fs = 44100
    print("🎙️ Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    wav.write(filename, fs, recording)

def transcribe_audio(audio_path):
    print("📝 Transcribing...")
    result = model.transcribe(audio_path)
    return result["text"]

def synthesize_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
