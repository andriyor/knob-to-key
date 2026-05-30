#!/usr/bin/env python3
# Reads the encoder via kernel dtoverlay+evdev instead of gpiozero.RotaryEncoder.
# gpiozero polls GPIO in userspace and misses steps under CPU load; the kernel
# driver counts pulses in hardware so no steps are lost.
import threading
import time
from signal import pause
from evdev import InputDevice, UInput, ecodes
from gpiozero import Button

# find it in cat /proc/bus/input/devices
ENCODER_PATH = '/dev/input/event4'
# steps-per-period=4 matches this encoder's 4 quadrature edges per detent,
# so the kernel emits exactly 1 EV_REL per physical click.
DEBOUNCE_DELAY = 0.05 # seconds

ui = UInput({
    ecodes.EV_KEY: [ecodes.KEY_UP, ecodes.KEY_DOWN, ecodes.KEY_ENTER]
})

def send_key(key):
    ui.write(ecodes.EV_KEY, key, 1)
    ui.write(ecodes.EV_KEY, key, 0)
    ui.syn()

def encoder_loop():
    encoder = InputDevice(ENCODER_PATH)
    last_click_time = 0

    for event in encoder.read_loop():
        if event.type == ecodes.EV_REL:
            current_time = time.time()

            if (current_time - last_click_time) < DEBOUNCE_DELAY:
                continue

            last_click_time = current_time

            if event.value > 0:
                send_key(ecodes.KEY_UP)
            elif event.value < 0:
                send_key(ecodes.KEY_DOWN)

threading.Thread(target=encoder_loop, daemon=True).start()

button = Button(27)
button.when_pressed = lambda: send_key(ecodes.KEY_ENTER)

pause()
