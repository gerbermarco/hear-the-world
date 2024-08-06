# Hear the world using Azure OpenAI and a Raspberry Pi

## Overview

In my free time, I have a strong interest in electronics, particularly in microcomputers like the Raspberry Pi, microcontrollers like the ESP32, and various sensors and circuits. I'm fascinated by the integration of hardware, physics, and software to create amazing projects, which is now more accessible than ever. I learn best through practical tasks, so I always set my own challenges. This project is one of those challenges, and I’m excited to share it with you to demonstrate that not everything is as complex as it seems. I am not an expert, so your feedback is more than welcome.

This project is designed to help visually impaired individuals by recognizing objects in images and providing audio feedback. To achieve this I use a Raspberry Pi Zero 2 W, camera, OLED display, speaker, vibration motor, and Azure OpenAI and Speech Service for image recognition and text-to-speech synthesis. The user interface includes a touch sensor to trigger image capture and analysis.

The project is explained in greater detail in my blog post: [Hear the world using Azure OpenAI and a Raspberry Pi - marcogerber.ch](https://marcogerber.ch/hear-the-world-using-azure-openai-and-a-raspberry-pi/)

![Components overview front](https://marcogerber.ch/wp-content/uploads/2024/07/overview-components-front.jpg)

## Table of contents

- [Requirements](#requirements)
  - [Hardware](#hardware)
  - [Software](#software)
  - [Wiring](#wiring)
- [Raspberry Pi setup](#raspberry-pi-setup)
- [Functions](#functions)
- [Running the project](#running-the-project)

## Requirements

### Hardware

- Raspberry Pi Zero 2 W
- Zero Spy Camera
- SSD1306 OLED Display
- Vibration Motor
- Touch Sensor
- MAX98357A Amplifier
- Adafruit Mini Oval Speaker
- LED and 220 Ohms Resistor
- Jumper cables

### Software

- Azure OpenAI Service with a gpt-4o model deployed
- Azure Speech Service
- Python 3.x
- Required Python libraries: `os`, `time`, `base64`, `requests`, `python-dotenv`, `requests`, `RPi.GPIO`, `gpiozero`, `openai`, `Adafruit-SSD1306`, `adafruit-python-shell`, `pillow==9.5.0`, `pygame`
- Other libraries and tools: `git`, `curl`, `libsdl2-mixer-2.0-0`, `libsdl2-image-2.0-0`, `libsdl2-2.0-0`, `libopenjp2-7`, `libcap-dev`, `python3-picamera2`, `i2samp.py`

### Wiring

Please check my blog post for further wiring information: [Hear the world using Azure OpenAI and a Raspberry Pi - marcogerber.ch](https://marcogerber.ch/hear-the-world-using-azure-openai-and-a-raspberry-pi/)

![Components overview breadboard](https://marcogerber.ch/wp-content/uploads/2024/07/overview-components-breadboard.jpg)


## Raspberry Pi setup

1. Enable I2C serial communication protocol in raspi-config:

    ```bash
    sudo raspi-config > Interface Options > I2C > Yes > Finish
    sudo reboot
    ```

2. Install missing libraries and tools:

    ```bash
    sudo apt-get install git curl libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0 libopenjp2-7
    sudo apt install -y python3-picamera2 libcap-dev
    ```

3. Install I2S Amplifier prerequisites:

    ```bash
    sudo apt install -y wget
    wget https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/raw/main/i2samp.py
    sudo -E env PATH=$PATH python3 i2samp.py
    ```

4. Create a Python virtual environment:

    ```bash
    python3 -m venv --system-site-packages .venv
    source .venv/bin/activate
    ```

5. Install Python modules:

    ```bash
    python3 -m pip install python-dotenv requests RPi.GPIO gpiozero openai Adafruit-SSD1306 adafruit-python-shell pillow==9.5.0 pygame
    ```

6. Update the `.env` file in the root directory of the project with your own values:

    ```env
    AZURE_OPENAI_ENDPOINT=<your_azure_openai_endpoint>      # The endpoint for your Azure OpenAI service.
    AZURE_OPENAI_API_KEY=<your_azure_openai_api_key>        # The API key for your Azure OpenAI service.
    AZURE_OPENAI_DEPLOYMENT=<your_azure_openai_deployment>  # The deployment name for your Azure OpenAI service.
    SPEECH_KEY=<your_azure_speech_key>                      # The key for your Azure Speech service.
    SPEECH_REGION=<your_azure_speech_region>                # The region for your Azure Speech service.
    ```


## Functions

### `display_screen()`

Updates the OLED display with the current image.

### `scroll_text(display, text)`

Scrolls text on the OLED display if it exceeds the screen size.

### `vibration_pulse()`

Activates the vibration motor for a short pulse.

### `encode_image(image_path)`

Encodes the image at the given path to a base64 string.

### `play_audio(audio_file_path)`

Plays the audio file at the given path.

### `synthesize_speech(text_input)`

Synthesizes speech using Azure Speech services from the given text input.

### `main()`

Main loop that initializes the system, waits for user input via the touch sensor, captures and analyzes images, and provides audio feedback.

## Running the project

1. Ensure your Raspberry Pi is properly set up with the necessary hardware and software prerequisites.
2. Run the Python script:

    ```bash
    python3 main.py
    ```

3. The system will initialize and display "Device is ready" on the OLED screen as well as play an audio description.
4. Touch the sensor to capture an image, which will be analyzed and described using Azure OpenAI services. The description will be played back via audio.
