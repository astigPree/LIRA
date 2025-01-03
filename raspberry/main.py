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


def openAlarm():
    # Open the alarm using your preferred method (e.g., using GPIO pins) and the duration is 90 seconds
    print("Alarm is being opened")

def openLights():
    # Open the lights using your preferred method (e.g., using GPIO pins)
    print("Lights are being opened")
    
    
def sendLocation():
    # Get the location from the module (GY-NEO6MV3)
    # Send the location using your preferred method (e.g., using SIM800L )
    # Send also pre-defined message
    print("Location is being sent") 
    


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
                
                if 'help' in command:
                    # Emergency Response: Activate the full emergency response with certain voice commands:
                    sendLocation() # 1. Send location
                    openAlarm() # 2. Open alarm
                    recordAudio() # 3. Record audio
                 
                if 'light' in command:
                    # Lights: Turn on/off the device's lights.
                    openLights()
                    
                if 'record' in command:
                    # Recording: Start/stop audio recording.
                    recordAudio(stream) 
                                    
                if 'message' in command:
                    # SMS: Send a pre-defined text message.
                    sendLocation() 
            
                    
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
