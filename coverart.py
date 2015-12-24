import pygame.transform
import pygame.image
import io
import os.path
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from constants import *

def getcoverart(file):
    try:
        filename, fileext = os.path.splitext(file)
        filepath, tail = os.path.split(file)
        if fileext.lower() == '.flac':
            flac = FLAC(file)
            data = flac.pictures[0].data
        elif fileext.lower() == '.mp3':
            mp3 = MP3(file)
            data = mp3.tags['APIC:'].data
        
        image = scale(pygame.image.load(io.BytesIO(data)), IMAGESIZE)
        pygame.image.save(image, filepath + "/cover.png")
    except:
        pass

def scale(image, size):
    width = image.get_width()
    height = image.get_height()
    scale = max(width, height)
    newsize = (int((width / scale) * size), int((height / scale) * size))
    return pygame.transform.smoothscale(image, newsize)


