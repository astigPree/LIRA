# import serial

# # Configure the serial connection
# ser = serial.Serial('/dev/serial0', 9600, timeout=1)  # Match the SIM7600 baud rate
# ser.write(b'AT\r\n')  # Send AT command
# response = ser.read(100)  # Read response
# print( "SIM7600 :" , response.decode('utf-8'))  # Print the module's response
from signal import pause
from gpiozero import Button
from gpiozero.pins.rpigpio import RPiGPIOFactory  # Use RPi.GPIO pin factory

factory = RPiGPIOFactory()
button = Button(2, pin_factory=factory)
def say_hello():
    print("Hello!")

button = Button(22)

button.when_pressed = say_hello

pause()



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