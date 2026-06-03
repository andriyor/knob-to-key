# knob-to-key

Translates a rotary encoder into keyboard input (UP, DOWN, ENTER) using the Linux kernel's evdev interface. Turning the encoder emits arrow keys; pressing the button emits Enter.

## Hardware wiring

| Component | GPIO (BCM) |
|-----------|-----------|
| Encoder CLK (A) | 17 |
| Encoder DT (B) | 18 |
| Button | 27 |

## Setup

Install dependencies:

```sh
uv sync
```

Enable the kernel rotary encoder driver by adding to `/boot/firmware/config.txt`:

```
dtoverlay=rotary-encoder,pin_a=17,pin_b=18,relative_axis=1,steps-per-period=4
```

Reboot, then find the encoder's event device:

```sh
cat /proc/bus/input/devices
```

Update `ENCODER_PATH` in `encoder_driver.py` to match (default: `/dev/input/event4`).

Grant access to `/dev/uinput` (required to emit virtual key events).

**Temporary (until next reboot):**

```sh
sudo chmod 666 /dev/uinput
```

**Permanent — create a udev rule:**

```sh
echo 'KERNEL=="uinput", MODE="0666"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Run:

```sh
uv run encoder_driver.py
```

## Why evdev instead of gpiozero

gpiozero's `RotaryEncoder` polls GPIO in userspace, which misses steps under CPU load. The kernel `rotary-encoder` dtoverlay counts quadrature pulses in hardware — no steps are lost regardless of system load. `steps-per-period=4` matches a standard encoder's 4 edges per detent, so the kernel emits exactly one `EV_REL` event per physical click.
