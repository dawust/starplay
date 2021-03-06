import pygame.transform
import pygame.image
import io
import os.path
import threading
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from constants import *

def getembeddedcover(file):
    try:
        filename, fileext = os.path.splitext(file)
        filepath, tail = os.path.split(file)
        if fileext.lower() == '.flac':
            flac = FLAC(file)
            data = flac.pictures[0].data
        elif fileext.lower() == '.mp3':
            mp3 = MP3(file)
            apic = mp3.tags.get('APIC:', None)
            if apic is None:
                for key in mp3.tags:
                    if key.startswith("APIC:"):
                        apic = mp3.tags.get(key)
                        break
            data = apic.data
        
        image = scale(pygame.image.load(io.BytesIO(data)), IMAGESIZE)
        os.makedirs(COVERPATH + filepath, exist_ok=True)
        pygame.image.save(image, COVERPATH + filepath + "/cover.png")
        return image
    except Exception as e:
        pass

def scale(image, size):
    width = image.get_width()
    height = image.get_height()
    scale = max(width, height)
    newsize = (int((width / scale) * size), int((height / scale) * size))
    return pygame.transform.smoothscale(image, newsize)

def getcover(file, callback):
    filename = MUSICPATH + file
    filepath, tail = os.path.split(filename)
    covername = filepath + "/cover.png"
    if os.path.exists(covername):
        image = pygame.image.load(covername).convert()
        if image is not None: callback(image)
    elif not os.path.exists(COVERPATH + covername):
        threading.Thread(target=getcoverhelper, args=[filename, callback]).start()
    else:
        image = pygame.image.load(COVERPATH + covername).convert()
        if image is not None: callback(image)

def getcoverhelper(filename, callback):
    image = getembeddedcover(filename)
    if image is not None: callback(image)
