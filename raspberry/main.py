import pyaudio
import wave
import datetime
from vosk import Model, KaldiRecognizer
import os
import gpiozero
import signal
import time
import serial
import RPi.GPIO as GPIO
import time
from threading import Thread

button = 2
GPIO.setmode(GPIO.BCM)  # Use Broadcom (BCM) pin numbering
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Setup GPIO2 as input with pull-up

device_turn_on = True
has_main_action = False
alarm = gpiozero.OutputDevice(27)
red_light =gpiozero.OutputDevice(22)
green_light =gpiozero.OutputDevice(24)
blue_light =gpiozero.OutputDevice(23)
flash_light = gpiozero.OutputDevice(26)
# button = gpiozero.Button(2)
# button = None


def parse_gpgga(data : str):
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

def read_gps(gps: serial.Serial, timeout=300):
    if not gps:
        print("Failed to open GPS serial port.")
        return None
    start_time = time.time()
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        if elapsed_time > timeout:
            print("Timeout: GPS data not fetched within 5 minutes.")
            return None 
        line = gps.readline().decode('ascii', errors='replace')
        if line.startswith('$GPGGA'):
            gps_data = parse_gpgga(line)
            if gps_data:
                return gps_data
            else:
                print("Failed to parse GPS data")



def check_balance(sms : serial.Serial):
    try:
        # Send the USSD command for balance inquiry
        sms.write(b'AT+CUSD=1,"*123#",15\r')  # Replace *123# with your network's USSD code
        time.sleep(2)  # Wait for the response

        # Read the response from the SMS module
        response = sms.read_all().decode('ascii', errors='ignore')
        print("Balance Response:", response)

        # Check if the response contains "OK" or valid information
        if "OK" in response or any(char.isdigit() for char in response):  # Check for numeric balance info
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking balance: {e}")
        return False  # Return False if an exception occurs

        
        
def get_sms_phone_numbers( sms : serial.Serial):
    if sms is None:
        print("Failed to open SMS serial port.")
        return []
    sms.write(b'AT\r')
    time.sleep(1)
    sms.write(b'AT+CMGF=1\r')  # Set SMS mode to text
    time.sleep(1)
    sms.write(b'AT+CMGL="ALL"\r')  # List all SMS messages
    time.sleep(1)
    
    response = sms.read_all().decode('ascii', errors='replace')
    
    phone_numbers = []
    for line in response.split('\r\n'):
        if line.startswith('+CMGL'):
            parts = line.split(',')
            if len(parts) >= 3:
                phone_number = parts[2].strip('"')
                phone_numbers.append(phone_number)
    
    return phone_numbers

def send_sms( sms : serial.Serial , phone_number : str, message : str):
    if sms is None:
        print("Failed to open SMS serial port.")
        return False
    sms.write(b'AT\r')
    time.sleep(1)
    sms.write(b'AT+CMGF=1\r')  # Set SMS mode to text
    time.sleep(1)
    sms.write(f'AT+CMGS="{phone_number}"\r'.encode())
    time.sleep(1)
    sms.write(f'{message}\x1A'.encode())  # \x1A is the ASCII code for Ctrl+Z
    time.sleep(3)
    
    response = sms.read_all().decode('ascii', errors='replace')
    if 'OK' in response:
        print("Message sent successfully!")
        return True
    else:
        print("Failed to send message.")
        return False

def recordAudio(stream, duration=10, sample_rate=16000, channels=1, chunk_size=1024):
    print("Recording...")
    frames = []

    try:
        # Record audio in chunks for the specified duration
        for _ in range(int(sample_rate / chunk_size * duration)):
            data = stream.read(chunk_size, exception_on_overflow=False)  # Avoid potential overflow errors
            frames.append(data)

        print("Recording finished")

        # Function to generate a timestamped filename
        def generate_filename():
            current_time = datetime.datetime.now()
            date_str = current_time.strftime("%Y%m%d_%H%M%S")
            filename = f"recorded_audio_{date_str}.wav"
            return filename

        # Ensure the "recorded" directory exists
        output_dir = os.path.join(os.getcwd(), "recorded")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create the full file path
        filename = os.path.join(output_dir, generate_filename())

        # Save the recorded audio to a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"Audio saved as {filename}")
    
    except Exception as e:
        print(f"An error occurred while recording or saving audio: {e}")



def openAlarm(mode: str , timeout=90):
    # Open the alarm using GPIO pins and keep it active for 90 seconds
    print("Alarm is being opened")
    
    if mode == "on":
        alarm.on()
        time.sleep(timeout)  # Alarm active for 90 seconds
        alarm.off()
        print("Alarm turned off after 90 seconds")
    
    elif mode == "off":
        alarm.off()
        print("Alarm turned off immediately")
    
    elif mode == "SOS":
        # SOS signal: on and off sequence
        for _ in range(9):  # 9 cycles for SOS (3 short, 3 long, 3 short)
            alarm.on()
            time.sleep(0.5)  # Short beep (0.5 seconds)
            alarm.off()
            time.sleep(0.5)
        time.sleep(1)  # Pause between cycles
        for _ in range(9):
            alarm.on()
            time.sleep(1)  # Long beep (1 second)
            alarm.off()
            time.sleep(0.5)
        alarm.off()
        print("SOS signal sent and alarm turned off")
        
    elif mode == "device_on":
        alarm.on()
        print("Device alarm activated with continuous sound sequence")
        # Continuous sound sequence for device mode
        for _ in range(10):
            alarm.on()
            time.sleep(0.2)
            alarm.off()
            time.sleep(0.2)
            
    elif mode == "device_off":
        alarm.on()
        print("Device alarm activated with continuous sound sequence")
        # Continuous sound sequence for device mode
        for _ in range(10):
            alarm.on()
            time.sleep(0.5)
            alarm.off()
            time.sleep(0.2)
    
def openSOSLights(mode: str):
    # Open the lights using your preferred method (e.g., using GPIO pins)
    print(f"Lights are being opened: {mode}")

    if mode == "SOS":
        # SOS signal: 3 short, 3 long, 3 short with different colors
        colors = [(red_light, "Red"), (green_light, "Green"), (blue_light, "Blue")]

        for i in range(3):  # 3 short flashes
            for light, color_name in colors:
                light.on()
                print(f"Short flash: {color_name}")
                time.sleep(0.5)
                light.off()
                time.sleep(0.5)

        for i in range(3):  # 3 long flashes
            for light, color_name in colors:
                light.on()
                print(f"Long flash: {color_name}")
                time.sleep(1)
                light.off()
                time.sleep(0.5)

        for i in range(3):  # 3 short flashes
            for light, color_name in colors:
                light.on()
                print(f"Short flash: {color_name}")
                time.sleep(0.5)
                light.off()
                time.sleep(0.5)

        print("SOS signal with disco effect sent")

    elif mode == "on":
        flash_light.on()
        print("Lights turned on")

    elif mode == "off":
        red_light.off()
        green_light.off()
        blue_light.off()
        flash_light.off()
        print("Lights turned off")
    
    
def sendLocation(gps : serial.Serial, sms : serial.Serial):
    # Get the location from the module (GY-NEO6MV3)
    if not sms or not gps:
        print("Failed to send location. Either SMS or GPS is not available.")
        return
    location = read_gps(gps)
    # Send the location using your preferred method (e.g., using SIM800L )
    phone_numbers = get_sms_phone_numbers(sms)
    sms_text = "Emergency: I am in immediate danger and require urgent assistance. My last known location is as follows {latitude}, {longitude}"
    sms_text_without_gps = "Emergency! Please help me! My location is unknown please check my location to another device."  
    for phone_number in phone_numbers:
        if location:
            send_sms(sms, phone_number, sms_text.format(latitude=location['latitude'], longitude=location['longitude']))
        else:
            send_sms(sms, phone_number, sms_text_without_gps)
    # Send also pre-defined message
    print("Location is being sent")



def speak_in_commands(text : str , commands : list[str]):
    for command in commands:
        if command in text:
            return True
    return False


def single_click():
    global device_turn_on
    print("Single click detected")
    device_turn_on = not device_turn_on
    if device_turn_on:
        print("Device turned on")
        openAlarm("device_on")
    else:
        print("Device turned off")
        openAlarm("device_off")

def double_click():
    print("Double click detected")

def triple_click():
    print("Triple click detected")


# Initialize the Vosk model and recognizer
is_button_pressed = False
click_count = 0
last_click_time = 0
click_timeout = 0.4  # Time window for double/triple clicks in seconds

def reset_clicks():
    global click_count, last_click_time , is_button_pressed
    click_count = 0
    last_click_time = 0
    is_button_pressed = False


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
        reset_clicks()
    elif click_count == 2:
        is_button_pressed = False
        double_click()
        reset_clicks()
    elif click_count == 3:
        is_button_pressed = False
        triple_click()
        reset_clicks()
    
# Global flag to stop the thread
stop_thread = False

def thread_button_event():
    global sms
    global green_light
    try:
        while not stop_thread:  # Run only if stop_thread is False
            if GPIO.input(2) == GPIO.LOW:  # Check if the button is pressed
                print("Button was pressed!")
                handle_click()
                time.sleep(0.2)  # Debounce
            if not has_main_action:
                if not check_balance(sms):
                    green_light.on()
                    print("No enough load balance!")
                    time.sleep(0.2)  # Debounce
                    
    except Exception as e:
        print(f"Error: {e}")

# Start the thread (non-daemon for proper cleanup)

model = Model(r"vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()

stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

if __name__ == '__main__':
    try:
        
        print("Starting...")
        # button.when_pressed = handle_click
        
        # Set up the serial connection (adjust the port and baud rate as needed)
        gps = serial.Serial('/dev/ttyS0', 115200, timeout=1)
        sms = serial.Serial('/dev/serial0', 115200, timeout=1)
        # gps = None
        # sms = None
                
        button_thread = Thread(target=thread_button_event, daemon=False)
        button_thread.start()
                
        
        while True:
            
            if not device_turn_on:
                continue
            
            if is_button_pressed:
                continue
            
            
            data = stream.read(4096)
            
            if recognizer.AcceptWaveform(data):
                text = recognizer.Result()
                print( "Recognized: " + text[14:-3])
                command = text[14:-3]
                
                if speak_in_commands(command , ['lira', 'leona', 'lila' , 'laura', 'later', 'lita', 'era']):
                    # Name of the machine to activate all the command
                    if speak_in_commands(command , ['help', 'emergency', 'panic']):
                        has_main_action = True
                        # Emergency Response: Activate the full emergency response with certain voice commands:
                        sendLocation( gps=gps , sms=sms ) # 1. Send location
                        openAlarm("on") # 2. Open alarm
                        recordAudio(stream) # 3. Record audio
                        has_main_action = False
                    
                    if speak_in_commands(command , ['lights', 'light' , 'lighting']):
                        # Lights: Turn on/off the device's lights.
                        has_main_action = True
                        if speak_in_commands(command, ['blink']):
                            openSOSLights('SOS')
                        elif speak_in_commands(command, ['on', 'steady', 'stay']):
                            openSOSLights('on')
                        elif speak_in_commands(command, ['off', 'turn off']):
                            openSOSLights('off')
                        has_main_action = False
                        
                    if speak_in_commands(command , ['record', 'recording', 'recognized', 'recognize']):
                        # Recording: Start/stop audio recording.
                        has_main_action = True
                        recordAudio(stream) 
                        has_main_action = False
                                        
                    if speak_in_commands(command , ['sms', 'message', 'chat', 'text', 'send', 'report']):
                        # SMS: Send a pre-defined text message.
                        has_main_action= True
                        sendLocation( gps=gps , sms=sms ) # 1. Send location
                        has_main_action = False

    
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
        stop_thread = True  # Signal the thread to stop
        button_thread.join()  # Wait for the thread to finish
        alarm.close()
        red_light.close()
        green_light.close()
        blue_light.close()
        flash_light.close() 
        GPIO.cleanup()  # Final GPIO cleanup