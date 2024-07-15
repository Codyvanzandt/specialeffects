from kasa import SmartBulb


class KasaLight:
    def __init__(self, host):
        self.light = SmartBulb(host)

    async def turn_on(self):
        await self.light.turn_on()

    async def turn_off(self):
        await self.light.turn_off()

    async def set_color(self, hue, saturation, value):
        await self.light.update()
        await self.light.set_hsv(hue, saturation, value)
