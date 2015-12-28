import pygame.freetype
class BarFactory:
    @staticmethod
    def create_selectbar():
        bar = []
        for i in range(0, 30):
            bar.append((i*2, i*2, i*2))
        for i in range(0, 30):
            bar.append((60-i*2, 60-i*2, 60-i*2))
        return bar

    @staticmethod
    def create_pbar():
        bar = []
        for i in range(0, 8):
            bar.append((140-i*10, 140-i*10, 140 - i*10))
        for i in range(0, 8):
            bar.append((i*10, i*10, i*10))
        return bar

    @staticmethod
    def create_pbaractive():
        bar = []
        for i in range(0, 16):
            bar.append((250-i*2, 220-i*2, 160-i*2))
        return bar

MPDIP = "10.1.1.3"
MUSICPATH = "/home/fritz/music/"
COVERPATH = "/home/fritz/test/"

pygame.freetype.init()
FONT = pygame.freetype.Font(pygame.font.match_font('Hiragino Kaku Gothic Pro'), 42)
FONT.origin = True

IMAGESIZE = 330
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTTEXT = (250, 220, 160)
GRAY = (50, 50, 50)
LEFT = 60
TOP = 30
RIGHT = 980
SPACER = 35
LINEPOS = 40

SELECTBAR = BarFactory.create_selectbar()
PBAR = BarFactory.create_pbar()
PBARACTIVE = BarFactory.create_pbaractive()

