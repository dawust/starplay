import pygame.draw
import pygame.image
import coverart
from constants import *

class Screen:
    def keydown(self): pass
    
    def keyup(self): pass

    def keypgdn(self): pass

    def keypgup(self): pass

    def keyenter(self): 
        self.evententer()

    def keybackspace(self):
        self.eventbackspace()
   
    def setevententer(self, event):
        self.evententer = event

    def seteventbackspace(self, event):
        self.eventbackspace = event

    def changedsong(self): pass

    def drawtitle(self, title):
        self.surface.fill(BLACK)
        FONT.render_to(self.surface, (LEFT, TOP+16), title, WHITE, BLACK, pygame.freetype.STYLE_STRONG, 0, 24)
        self.drawicons()
        pygame.draw.line(self.surface, GRAY, (LEFT, TOP + LINEPOS), (RIGHT, TOP + LINEPOS))

    def drawicons(self):
        self.surface.fill(BLACK, (RIGHT-25, TOP - 24, RIGHT, TOP + 24))
        if (self.player.playbackmode == 1):
            FONT.render_to(self.surface, (RIGHT-25, TOP+16), "\u2192", WHITE, BLACK, pygame.freetype.STYLE_STRONG, 0, 24)
        elif (self.player.playbackmode == 2):
            FONT.render_to(self.surface, (RIGHT-25, TOP+16), "\u21c6", WHITE, BLACK, pygame.freetype.STYLE_STRONG, 0, 24)

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
                rect = FONT.get_rect(first)
                if rect.width < maxwidth: break

            FONT.render_to(self.surface, pos, first, fg, bg)
            
            if maxlen != splittextlen:
               pos = (pos[0], pos[1] + 60)
               self.drawtextshort(second, pos, fg, bg)

        pos = (pos[0], pos[1] + 60)
        return pos

    def drawtextshort(self, text, pos, fg, bg, offset=0):
        maxwidth = RIGHT - pos[0] - offset

        rect = FONT.get_rect(text)
        if rect.width < maxwidth: 
            FONT.render_to(self.surface, pos, text, fg, bg)
        else:
            maxlen = 0
            textlen = len(text) 
            for maxlen in range(textlen, 0, -1):
                rect = FONT.get_rect(text[:maxlen] + "...")
                if rect.width < maxwidth: break
            FONT.render_to(self.surface, pos, text[:maxlen] + "...", fg, bg)

class Playscreen(Screen):
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player
    
    def changedsong(self):
        try:
            self.drawtitle("Now Playing (%d/%d)" % (int(self.player.currentsong['pos'])+1, int(self.player.currentstatus['playlistlength'])))

            pos = (LEFT + IMAGESIZE + SPACER, TOP + LINEPOS + SPACER + 32)
            pos = self.drawtextsplit(self.player.currentsong['title'], pos, LIGHTTEXT, BLACK)
            pos = self.drawtextsplit(self.player.currentsong['artist'], pos, WHITE, BLACK)
            self.drawtextsplit(self.player.currentsong['album'], pos, WHITE, BLACK)
            
            coverart.getcover(self.player.currentsong['file'], self.drawcover)
        except:
            pass

    def drawcover(self, image):
        self.surface.blit(image, (LEFT, TOP + LINEPOS + SPACER))
        
        x = image.get_width()
        y = image.get_height()
        image.set_alpha(192)
        self.surface.blit(image, (LEFT, TOP + LINEPOS + SPACER-1), (0,0,x,1) )
        self.surface.blit(image, (LEFT, TOP + LINEPOS + SPACER + y), (0,y-1, x,y) )
        image.set_alpha(128)
        self.surface.blit(image, (LEFT, TOP + LINEPOS + SPACER-2), (0,0,x,1) )
        self.surface.blit(image, (LEFT, TOP + LINEPOS + SPACER + y + 1), (0,y-1, x,y) )
        image.set_alpha(64)
        self.surface.blit(image, (LEFT, TOP + LINEPOS + SPACER-3), (0,0,x,1) )
        self.surface.blit(image, (LEFT, TOP + LINEPOS + SPACER + y + 2), (0,y-1, x,y) )

    def render(self):
        try:
            self.drawicons()
            playtime = self.player.currentstatus['time'].split(':')
            timenow = int(playtime[0])
            timetotal = int(playtime[-1])
            timenowmin, timenowsec = divmod(timenow, 60)
            timetotalmin, timetotalsec = divmod(timetotal, 60)
         
            barwidth = RIGHT - LEFT
            barmid = LEFT + int(barwidth * (float(timenow)/timetotal))
            barpos = TOP + LINEPOS + SPACER + IMAGESIZE + SPACER
            for i in range(0, 16):
                pygame.draw.line(self.surface, PBARACTIVE[i], (LEFT, barpos+i), (barmid, barpos+i))
                pygame.draw.line(self.surface, PBAR[i], (barmid, barpos+i), (RIGHT, barpos+i))
            self.surface.fill(BLACK, (LEFT, barpos + SPACER - 5, RIGHT, barpos + SPACER + 60))
            FONT.render_to(self.surface, (LEFT, barpos + SPACER + 32), "%02d:%02d" % (timenowmin, timenowsec), WHITE, BLACK)
            FONT.render_to(self.surface, (RIGHT - 120, barpos + SPACER + 32), "%02d:%02d" % (timetotalmin, timetotalsec), WHITE, BLACK)

        except Exception as e:
            print("Playback Exception")
            print(self.player.currentstatus)

class Menu(Screen):
    def __init__(self, surface, player, name=""):
        self.surface = surface
        self.player = player
        self.name = name
        self.clear()

    def clear(self):
        self.sel = 0
        self.start = 0
        self.end = 7
        self.entries = []
    
    def setname(self, name):
        self.name = name

    def getname(self):
        return self.name

    def keypgup(self):
        for i in range(6):
            self.keyup()

    def keypgdn(self):
        for i in range(6):
            self.keydown()

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

    def setpos(self):
        self.sel = len(self.entries) - 1
        if (self.sel >= self.end):
            entries = self.end - self.start    
            self.start = self.sel - entries + 1
            self.end = self.sel + 1

    def addentry(self, entry):
        self.entries.append(entry)

    def drawentry(self, text, pos, sel=False):
        if sel:                
            for j in range(0, 60):
                pygame.draw.line(self.surface, SELECTBAR[j], (pos[0], pos[1]-15+j), (RIGHT-32, pos[1]-15+j))
            self.drawtextshort(text, (pos[0]+10, pos[1]+32), LIGHTTEXT, None, 32)
        else:
            self.drawtextshort(text, (pos[0]+10, pos[1]+32), WHITE, BLACK, 32)
        pos = (pos[0], pos[1] + 60)
        return pos

    def drawscrollbar(self):
        HEIGHT = 400 + 15
        x = RIGHT - 16
        y = TOP + LINEPOS + SPACER - 15
        entries = len(self.entries)
        if self.end - self.start >= entries: return
                
        totalheight = HEIGHT / entries
        startheight = self.start * totalheight
        endheight = self.end * totalheight

        for i in range(0, 16):
            pygame.draw.line(self.surface, PBAR[i], (x+i, y), (x+i, y+HEIGHT))
            pygame.draw.line(self.surface, PBARACTIVE[i], (x+i, y+startheight), (x+i, y+endheight))
    
    def render(self):
        self.drawtitle(self.name)
        pos = (LEFT, TOP + LINEPOS + SPACER)
        for entry in self.entries[self.start:self.end]:
           pos = self.drawentry(entry.name, pos, self.entries.index(entry) == self.sel)
        self.drawscrollbar()

