from gpiozero import RotaryEncoder, Button
from evdev import UInput, ecodes as e
from signal import pause

ui = UInput({
    e.EV_KEY: [
        e.KEY_UP,
        e.KEY_DOWN,
        e.KEY_ENTER,
    ]
})

def send_key(key):
    ui.write(e.EV_KEY, key, 1)
    ui.write(e.EV_KEY, key, 0)
    ui.syn()

encoder = RotaryEncoder(a=17, b=18, wrap=False, max_steps=0)
encoder.when_rotated_clockwise = lambda: send_key(e.KEY_DOWN)
encoder.when_rotated_counter_clockwise = lambda: send_key(e.KEY_UP)

button = Button(27)
button.when_pressed = lambda: send_key(e.KEY_ENTER)

pause()
