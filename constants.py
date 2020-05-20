import pygame.freetype

class BarFactory:
    @staticmethod
    def create_selectbar():
        bar = []
        for i in range(0, 30):
            bar.append((16+i*2, 16+i*2, 16+i*2))
        for i in range(0, 30):
            bar.append((76-i*2, 76-i*2, 76-i*2))
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
            bar.append((250-i*2, 200-i*2, 140-i*2))
        return bar

MPDIP = "localhost"
MUSICPATH = "/home/fritz/music/"
COVERPATH = "/home/fritz/test/"

pygame.freetype.init()
FONT = pygame.freetype.Font(pygame.font.match_font('Hiragino Kaku Gothic Pro'), 42)
FONT.origin = True

IMAGESIZE = 330
WHITE = (255, 255, 255)
BLACK = (32, 32, 32)
LIGHTTEXT = (250, 200, 140)
GRAY = (50, 50, 50)
LEFT = 16
TOP = 30
RIGHT = 985
SPACER = 35
LINEPOS = 40

SELECTBAR = BarFactory.create_selectbar()
PBAR = BarFactory.create_pbar()
PBARACTIVE = BarFactory.create_pbaractive()
