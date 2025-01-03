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

def openLights( mode: str):
    # Open the lights using your preferred method (e.g., using GPIO pins)
    print(f"Lights are being opened : {mode}")
    
    
def sendLocation():
    # Get the location from the module (GY-NEO6MV3)
    # Send the location using your preferred method (e.g., using SIM800L )
    # Send also pre-defined message
    print("Location is being sent") 



def PANIC_EVENT():
    # Activate the full emergency response when button is pressed
    print("PANIC EVENT")
    
    
    




def speak_in_commands(text : str , commands : list[str]):
    for command in commands:
        if command in text:
            return True
    return False


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
                
                if speak_in_commands(command , ['lira', 'leona', 'lila']):
                    # Name of the machine to activate all the command
                    if speak_in_commands(command , ['help', 'emergency', 'panic']):
                        # Emergency Response: Activate the full emergency response with certain voice commands:
                        sendLocation() # 1. Send location
                        openAlarm() # 2. Open alarm
                        recordAudio(stream) # 3. Record audio
                    
                    if speak_in_commands(command , ['lights', 'light' , 'lighting']):
                        # Lights: Turn on/off the device's lights.
                        if speak_in_commands(command, ['blink']):
                            openLights('blink')
                        elif speak_in_commands(command, ['on', 'steady', 'stay']):
                            openLights('on')
                        elif speak_in_commands(command, ['off', 'turn off']):
                            openLights('off')
                        
                    if speak_in_commands(command , ['record', 'recording', 'recognized', 'recognize']):
                        # Recording: Start/stop audio recording.
                        recordAudio(stream) 
                                        
                    if speak_in_commands(command , ['sms', 'message', 'chat', 'text', 'send', 'report']):
                        # SMS: Send a pre-defined text message.
                        sendLocation() 

                    
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
