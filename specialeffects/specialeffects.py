import asyncio
import itertools
from contextlib import contextmanager
from enum import Enum
from specialeffects import easing
from .sounds.default import DefaultPlayer


class LightAction(Enum):
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    SET_COLOR = "set_color"


class Effect:
    def __init__(self, repeat=1):
        self.repeat = repeat

    async def run(self):
        raise NotImplementedError


class SoundEffect(Effect):
    def __init__(
        self,
        sound_file,
        player,
        repeat=1,
    ):
        super().__init__(repeat)
        self.sound_file = sound_file
        self.player = player

    async def run(self):
        for _ in range(self.repeat) if self.repeat is not None else itertools.count():
            await self.player.play_sound(self.sound_file)


class LightEffect(Effect):
    def __init__(self, effect, repeat=1):
        super().__init__(repeat)
        self.effect = effect

    async def run(self):
        for _ in range(self.repeat) if self.repeat is not None else itertools.count():
            await self.effect()


class CustomEffect(Effect):
    def __init__(self, func, *args, **kwargs):
        super().__init__(repeat=1)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    async def run(self):
        await self._run_custom_effect()

    async def _run_custom_effect(self):
        await asyncio.to_thread(self._execute_func)

    def _execute_func(self):
        self.func(*self.args, **self.kwargs)


class Section(Effect):
    def __init__(self, effects, parallel=False, repeat=1, name=None):
        super().__init__(repeat)
        self.effects = effects
        self.parallel = parallel
        self.name = name

    async def run(
        self,
    ):
        repeat_count = itertools.count() if self.repeat is None else range(self.repeat)
        for _ in repeat_count:
            if self.parallel:
                await asyncio.gather(
                    *[self._run_effect(effect) for effect in self.effects]
                )
            else:
                for effect in self.effects:
                    await self._run_effect(effect)

    async def _run_effect(self, effect):
        if isinstance(effect, Section) and effect.repeat is None:
            task = asyncio.create_task(effect.run())
            await asyncio.sleep(0)
            return task
        else:
            return await effect.run()


class SpecialEffect:
    def __init__(self):
        self.lights = {}
        self.light_groups = {}
        self.effects = []
        self.named_effects = {}
        self._current_section = None

    @contextmanager
    def section(self, name=None, parallel=None, repeat=1):
        if name and name in self.named_effects:
            new_section = Section(
                self.named_effects[name].effects,
                parallel if parallel is not None else self.named_effects[name].parallel,
                repeat,
                name,
            )
        else:
            new_section = Section(
                [], parallel if parallel is not None else False, repeat, name
            )
            if name:
                self.named_effects[name] = new_section

        previous_section = self._current_section
        self._current_section = new_section
        yield self
        self._current_section = previous_section

        if previous_section:
            if new_section not in previous_section.effects:
                previous_section.effects.append(new_section)
        elif new_section not in self.effects:
            self.effects.append(new_section)

    def add_light(self, name, light):
        self.lights[name] = light
        return self

    def add_light_group(self, name, *light_names):
        self.light_groups[name] = [
            self.lights[ln] for ln in light_names if ln in self.lights
        ]
        return self

    def add_light_on(self, name):
        return self._create_light_effect(
            name,
            LightAction.TURN_ON,
        )

    def add_light_off(self, name):
        return self._create_light_effect(
            name,
            LightAction.TURN_OFF,
        )

    def add_light_color(self, name, color):
        async def effect():
            for light in self._get_targets(name):
                await light.set_color(*color)

        return self._add_effect(LightEffect(effect))

    def add_light_color_transition(
        self, name, start_color, end_color, duration, easing_type="linear"
    ):
        async def effect():
            targets = self._get_targets(name)
            async for color in easing.interpolate_color_over_time(
                start_color, end_color, duration, easing_type
            ):
                await asyncio.gather(*[light.set_color(*color) for light in targets])

        return self._add_effect(LightEffect(effect))

    def add_sound(self, sound_file, player=None):
        player = DefaultPlayer() if player is None else player
        return self._add_effect(SoundEffect(sound_file, player=player))

    def add_delay(self, seconds):
        return self._add_effect(LightEffect(lambda: asyncio.sleep(seconds)))

    def add_custom(self, func, *args, **kwargs):
        effect = CustomEffect(func, *args, **kwargs)
        return self._add_effect(effect)

    def play(self):
        asyncio.run(self._play_async())

    async def _play_async(self):
        tasks = []
        for effect in self.effects:
            result = await effect.run()
            if isinstance(result, asyncio.Task):
                tasks.append(result)

        if tasks:
            await asyncio.gather(*tasks)

    def _add_effect(self, effect):
        if self._current_section:
            self._current_section.effects.append(effect)
        else:
            self.effects.append(effect)
        return self

    def _create_light_effect(self, name, action):
        async def effect():
            for light in self._get_targets(name):
                await getattr(light, action.value)()

        return self._add_effect(LightEffect(effect))

    def _get_targets(self, name):
        targets = self.lights.get(name) or self.light_groups.get(name)
        if targets is None:
            raise ValueError(f"Light or group '{name}' not found.")
        return targets if isinstance(targets, list) else [targets]
