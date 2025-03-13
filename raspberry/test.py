import serial

# Define the parse function
def parse_gpgga(data: str):
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

# Configure the serial connection
gps_port = '/dev/ttyUSB0'  # Replace with your device port
baud_rate = 9600
gps = serial.Serial(gps_port, baud_rate, timeout=1)

print("Reading GPS data...")
try:
    while True:
        line = gps.readline().decode('ascii', errors='ignore')  # Read a line of NMEA data
        if line.startswith('$GPGGA'):  # Check for GPGGA sentences
            parsed_data = parse_gpgga(line)  # Use your function to parse the sentence
            if parsed_data:
                print(f"Latitude: {parsed_data['latitude']}, Longitude: {parsed_data['longitude']}")
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    gps.close()  # Close the serial connection



# import gpiozero
# import signal
# import time

# def single_click():
#     print("Single click detected")

# def double_click():
#     print("Double click detected")

# def triple_click():
#     print("Triple click detected")


# # Initialize the Vosk model and recognizer
# is_button_pressed = False

# def handle_click():
#     global click_count, last_click_time, is_button_pressed
    
#     current_time = time.time()
    
#     if current_time - last_click_time > click_timeout:
#         click_count = 1
#     else:
#         click_count += 1
    
#     last_click_time = current_time
    
#     # Wait a short period to determine if more clicks are coming
#     time.sleep(click_timeout)
    
#     if click_count == 1:
#         is_button_pressed = True
#         single_click()
#     elif click_count == 2:
#         is_button_pressed = False
#         double_click()
#     elif click_count == 3:
#         is_button_pressed = False
#         triple_click()

# click_count = 0
# last_click_time = 0
# click_timeout = 0.4  # Time window for double/triple clicks in seconds
# button = gpiozero.Button(22)
# button.when_pressed = handle_click


# signal.pause()  # Keeps the script running