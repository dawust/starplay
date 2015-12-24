import pygame.draw
import pygame.image
import pygame.freetype
import threading
import os.path
import coverart
from constants import *

class Entry:
    def __init__(self, name, filename=None):
        self.name = name
        self.filename = filename

class Screen:
    def keydown(self): pass
    def keyup(self): pass
        
    def setevententer(self, event):
        self.evententer = event

    def seteventbackspace(self, event):
        self.eventbackspace = event

    def keyenter(self):
        self.evententer()

    def keybackspace(self):
        self.eventbackspace()

    def changedstatus(self, status): pass

    def changedsong(self, song): pass

    def drawtitle(self, title):
        self.surface.fill(BLACK)
        self.font.render_to(self.surface, (LEFT, TOP+16), title, WHITE, BLACK, pygame.freetype.STYLE_NORMAL, 0, 24)
        pygame.draw.line(self.surface, GRAY, (LEFT, TOP + LINEPOS), (RIGHT, TOP + LINEPOS))

    def drawtextsplit(self, text, pos, fg, bg):
        maxwidth = RIGHT - pos[0]
        splittext = text.split(' ')
        splittextlen = len(splittext)
        if splittextlen == 1:
            self.drawtextshort(text, pos, fg, bg)
        else:
            first = ""
            second = ""
            maxlen = 0
            for maxlen in range(splittextlen, 0, -1):
                first = ' '.join(splittext[:maxlen])
                second = ' '.join(splittext[maxlen:])
                rect = self.font.get_rect(first)
                if rect.width < maxwidth: break

            self.font.render_to(self.surface, pos, first, fg, bg)
            
            if maxlen != splittextlen:
               pos = (pos[0], pos[1] + 60)
               self.drawtextshort(second, pos, fg, bg)

        pos = (pos[0], pos[1] + 60)
        return pos

    def drawtextshort(self, text, pos, fg, bg):
        maxlen = 0
        maxwidth = RIGHT - pos[0]
        textlen = len(text) 
        for maxlen in range(textlen, 0, -1):
            rect = self.font.get_rect(text[:maxlen])
            if rect.width < maxwidth: break
        if maxlen == textlen:
            self.font.render_to(self.surface, pos, text[:maxlen], fg, bg)
        else:
            self.font.render_to(self.surface, pos, text[:maxlen] + "...", fg, bg)

class Playscreen(Screen):
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.freetype.Font(pygame.font.match_font('Hiragino Sans GB'), 42)
        self.font.origin = True
        self.barcolor = []
        self.barcolore = [] 
        self.image = None
        for i in range(0, 8):
            self.barcolore.append((140-i*10, 140-i*10, 140 - i*10))
        for i in range(0, 8):
            self.barcolore.append((i*10, i*10, i*10))
        for i in range(0, 16):
            self.barcolor.append((250-i*2, 220-i*2, 160-i*2))

    def changedsong(self, song):
        self.currentsong = song
        try:
            self.drawtitle("Now Playing")
            self.getcover()

            pos = (LEFT + IMAGESIZE + SPACER, TOP + LINEPOS + SPACER + 32)
            pos = self.drawtextsplit(self.currentsong['title'], pos, LIGHTTEXT, BLACK)
            pos = self.drawtextsplit(self.currentsong['artist'], pos, WHITE, BLACK)
            self.drawtextsplit(self.currentsong['album'], pos, WHITE, BLACK)
        except:
            pass

    def changedstatus(self, status):
        self.currentstatus = status

    def getcover(self):
        filename = "/home/fritz/music/" + self.currentsong['file']
        filepath, tail = os.path.split(filename)
        covername = filepath + "/cover.png"
        if not os.path.exists(covername):
            threading.Thread(target=self.getcoverhelper, args=[filename, covername]).start()
        else:
            self.drawcover(covername)

    def getcoverhelper(self, filename, covername):
        try:
            coverart.getcoverart(filename)
            self.drawcover(covername)
        except:
            pass

    def drawcover(self, covername):
        try:
            self.image = pygame.image.load(covername).convert()
            self.surface.blit(self.image, (LEFT, TOP + LINEPOS + SPACER))
        except:
            pass

    def render(self):
        try:
            playtime = self.currentstatus['time'].split(':')
            timenow = int(playtime[0])
            timetotal = int(playtime[-1])
            timenowmin, timenowsec = divmod(timenow, 60)
            timetotalmin, timetotalsec = divmod(timetotal, 60)
         
            barwidth = RIGHT - LEFT
            barmid = LEFT + int(barwidth * (float(timenow)/timetotal))
            barpos = TOP + LINEPOS + SPACER + IMAGESIZE + SPACER
            for i in range(0, 16):
                pygame.draw.line(self.surface, self.barcolor[i], (LEFT, barpos+i), (barmid, barpos+i))
                pygame.draw.line(self.surface, self.barcolore[i], (barmid, barpos+i), (RIGHT, barpos+i))
            self.surface.fill(BLACK, (LEFT, barpos + SPACER - 5, RIGHT, barpos + SPACER + 60))
            self.font.render_to(self.surface, (LEFT, barpos + SPACER + 32), "%02d:%02d" % (timenowmin, timenowsec), WHITE, BLACK)
            self.font.render_to(self.surface, (RIGHT - 120, barpos + SPACER + 32), "%02d:%02d" % (timetotalmin, timetotalsec), WHITE, BLACK)

        except:
            print("Playback Exception")
            self.eventbackspace()

class Menu(Screen):
    def __init__(self, surface, name=""):
        self.name = name
        self.surface = surface
        self.font = pygame.freetype.Font(pygame.font.match_font('Hiragino Sans GB'), 42)
        self.font.origin = True
        self.barcolor = []
        self.clear()

        for i in range(0, 30):
                self.barcolor.append((i*2, i*2, i*2))
        for i in range(0, 30):
                self.barcolor.append((60-i*2, 60-i*2, 60-i*2))

    def clear(self):
        self.sel = 0
        self.start = 0
        self.end = 7
        self.entries = []
    
    def setname(self, name):
        self.name = name

    def getname(self):
        return self.name

    def keyup(self):
        if self.sel > 0:
            self.sel -= 1
            if self.sel < self.start:
                self.start -= 1
                self.end -= 1

    def keydown(self):
        if self.sel < len(self.entries) - 1:
            self.sel += 1
            if self.sel >= self.end:
                self.start += 1
                self.end += 1

    def getentry(self):
        return self.entries[self.sel]

    def getpos(self):
        return self.sel

    def setpos(self, pos):
        self.sel = pos
        if (pos > self.end):
            self.start += self.sel
            self.end += self.sel

    def addentry(self, entry):
        self.entries.append(entry)

    def render(self):
        self.drawtitle(self.name)
        y = TOP + LINEPOS + SPACER
        i = 0
        for entry in self.entries[self.start:self.end]:
            if (self.entries.index(entry) == self.sel):                
                for j in range(0, 60):
                    pygame.draw.line(self.surface, self.barcolor[j], (LEFT, (y-15+(i * 60))+j), (RIGHT, (y-15 + (i*60))+ j))
                self.font.render_to(self.surface, (LEFT+10, y+32 + (i * 60)), entry.name, LIGHTTEXT)
            else:
                self.font.render_to(self.surface, (LEFT+10, y+32 + (i * 60)), entry.name, WHITE, BLACK)
            i += 1
