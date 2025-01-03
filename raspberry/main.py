import pyaudio
import wave
import datetime
from vosk import Model, KaldiRecognizer
import os



def recordAudio(stream, duration=10, sample_rate=16000, channels=1, chunk_size=1024):
    print("Recording...")
    frames = []

    for _ in range(int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    print("Recording finished")

    # Save the recorded audio to a file
    def generate_filename():
        current_time = datetime.datetime.now()
        date_str = current_time.strftime("%Y%m%d_%H%M%S")
        filename = f"recorded_audio_{date_str}.wav"
        return filename
    
    filename = os.path.join( os.getcwd(), "recorded" , generate_filename())
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Audio saved as {filename}")










# Initialize the Vosk model and recognizer
model = Model(r"vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()

stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

if __name__ == '__main__':
    try:
        while True:
            data = stream.read(4096)
            
            if recognizer.AcceptWaveform(data):
                text = recognizer.Result()
                print(text[14:-3])
                command = text[14:-3]
                
                if 'record' in command:
                    recordAudio(stream)
                    
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
