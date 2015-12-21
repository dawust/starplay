#!/usr/bin/env python3
import time
import pygame
import pygame.freetype
from mpd import MPDClient
import mutagen
from mutagen import File
import io

class Entry:
    def __init__(self, name, filename=None):
        self.name = name
        self.filename = filename

class Screen:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHTTEXT = (250, 220, 160)
    GRAY = (50, 50, 50)
    LEFT = 60
    TOP = 30
    RIGHT = 980
    IMAGESIZE = 330
    SPACER = 35
    LINEPOS = 40

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
        self.surface.fill(Screen.BLACK)
        self.font.render_to(self.surface, (Screen.LEFT, Screen.TOP+16), title, Screen.WHITE, Screen.BLACK, pygame.freetype.STYLE_NORMAL, 0, 24)
        pygame.draw.line(self.surface, Screen.GRAY, (Screen.LEFT, Screen.TOP + Screen.LINEPOS), (Screen.RIGHT, Screen.TOP + Screen.LINEPOS))

class Playscreen(Screen):
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.freetype.Font(pygame.font.match_font('Hiragino Sans GB'), 42)
        self.font.origin = True
        self.first = False
        self.barcolor = []
        self.barcolore = [] 
        for i in range(0, 8):
            self.barcolore.append((140-i*10, 140-i*10, 140 - i*10))
        for i in range(0, 8):
            self.barcolore.append((i*10, i*10, i*10))
        for i in range(0, 16):
            self.barcolor.append((250-i*2, 220-i*2, 160-i*2))

    def changedsong(self, song):
        self.first = False
        self.currentsong = song

    def changedstatus(self, status):
        self.currentstatus = status

    def seteventfinished(self, event):
        self.eventfinished = event
    
    def setimage(self, image):
        try:
            self.image = scale(image, Screen.IMAGESIZE)
        except:
            pass

    def drawcover(self):
        try:
            self.surface.blit(self.image, (Screen.LEFT, Screen.TOP + Screen.LINEPOS + Screen.SPACER))
        except:
            pass

    def drawtextsplit(self, text, pos, fg, bg):
        maxwidth = Screen.RIGHT - pos[0]
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
        maxwidth = Screen.RIGHT - pos[0]
        textlen = len(text) 
        for maxlen in range(textlen, 0, -1):
            rect = self.font.get_rect(text[:maxlen])
            if rect.width < maxwidth: break
        if maxlen == textlen:
            self.font.render_to(self.surface, pos, text[:maxlen], fg, bg)
        else:
            self.font.render_to(self.surface, pos, text[:maxlen] + "...", fg, bg)


    def render(self):
        try:
            if self.first == False:
                self.drawtitle("Now Playing")
                self.drawcover()
                pos = (Screen.LEFT + Screen.IMAGESIZE + Screen.SPACER, Screen.TOP + Screen.LINEPOS + Screen.SPACER + 32)
                pos = self.drawtextsplit(self.currentsong['title'], pos, Screen.LIGHTTEXT, Screen.BLACK)
                pos = self.drawtextsplit(self.currentsong['artist'], pos, Screen.WHITE, Screen.BLACK)
                self.drawtextsplit(self.currentsong['album'], pos, Screen.WHITE, Screen.BLACK)
                self.first=True

            playtime = self.currentstatus['time'].split(':')
            timenow = int(playtime[0])
            timetotal = int(playtime[-1])
            timenowmin, timenowsec = divmod(timenow, 60)
            timetotalmin, timetotalsec = divmod(timetotal, 60)
         
            barwidth = Screen.RIGHT - Screen.LEFT
            barmid = Screen.LEFT + int(barwidth * (float(timenow)/timetotal))
            barpos = Screen.TOP + Screen.LINEPOS + Screen.SPACER + Screen.IMAGESIZE + Screen.SPACER
            for i in range(0, 16):
                pygame.draw.line(self.surface, self.barcolor[i], (Screen.LEFT, barpos+i), (barmid, barpos+i))
                pygame.draw.line(self.surface, self.barcolore[i], (barmid, barpos+i), (Screen.RIGHT, barpos+i))
            self.surface.fill(Screen.BLACK, (Screen.LEFT, barpos + Screen.SPACER - 5, Screen.RIGHT, barpos + Screen.SPACER + 60))
            self.font.render_to(self.surface, (Screen.LEFT, barpos + Screen.SPACER + 32), "%02d:%02d" % (timenowmin, timenowsec), Screen.WHITE, Screen.BLACK)
            self.font.render_to(self.surface, (Screen.RIGHT - 120, barpos + Screen.SPACER + 32), "%02d:%02d" % (timetotalmin, timetotalsec), Screen.WHITE, Screen.BLACK)
        except:
            print("Playback Exception")
            self.eventfinished()

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
            if self.sel >= self.end :
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
        y = Screen.TOP + Screen.LINEPOS + Screen.SPACER
        i = 0
        for entry in self.entries[self.start:self.end]:
            if (self.entries.index(entry) == self.sel):                
                for j in range(0, 60):
                    pygame.draw.line(self.surface, self.barcolor[j], (Screen.LEFT, (y-15+(i * 60))+j), (Screen.RIGHT, (y-15 + (i*60))+ j))
                self.font.render_to(self.surface, (Screen.LEFT+10, y+32 + (i * 60)), entry.name, Screen.LIGHTTEXT)
            else:
                self.font.render_to(self.surface, (Screen.LEFT+10, y+32 + (i * 60)), entry.name, Screen.WHITE, Screen.BLACK)
            i += 1

def getcoverart(file):
    audio = File(file)
    try:
        return audio.pictures[0].data
    except:
        pass
    try:
        return audio['APIC:'].data
    except:
        pass
    try:
        return audio['covr'].data
    except: 
        return None

def scale(image, size):
    width = image.get_width()
    height = image.get_height()
    scale = max(width, height)
    newsize = (int((width / scale) * size), int((height / scale) * size))
    return pygame.transform.smoothscale(image, newsize)

class Starplay:

    def mpdinit(self):
        self.mpd = MPDClient()
        self.mpd.connect("10.1.1.3", 6600)
    
    def pygameinit(self):
        print(pygame.freetype.Font.origin)
        pygame.init()
        pygame.display.set_caption("splay")
        self.surface = pygame.display.set_mode((1024,576))

    def createartistmenu(self):
        self.artistmenu = Menu(self.surface, "Artists")
        artists = self.mpd.list("ARTIST")
        for artist in sorted(artists, key=lambda s: s.lower()):
            self.artistmenu.addentry(Entry(artist))
        self.artistmenu.setevententer(self.selectartist)
        self.artistmenu.seteventbackspace(lambda: None)

    def createalbummenu(self):
        self.albummenu = Menu(self.surface)
        self.albummenu.setevententer(self.selectalbum)
        self.albummenu.seteventbackspace(lambda: self.setactivemenu(self.artistmenu))

    def createtrackmenu(self):
        self.trackmenu = Menu(self.surface)
        self.trackmenu.setevententer(self.selecttrack)
        self.trackmenu.seteventbackspace(lambda: self.setactivemenu(self.albummenu))

    def createplayback(self):
        self.playback = Playscreen(self.surface)
        self.playback.setevententer(self.mpd.pause)
        self.playback.seteventbackspace(lambda: self.setactivemenu(self.trackmenu))
        self.playback.seteventfinished(self.selectalbum)

    def __init__(self):
        self.currentstatus = None
        self.currentsong = None
        
        self.mpdinit()
        self.pygameinit()
        self.createartistmenu()
        self.createalbummenu()
        self.createtrackmenu()
        self.createplayback()  

        self.setactivemenu(self.artistmenu)
       
        running = True
        changed = True
        while running:
            for event in pygame.event.get():
                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        return
                    elif (event.key == pygame.K_DOWN):
                        self.activemenu.keydown()
                    elif (event.key == pygame.K_UP):
                        self.activemenu.keyup()
                    elif (event.key == pygame.K_LEFT):                        
                        self.mpd.previous()
                    elif (event.key == pygame.K_RIGHT):
                        self.mpd.next()
                    elif (event.key == pygame.K_RETURN):
                        self.activemenu.keyenter()
                    elif (event.key == pygame.K_BACKSPACE):
                        self.activemenu.keybackspace()
                changed = True
            changed |= self.updatempd()
            if changed == True:
                self.activemenu.render()
                pygame.display.update()
            time.sleep(0.05)
            changed = False

    def updatempd(self):
        changed = False
        newstatus = self.mpd.status()
        newsong = self.mpd.currentsong()
        if (newstatus != self.currentstatus):
            self.playback.changedstatus(newstatus)
            if ((self.currentstatus == None) or (not 'time' in newstatus) or (not 'time' in self.currentstatus) or newstatus['time'] != self.currentstatus['time']):
                changed = True
        if (newsong != self.currentsong):
            self.playback.changedsong(newsong)
            changed = True
        self.currentsong = newsong
        self.currentstatus = newstatus
        return changed
    def setactivemenu(self, menu):
        self.playback.changedsong(self.currentsong)
        self.activemenu = menu

    def selectartist(self):
        artist = self.artistmenu.getentry().name
        if self.albummenu.getname() != artist:
            albums = self.mpd.list("ALBUM", "ARTIST", artist)
            self.albummenu.clear()
            self.albummenu.setname(artist)
            for album in sorted(albums, key=lambda s: s.lower()):
                self.albummenu.addentry(Entry(album))

        self.setactivemenu(self.albummenu)

    def selectalbum(self):
        artist = self.artistmenu.getentry().name
        album = self.albummenu.getentry().name
        tracks = self.mpd.find("ARTIST", artist, "ALBUM", album)
        self.trackmenu.clear()
        self.trackmenu.setname(album)
        for track in tracks:
            self.trackmenu.addentry(Entry(track['title'], track['file']))
            if 'file' in self.currentsong and self.currentsong['file'] == track['file']:
                self.trackmenu.setpos(int(self.currentstatus['song']))
        self.setactivemenu(self.trackmenu)

    def selecttrack(self):
        self.updatempd()
        if ((not 'file' in self.currentsong) or self.currentsong['file'] != self.trackmenu.getentry().filename):
            self.mpd.clear()
            songs = self.mpd.find("ARTIST", self.artistmenu.getentry().name , "ALBUM", self.albummenu.getentry().name)
            coverfile = None
            for song in songs:
                if coverfile == None: coverfile = song['file']
                self.mpd.add(song['file'])
            self.mpd.play(self.trackmenu.getpos())
            try:
                self.playback.setimage(pygame.image.load(io.BytesIO(getcoverart("/home/fritz/music/" + coverfile))).convert())
            except:
                pass
        self.mpd.pause(0)
        self.setactivemenu(self.playback)

if __name__ == "__main__":
    splay = Starplay()
