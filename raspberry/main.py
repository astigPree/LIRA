import pyaudio
import wave
import datetime
from vosk import Model, KaldiRecognizer
import os
import gpiozero
import signal
import time
import serial


def parse_gpgga(data):
    fields = data.split(',')
    if len(fields) < 6:
        return None

    latitude = fields[2]
    latitude_dir = fields[3]
    longitude = fields[4]
    longitude_dir = fields[5]

    return {
        'latitude': latitude + ' ' + latitude_dir,
        'longitude': longitude + ' ' + longitude_dir
    }

def read_gps(gps):
    while True:
        line = gps.readline().decode('ascii', errors='replace')
        if line.startswith('$GPGGA'):
            gps_data = parse_gpgga(line)
            if gps_data:
                return gps_data
            else:
                print("Failed to parse GPS data")

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
    if mode == "blink":
        pass
    elif mode == "on":
        pass
    elif mode == "off":
        pass
    
    
def sendLocation():
    # Get the location from the module (GY-NEO6MV3)
    location = read_gps(gps)
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



def single_click():
    print("Single click detected")

def double_click():
    print("Double click detected")

def triple_click():
    print("Triple click detected")


# Initialize the Vosk model and recognizer
is_button_pressed = False
click_count = 0
last_click_time = 0
click_timeout = 0.4  # Time window for double/triple clicks in seconds

def handle_click():
    global click_count, last_click_time, is_button_pressed
    
    current_time = time.time()
    
    if current_time - last_click_time > click_timeout:
        click_count = 1
    else:
        click_count += 1
    
    last_click_time = current_time
    
    # Wait a short period to determine if more clicks are coming
    time.sleep(click_timeout)
    
    if click_count == 1:
        is_button_pressed = True
        single_click()
    elif click_count == 2:
        is_button_pressed = False
        double_click()
    elif click_count == 3:
        is_button_pressed = False
        triple_click()

def reset_clicks():
    global click_count, last_click_time
    click_count = 0
    last_click_time = 0



model = Model(r"vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()

stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()


if __name__ == '__main__':
    try:
        
        button = gpiozero.Button(22)
        button.when_pressed = handle_click
        
        # Set up the serial connection (adjust the port and baud rate as needed)
        gps = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        
        while True:
            
            if is_button_pressed:
                continue
            
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

    
    except gpiozero.exc.BadPinFactory as e:
        print(f"GPIO error: {e}")    
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        if stream :
            stream.stop_stream()
            stream.close()
        if mic:
            mic.terminate()
