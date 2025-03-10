from pocketsphinx import LiveSpeech

# Initialize LiveSpeech for offline recognition
speech = LiveSpeech(
    rate=16000,             # Ensure the sampling rate matches the microphone's configuration
    buffer_size=2048,       # Reduce buffer size for resource-constrained devices
    no_search=False,        # Enable recognition
    full_utt=False          # Process partial utterances
)

if __name__ == '__main__':
    try:
        print("Start speaking...")

        # Continuous speech recognition loop
        for phrase in speech:
            # Convert recognized speech to text
            text = str(phrase)
            print(f"You said: {text}")

            # Process recognized command if needed
            command = text.strip()
            print(f"Command: {command}")
    except KeyboardInterrupt:
        print("\nExiting...")









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