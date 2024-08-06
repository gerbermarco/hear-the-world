import os
from time import sleep
import base64
import requests
from dotenv import load_dotenv
import RPi.GPIO as GPIO
from gpiozero import LED
from picamera2 import Picamera2, Preview
from openai import AzureOpenAI
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
from gpiozero import DigitalOutputDevice
import pygame

load_dotenv()

# Initialize LED
green_led = LED(12)

# Initialize SSD1306 LCD screen
RST, DC, SPI_PORT, SPI_DEVICE = 24, 23, 0, 0
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
disp.clear()
disp.display()

# Create blank image for drawing
width, height = disp.width, disp.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)

# Set font and padding
font = ImageFont.truetype("includes/fonts/PixelOperator.ttf", 16)
padding, top, bottom, x = -2, -2, height + 2, 0

# Setup touch sensor
touch_pin = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Camera setup
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (1024, 768)})
picam2.configure(preview_config)
image_path = "snapshots/snap.jpg"

# Vibration motor setup
vibration_motor = DigitalOutputDevice(25)

# Azure OpenAI setup
oai_api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
oai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
oai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
oai_api_version = "2023-12-01-preview"

client = AzureOpenAI(
    api_key=oai_api_key,
    api_version=oai_api_version,
    base_url=f"{oai_api_base}/openai/deployments/{oai_deployment_name}",
)

# Azure Speech Service setup
speech_key = os.getenv("SPEECH_KEY")
speech_region = os.getenv("SPEECH_REGION")

# Define audio file paths
audio_file_path_response = "audio/response.mp3"
audio_file_path_device_ready = "includes/audio_snippets/device_ready.mp3"
audio_file_path_analyze_picture = "includes/audio_snippets/analyze_view.mp3"
audio_file_path_hold_still = "includes/audio_snippets/hold_still.mp3"

# Initialize Pygame mixer for audio playback
pygame.mixer.init()


# Helper functions
# Function to update OLED display
def display_screen():
    disp.image(image)
    disp.display()


def scroll_text(display, text):
    # Create blank image for drawing
    width = disp.width
    height = disp.height
    image = Image.new("1", (width, height))

    # Get a drawing context
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.truetype("includes/fonts/PixelOperator.ttf", 16)
    font_width, font_height = font.getsize("A")  # Assuming monospace font, get width and height of a character

    # Calculate the maximum number of characters per line
    max_chars_per_line = width // font_width

    # Split the text into lines that fit within the display width
    lines = []
    current_line = ""
    for word in text.split():
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())

    # Calculate total text height
    total_text_height = (len(lines) * font_height) + 10

    # Initial display of the text
    y = 0
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    for i, line in enumerate(lines):
        draw.text((0, y + i * font_height), line, font=font, fill=255)
    display_screen()

    if total_text_height > height:
        # If text exceeds screen size, scroll the text
        y = 0
        while y > -total_text_height + height:
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            for i, line in enumerate(lines):
                draw.text((0, y + i * font_height), line, font=font, fill=255)
            disp.image(image)
            disp.display()
            y -= 2.5

        # Clear the display after scrolling is complete
        sleep(2)
        display_screen()


def vibration_pulse():
    vibration_motor.on()
    sleep(0.1)
    vibration_motor.off()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def play_audio(audio_file_path):
    pygame.mixer.music.load(audio_file_path)
    pygame.mixer.music.play()


def synthesize_speech(text_input):
    url = f"https://{speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": speech_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
        "User-Agent": "curl",
    }
    data = f"""<speak version='1.0' xml:lang='en-US'>
        <voice xml:lang='en-US' xml:gender='Male' name='en-US-ChristopherNeural'>
            {text_input}
        </voice>
    </speak>"""
    response = requests.post(url, headers=headers, data=data)
    with open(audio_file_path_response, "wb") as f:
        f.write(response.content)
    play_audio(audio_file_path_response)


# Play audio "Device is ready"
play_audio(audio_file_path_device_ready)

while True:
    try:
        green_led.on()
        input_state = GPIO.input(touch_pin)

        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x, top + 2), "Device is ready", font=font, fill=255)
        display_screen()

        if input_state == 1:

            play_audio(audio_file_path_hold_still)

            green_led.off()
            sleep(0.1)
            green_led.on()

            vibration_pulse()

            state = 0

            print("Taking photo 📸")
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((x, top + 2), "Taking photo ...", font=font, fill=255)
            display_screen()
            picam2.start()
            sleep(1)
            metadata = picam2.capture_file(image_path)
            # picam2.close()
            picam2.stop()

            play_audio(audio_file_path_analyze_picture)
            print("Analysing image ...")
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((x, top + 2), "Analysing image ...", font=font, fill=255)
            display_screen()

            # Open the image file and encode it as a base64 string
            base64_image = encode_image(image_path)

            if state == 0:
                green_led.blink(0.1, 0.1)

                response = client.chat.completions.create(
                    model=oai_deployment_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a device that helps visually impaired people recognize objects. Describe the pictures so that it is as understandable as possible for visually impaired people. Limit your answer to two to three sentences. Only describe the most important part in the image.",
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe this image:"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        },
                    ],
                    max_tokens=2000,
                )

            response = response.choices[0].message.content

            vibration_pulse()
            sleep(0.1)
            vibration_pulse()

            print("Response:")
            print(response)

            synthesize_speech(response)

            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            scroll_text(display_screen, response)

            state = 1
            sleep(5)

    except KeyboardInterrupt:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        display_screen()
        print("Interrupted")
        break

    except IOError:
        print("Error")
        print(IOError)
