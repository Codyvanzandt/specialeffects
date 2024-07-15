from playsound3 import playsound


class DefaultPlayer:

    def play_sound(self, path):
        playsound(path, block=False)
