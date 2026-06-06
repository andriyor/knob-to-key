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

**KY-040 only:** enable the kernel rotary encoder driver by adding to `/boot/firmware/config.txt`:

```
dtoverlay=rotary-encoder,pin_a=17,pin_b=18,relative_axis=1,steps-per-period=4
```

If you have a PEC11R-4220K-S0024 (or another clean full-step encoder), skip this — use `encode_driver_gpozero.py` directly instead.

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

- KY-040: `uv run encoder_driver.py`
- PEC11R-4220K-S0024 (or clean full-step encoder): `uv run encode_driver_gpozero.py`

## A note on KY-040 and similar

Cheap breakout-board encoders such as the KY-040 use a half-step quadrature scheme and have severe contact bounce. With the kernel `rotary-encoder` driver at `steps-per-period=4` they emit spurious or missed steps. To use a KY-040 you would need to change to `steps-per-period=2` **and** add 100 nF decoupling capacitors from each encoder line (CLK, DT) to ground to suppress bounce — even then reliability is marginal. Use `encoder_driver.py` (the evdev/kernel driver) for KY-040; its `DEBOUNCE_DELAY` provides an additional software debounce layer that `encode_driver_gpozero.py` lacks.

The **PEC11R-4220K-S0024** (Bourns) works out of the box with the configuration in this README: it is a full-step encoder with clean edges, so `steps-per-period=4` gives exactly one event per physical detent with no extra hardware. Either driver works.

If your encoder produces double-steps or missed steps, first try halving `steps-per-period` before adding hardware filters.

## Why evdev instead of gpiozero

gpiozero's `RotaryEncoder` polls GPIO in userspace, which misses steps under CPU load. The kernel `rotary-encoder` dtoverlay counts quadrature pulses in hardware — no steps are lost regardless of system load. `steps-per-period=4` matches a standard encoder's 4 edges per detent, so the kernel emits exactly one `EV_REL` event per physical click.
