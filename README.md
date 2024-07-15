# SpecialEffects

SpecialEffects is a Python library that allows you to orchestrate special effect sequences with smart lights, audio
files, and custom functions.

The ideal user wants to run light and sound effects inside Python, but doesn't want
to become an expert in either asynchronous programming or professional-grade special effects tools.

## Features

* Intuitive orchestration of custom Python functions alongside audio and light effects
* Pluggable architecture; bring your own smart lights or audio player
* Fully asynchronous without requiring the user to understand asynchronous programming

## Installation

You can install SpecialEffects using pip:

```commandline
pip install specialeffects
```

## Basic Example

The following example configures two Kasa brand smart lights, and then
orchestrates the
following effect:

* Turn on both lights
* Delay for one second
* Play a sound file
* Delay for one second
* Turn off both lights

```python
from specialeffects import SpecialEffect
from specialeffects.lights import KasaLight

effect = (
    SpecialEffect()
    .add_light("light1", KasaLight("10.0.0.1"))
    .add_light("light2", KasaLight("10.0.0.2"))
    .add_light_on("light1")
    .add_light_on("light2")
    .add_delay(1)
    .add_sound("path/to/soundfile.mp3")
    .add_delay(1)
    .add_light_off("light1")
    .add_light_off("light2")
)

effect.play()
```

## Advanced Example

SpecialEffects is lightweight by design, with a small number of methods.
But this simplicity doesn't prevent you from building complex effects.
Instead of forcing you to learn a complicated special effects framework,
the complexity is shifted to Python itself, where you're already comfortable.

The following function, `create_lightning_storm_effect()`, creates a lightning storm effect across
a variable number of light objects.
Despite the complexity of the effect, the use of the SpecialEffects library is rather limited.
Most of the code is pure Python, dedicated to the implementing the randomness of the storm.

```python
import random
from specialeffects import SpecialEffect


def create_lightning_storm_effect(light_objects, number_strikes=20):
    # Create the effect object
    effect = SpecialEffect()

    # Name and configure the lights
    light_names = [f"light_{i}" for i in range(len(light_objects))]
    for light_name, light_object in zip(light_names, light_objects):
        effect.add_light(light_name, light_object)

    # Choose a color for the lightning
    lightning_color = (60, 100, 100)  # Bright yellow in the HSV color system

    for _ in range(number_strikes):
        # Stagger when the lightning strikes happen by putting random delays between them.
        delay_until_strike = random.uniform(0.5, 3)
        effect.add_delay(delay_until_strike)

        # Choose how many lights will be involved in the strike
        number_of_lights_involved = random.randrange(1, len(light_names) + 1)

        # Choose which lights will be involved in the strike
        involved_light_names = random.sample(light_names, number_of_lights_involved)

        # Make the involved lights flash yellow
        for involved_light_name in involved_light_names:
            effect.add_light_color(involved_light_name, lightning_color)

        # Add a short delay so the flash is visible
        effect.add_delay(0.1)

        # Make the involved lights turn off
        for involved_light_name in involved_light_names:
            effect.add_light_off(involved_light_name)

        # Make thunder rumble after a short random delay
        # Assumes the thunder mp3 files already exist locally
        thunder_effect = random.choice(["thunder1.mp3", "thunder2.mp3", "thunder3.mp3"])
        effect.add_delay(random.uniform(0.1, 1))
        effect.add_sound(thunder_effect)

    return effect


# Usage
from specialeffects.lights import KasaLight

lights = [KasaLight("10.0.0.1"), KasaLight("10.0.0.2"), KasaLight("10.0.0.3")]
storm_effect = create_lightning_storm_effect(lights, number_strikes=30)
storm_effect.play()
```

## Tutorial

The next few sections walk you through all of SpecialEffect's features.

SpecialEffects has built-in support for Kasa brand smart lights, though you can easily configure
other smart light brands to work.
For clarity, this tutorial uses the built-in Kasa API and leaves configuring other smart light brands until the
end.

## Special Effect Construction

`SpecialEffect` objects can be built either with or without method chaining.

In the following example, the two special effects are completely equivalent:

```python
from specialeffects import SpecialEffect
from specialeffects.lights import KasaLight

effect_with_chaining = (
    SpecialEffect()
    .add_light("light1", KasaLight("10.0.0.1"))
    .add_light_on("light1")
    .add_delay(1)
    .add_light_off("light1")
)

effect_without_chaining = SpecialEffect()
effect_without_chaining.add_light("light1", KasaLight("10.0.0.1"))
effect_without_chaining.add_light_on("light1")
effect_without_chaining.add_delay(1)
effect_without_chaining.add_light_off("light1")
```

## Light Groups

Lights can be grouped together and then controlled as a single unit.

`.add_light_group()` takes a name for the light group, and then an arbitrary number of light names to add to the group.

```python
from specialeffects import SpecialEffect
from specialeffects.lights import KasaLight

effect = (
    SpecialEffect()
    .add_light("light1", KasaLight("10.0.0.1"))
    .add_light("light2", KasaLight("10.0.0.2"))
    .add_light_group("both_lights", "light1", "light2")  # A new light group is defined
    .add_light_on("both_lights")
    .add_delay(1)
    .add_light_off("both_lights")
)

effect.play()
```

## Sections

Effects can be grouped into named sections, which can then be reused later. Sections do not just define a sequence of
effects, they also schedule those effects to be run, just as if you had
added the effects without using a section.

The following example defines a section, `play_sound_then_pause`, that plays a sound then pauses for three seconds.
In the example, `play_sound_then_pause` is scheduled to run three times:

* Once when it is defined
* Once when it is reused
* And then once more when it is reused with an additional effect tacked on

```python
from specialeffects import SpecialEffect

effect = (
    SpecialEffect()
)

# "play_sound_then_pause" is both defined and scheduled to run
with effect.section("play_sound_then_pause"):
    effect.add_sound("path/to/soundfile.mp3")
    effect.add_delay(3)

# "play_sound_then_pause" is scheduled to run again
with effect.section("play_sound_then_pause"):
    pass

# "play_sound_then_pause" is scheduled to run again, with an additional delay is added to the end.
with effect.section("play_sound_then_pause"):
    effect.add_delay(1)

effect.play()
```

## Repeating Sections

Another advantage of sections is that they can be scheduled to repeat a given number of times.

Sections take a `repeat` argument, which can be an integer or `None`. An integer schedules the section to repeat an
integer number
of times.
`None` schedules the section to repeat infinitely.

```python
from specialeffects import SpecialEffect

effect = (
    SpecialEffect()
)

# "play_sound_then_pause" repeats three times
with effect.section("play_sound_then_pause", repeat=3):
    effect.add_sound("path/to/soundfile.mp3")
    effect.add_delay(3)

# "play_sound_then_pause" is resused and repeats infinitely
with effect.section("play_sound_then_pause", repeat=None):
    pass
```

## Unnamed and Nested Sections

It sometimes increases clarity to use unnamed or nested sections.

```python
from specialeffects import SpecialEffect
from specialeffects.lights import KasaLight

effect = (
    SpecialEffect()
    .add_light("light1", KasaLight("10.0.0.1"))
    .add_light("light2", KasaLight("10.0.0.2"))
)

# defines and schedules the entirety of "outer_section"
with effect.section("outer_section"):
    with effect.section():
        effect.add_light_on("light1")
        effect.add_delay(1)

    with effect.section():
        effect.add_light_on("light2")
        effect.add_delay(1)

# schedules the entirety of "outer_section"
with effect.section("outer_section"):
    pass
```

## Parallel Sections

All effects run in parallel, with the only delays being those caused by `.add_delay()`.
However, it is often tricky to use `.add_delay()` to get the precise effect one is looking for.

Consider an effect where one light starts red, delays for one second, then becomes blue.
Simultaneously, a second light starts blue, delays for one second, then becomes red.

One might naively write this code:

```python
from specialeffects import SpecialEffect
from specialeffects.lights import KasaLight

effect = (
    SpecialEffect()
    .add_light("light1", KasaLight("10.0.0.1"))
    .add_light("light2", KasaLight("10.0.0.2"))
)

red = (0, 100, 100)
blue = (240, 100, 100)

with effect.section("red_to_blue"):
    effect.add_light_color("light1", red)
    effect.add_delay(1)
    effect.add_light_color("light1", blue)

with effect.section("blue_to_red"):
    effect.add_light_color("light2", blue)
    effect.add_delay(1)
    effect.add_light_color("light2", red)

effect.play()
```

However, the `.add_delay(1)` in the `red_to_blue` section causes a one-second delay *before* the `blue_to_red` section
has a chance to run. Because of this delay, the two sections no longer execute in parallel.

The correct approach would be to set both lights to their initial colors, delay for one second, then set the lights to
their second colors:

```python
with effect.section("red_to_blue_and_blue_to_red"):
    effect.add_light_color("light1", red)
    effect.add_light_color("light2", blue)
    effect.add_delay(1)
    effect.add_light_color("light1", blue)
    effect.add_light_color("light2", red)
```

This approach yields the correct effect, but it is significantly less readable that the first approach. As a compromise,
SpecialEffects permits running sections in parallel with the `parallel` argument.

If `parallel` is set to `True` on a section, the sections and effects nested underneath it will be run in parallel.

Here is how the red-to-blue, blue-to-red effect looks with a parallel section:

```python
with effect.section(parallel=True):
    with effect.section("red_to_blue"):
        effect.add_light_color("light1", red)
        effect.add_delay(1)
        effect.add_light_color("light1", blue)

    with effect.section("blue_to_red"):
        effect.add_light_color("light2", blue)
        effect.add_delay(1)
        effect.add_light_color("light2", red)
```

The outer section has `parallel` set to `True`, so
its inner sections, `red_to_blue` and `blue_to_red`, run in parallel. The two lights make
their respective color changes simultaneously, and the desired effect is achieved.

However, `parallel` is *not* set to `True` on the two inner sections, meaning that
the `.add_delay()` call within each inner section is still respected.
Each light still pauses for one second before changing colors.

If the inner sections had `parallel` set to `True`, the two color changes and the delay would all run in a parallel,
ruining the one-color-then-the-other effect.

## Using Other Audio Players

SpecialEffects provides a built-in, cross-platform, asynchronous audio player through the
playsound3 library.

You can plug in an audio player of your choice using the `player` argument on the `.add_sound()` method.
The `player` argument must receive an instance of a class with a `.play_sound(path_to_audio_file)` method.
The `.play_sound(path_to_audio_file)` method use threading to play each new sound in a separate thread.

Here is a toy example:

```python
from specialeffects import SpecialEffect
from threading import Thread


class CustomAudioPlayer:

    def play_sound(self, file_path):
        Thread(target=self._play, args=(file_path,), daemon=True).start()

    def _play(self, file_path):
        pass  # Insert your custom code for playing a sound


custom_player = CustomAudioPlayer()

effect = (
    SpecialEffect()
    .add_sound("path/to/sound.mp3", player=custom_player)
)
```

## Configuring Other Smart Light Brands

SpecialEffects has built-in support for Kasa brand smart lights, although
you can also use your own brand of lights with minimal configuration.
We'll walk through an example
for configuring Kasa lights, which you can then adapt for your own light brand.

### Step 1: Find the Python API for your lights

Smart device brands typically have a library for manipulating their devices using Python.
Usually, it's an unofficial library maintained by the open source community.
For Kasa, this is the [python-kasa](https://github.com/python-kasa/python-kasa) library.

If your brand of smart lights doesn't have a Python API, you'll either need to make one yourself or
switch smart light brands.
Making one yourself can be tricky, and is entirely too far outside the scope of this tutorial.
If you find yourself without a Python API for your smart lights, you'll likely want to switch brands.

### Step 2: Use the Python API for your lights

You'll need to learn enough about your light's Python API to be able to do four things:

* create a light object that represents your smart light
* turn on the smart light
* turn off the smart light
* change the smart light's color using hue, saturation, and value (HSV)

For [python-kasa](https://github.com/python-kasa/python-kasa), here's what that looks like:

```python
from kasa import SmartBulb

# create a light object, in this case using the light's IP address
bulb = SmartBulb("10.0.0.1")

# turn on
bulb.turn_on()

# turn off
bulb.turn_off()

# change color using HSV
bulb.set_hsv(0, 0, 0)
```

### Step 3: Build a Wrapper Class

You now need to implement a class that wraps your brand of light's Python API.
This class needs to implement four methods: `__init__`, `turn_on`, `turn_off`, and `set_color`.

`__init__` can take whatever arguments are necessary to create smart light object in your light brand's
Python API.
The [python-kasa](https://github.com/python-kasa/python-kasa) API uses the light's IP address, which is
typical.

`turn_on` should not take any arguments.

`turn_off` should not take any arguments.

`set_color` should take three arguments: **hue** (integer between 0 and 255), **saturation** (integer between 0 and
100), and **value** (integer between 0 and 100)

All of these methods should be asynchronous and use Python's `ascynio` library.
If you're not familiar with `asyncio`, don't worry.
In most cases, all you'll need to do is put an `async` in front of each method's `def` put an `await` before
the lines of code that actually manipulate the light. SpecialEffects will take care of the rest.

Here's what this looks like for the Kasa bulb:

```python
from kasa import SmartBulb


class KasaLight:
    def __init__(self, host):
        self.light = SmartBulb(host)

    async def turn_on(self):
        await self.light.turn_on()

    async def turn_off(self):
        await self.light.turn_off()

    async def set_color(self, hue, saturation, value):
        await self.light.set_hsv(hue, saturation, value)

```

And you're done. You can now plug in your smart light class into the SpecialEffects API like so:

```python
from specialeffects import SpecialEffect

effect = (
    SpecialEffect()
    .add_light("light1", KasaLight("10.0.0.1"))
    .add_light("light2", KasaLight("10.0.0.2"))
)
```

# Documentation

## Sections and Light Groups

```python
with effect.section(name=None, parallel=None, repeat=1):
# Groups effects into a section
#
# name, string: used to identify and reuse sections
#
# parallel, None or boolean: used to create a parallel section
#   If True, the section is parallel
#   If False, the section is not parallel
#   If None, it is assumed that this section is reusing a previously defined named section
#       This section will use the previous definition's value for parallel
#       If the previous definition also set parallel to None, then parallel defaults to False
#
# repeat, integer or None: how many times a section should repeat
#   If an integer, the section repeats an integer number of times
#   If None, the section repeats infinitely
```

```python
.add_light_group(name, *light_names)
# Groups lights, allowing them to be controlled as one unit using their group name
#
# name, string: the name of the light group
#
# *light_names, strings: light names, passed in as non-keyword arguments
```

## Light Effects

```python
.add_light_on(name)
# Turns a light on
#
# name, string: light name

.add_light_off(name)
# Turns a light off
#
# name, string: light name

.add_light_color(name, color)
# Sets a light to a color
#
# name, string: light name
#
# color, 3-tuple of integers: either RGB or HSV colors, depending on the smart light brand

.add_light_color_transition(name, start_color, end_color, duration, easing_type="linear")
# Transitions a light from start_color to end_color over a duration using a type of easing
#
# name, string: light name
#
# start_color, (int, int, int): either RGB or HSV colors, depending on the smart light brand
#
# end_color, (int, int, int): either RGB or HSV colors, depending on the smart light brand
#
# duration, integer: seconds
#
# easing_type, string: one of the following
#   "linear"
#   "quadratic_in", "quadratic_out", "quadratic_in_out"
#   "cubic_in", "cubic_out", "cubic_in_out"
#   "sine_in", "sine_out", "sine_in_out"
```

## Sound Effects

```python
.add_sound(sound_file, player=None)
# Plays a sound file
#
# sound_file, string: a full path to a sound file
#
# player, object: an object with a .play_sound(sound_file) method
#   if None, the playsound3 module will be used
```

#### Delay

```python
.add_delay(seconds)
# Delays for a number of seconds
#
# seconds, integer: a number of seconds
```

## Custom Effects

SpecialEffects can schedule a user-defined synchronous function and run it asynchronously.

```python
.add_custom(func, *args, **kwargs)
# Calls a a user-defined function
# 
# func, callable: a callable (usually: a function or method)
#
# *args: non-keyword arguments to be passed to func
#
# *kwargs: keyword arguments to be passed to func
#
# func will be called like so:
#   func(*args, **kwargs)

```

# License, Contributions, Etc.

SpecialEffects is released under the [Creative Commons CC0](https://creativecommons.org/public-domain/cc0/) license,
which means that it is placed, as completely as possible, in the public domain.

Contributions are welcome, encouraged, and whatnot.
But keep in mind: the author considers himself less of a "maintainer"
and more of a "dude who kicked his personal library out onto the cold, dark, open-source streets."
Pull requests would make him smile, but he'll get to when he gets to it, you know?
