# import serial

# # Configure the serial connection
# ser = serial.Serial('/dev/serial0', 9600, timeout=1)  # Match the SIM7600 baud rate
# ser.write(b'AT\r\n')  # Send AT command
# response = ser.read(100)  # Read response
# print( "SIM7600 :" , response.decode('utf-8'))  # Print the module's response


from gpiozero import OutputDevice
from time import sleep

# Set up the GPIO pins
alarm = OutputDevice(27)
red_light = OutputDevice(22)
green_light = OutputDevice(24)
blue_light = OutputDevice(23)
flash_light = OutputDevice(26)

# List of all devices for testing
devices = {
    "Alarm": alarm,
    "Red Light": red_light,
    "Green Light": green_light,
    "Blue Light": blue_light,
    "Flash Light": flash_light,
}

# Test each pin
print("Testing output pins...")
try:
    for name, device in devices.items():
        print(f"Turning ON {name}")
        device.on()  # Turn the pin ON
        sleep(2)     # Wait for 2 seconds to observe
        print(f"Turning OFF {name}")
        device.off() # Turn the pin OFF
        sleep(1)     # Wait for 1 second before testing the next pin

    print("Testing complete. All pins toggled.")
except KeyboardInterrupt:
    print("\nExiting... Cleaning up GPIO.")
finally:
    # Clean up all GPIO pins
    for device in devices.values():
        device.off()  # Ensure all pins are turned off




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