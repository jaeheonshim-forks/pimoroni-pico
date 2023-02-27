import gc
import time
import random
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN, PEN_P8
from ulab import numpy

"""
A random, computer effect.
Experiment with the damping, number of spawns and intensity to change the effect.
"""

# MAXIMUM OVERKILL
# machine.freq(250_000_000)

cu = CosmicUnicorn()
cu.set_brightness(0.5)
graphics = PicoGraphics(DISPLAY_COSMIC_UNICORN, pen_type=PEN_P8)


DAMPING_FACTOR = 0.95
NUMBER_OF_LIGHTS = 10
INTENSITY = 20

# Fill palette with a yellow
r, g, b = (230, 150, 0)
PALETTE_ENTRIES = 255
for x in range(PALETTE_ENTRIES):
    _ = graphics.create_pen(r * x // PALETTE_ENTRIES, g * x // PALETTE_ENTRIES, b)


def update():
    computer[:] *= DAMPING_FACTOR

    # Spawn random drops
    for _ in range(NUMBER_OF_LIGHTS):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        computer[y][x] = random.randint(0, INTENSITY)


def draw():
    # Copy the effect to the framebuffer
    memoryview(graphics)[:] = numpy.ndarray(numpy.clip(computer, 0, 1) * (PALETTE_ENTRIES - 1), dtype=numpy.uint8).tobytes()
    cu.update(graphics)


width = CosmicUnicorn.WIDTH
height = CosmicUnicorn.HEIGHT
computer = numpy.zeros((height, width))

t_count = 0
t_total = 0


while True:
    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        cu.adjust_brightness(+0.01)

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        cu.adjust_brightness(-0.01)

    tstart = time.ticks_ms()
    gc.collect()
    update()
    draw()
    tfinish = time.ticks_ms()

    total = tfinish - tstart
    t_total += total
    t_count += 1

    if t_count == 60:
        per_frame_avg = t_total / t_count
        print(f"60 frames in {t_total}ms, avg {per_frame_avg:.02f}ms per frame, {1000/per_frame_avg:.02f} FPS")
        t_count = 0
        t_total = 0

    # pause for a moment (important or the USB serial device will fail)
    # try to pace at 60fps or 30fps
    if total > 1000 / 30:
        time.sleep(0.0001)
    elif total > 1000 / 60:
        t = 1000 / 30 - total
        time.sleep(t / 1000)
    else:
        t = 1000 / 60 - total
        time.sleep(t / 1000)
