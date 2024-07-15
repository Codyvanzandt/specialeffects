import asyncio
import math


def linear(t):
    return t


def quadratic_in(t):
    return t**2


def quadratic_out(t):
    return 1 - (1 - t) ** 2


def quadratic_in_out(t):
    if t < 0.5:
        return 2 * t**2
    return 1 - (-2 * t + 2) ** 2 / 2


def cubic_in(t):
    return t**3


def cubic_out(t):
    return 1 - (1 - t) ** 3


def cubic_in_out(t):
    if t < 0.5:
        return 4 * t**3
    return 1 - (-2 * t + 2) ** 3 / 2


def sine_in(t):
    return 1 - math.cos((t * math.pi) / 2)


def sine_out(t):
    return math.sin((t * math.pi) / 2)


def sine_in_out(t):
    return -(math.cos(math.pi * t) - 1) / 2


def interpolate_color(start_color, end_color, progress):
    start_h, start_s, start_v = start_color
    end_h, end_s, end_v = end_color

    # Correct hue interpolation
    if end_h < start_h:
        end_h += 360
    interpolated_h = (start_h + (end_h - start_h) * progress) % 360

    # Interpolate saturation and value
    interpolated_s = start_s + (end_s - start_s) * progress
    interpolated_v = start_v + (end_v - start_v) * progress

    return (int(interpolated_h), int(interpolated_s), int(interpolated_v))


async def interpolate_color_over_time(
    start_color, end_color, duration, easing_func="linear"
):
    easing_function = globals()[easing_func]
    start_time = asyncio.get_event_loop().time()

    while True:
        current_time = asyncio.get_event_loop().time()
        progress = (current_time - start_time) / duration

        if progress >= 1:
            break

        eased_progress = easing_function(progress)
        current_color = interpolate_color(start_color, end_color, eased_progress)

        yield current_color

        await asyncio.sleep(0.1)
