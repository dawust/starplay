import time
import pygame
from mpd import MPDClient
import menus
from constants import *

class Entry:
    def __init__(self, name, filename=None, next=None):
        self.name = name
        self.filename = filename
        self.next = next

class Starplay:

    def mpdinit(self):
        running = False
        while not running:
            try:
                self.mpd = MPDClient()
                self.mpd.connect(MPDIP, 6600)
                running = True
            except:
                time.sleep(0.5)
                pass
    
    def pygameinit(self):
        pygame.init()
        pygame.display.set_caption("splay")
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        size = (1024,576)
        self.surface = pygame.display.set_mode(size)

    def addartists(self, selartist):
        artists = self.mpd.list("ARTIST")
        for artist in sorted(artists, key=lambda s: s.lower()):
            self.artistmenu.addentry(Entry(artist))
            if selartist == artist: self.artistmenu.setpos()

    def createartistmenu(self):
        self.artistmenu = menus.Menu(self.surface, "Artists")
        self.artistmenu.setevententer(lambda: self.selectartist(self.artistmenu.getentry()))
        self.artistmenu.seteventbackspace(lambda: None)

    def createalbummenu(self):
        self.albummenu = menus.Menu(self.surface)
        self.albummenu.setevententer(lambda: self.selectalbum(self.artistmenu.getentry(), self.albummenu.getentry()))
        self.albummenu.seteventbackspace(lambda: self.setactivemenu(self.artistmenu))

    def createtrackmenu(self):
        self.trackmenu = menus.Menu(self.surface)
        self.trackmenu.setevententer(self.selecttrack)
        self.trackmenu.seteventbackspace(lambda: self.selectartist(self.currentartist))

    def createplayback(self):
        self.playback = menus.Playscreen(self.surface)
        self.playback.setevententer(self.mpd.pause)
        self.playback.seteventbackspace(lambda: self.selectalbum(self.currentartist, self.currentalbum))

    def rendermenu(self):
        self.activemenu.render()
        pygame.display.update()

    def updatempd(self, update=False):
        changed = False
        newstatus = self.mpd.status()
        newsong = self.mpd.currentsong()

        if (newstatus != self.currentstatus or update):
            self.activemenu.changedstatus(newstatus)
            changed = (newstatus.get('time') != self.currentstatus.get('time'))
        if (newsong != self.currentsong or update):
            self.activemenu.changedsong(newsong)
            changed = True
        
        self.currentsong = newsong
        self.currentstatus = newstatus

        if not newsong and int(self.currentstatus.get('playlistlength')) > 0: 
            self.playbackfinished()

        return changed

    def playbackfinished(self):
        print("Playback finished")
        if (self.playbackmode == 0):
            if self.activemenu == self.playback:
               self.selectalbum(self.currentartist, self.currentalbum)
        elif (self.playbackmode == 1):
            self.mpd.play(0)
        elif (self.playbackmode == 2):
            if self.currentalbum is not None and self.currentartist is not None:
                self.mpdaddalbum(self.currentartist, self.currentalbum.next)
                self.mpd.play(0)
        self.updatempd()

    def setactivemenu(self, menu):
        self.activemenu = menu
        self.updatempd(update=True)
        self.rendermenu()

    def selectartist(self, artist, update=True):
        ret = None
        albums = self.mpd.list("ALBUM", "ARTIST", artist.name)
        self.albummenu.clear()
        self.albummenu.setname(artist.name)
        prev = None
        first = None
        for album in sorted(albums, key=lambda s: s.lower()):
            entry = Entry(album)
            if prev: 
                prev.next = entry
            else:
                first = entry
            self.albummenu.addentry(entry)
            prev = entry
            if self.currentalbum and self.currentalbum.name == album:
                self.albummenu.setpos()
                ret = entry
        if prev is not None: prev.next = first

        if update: self.setactivemenu(self.albummenu)
        return ret

    def selectalbum(self, artist, album):
        tracks = self.mpd.find("ARTIST", artist.name, "ALBUM", album.name)
        self.trackmenu.clear()
        self.trackmenu.setname(album.name)
        for track in tracks:
            entry = Entry(track.get('title'), track.get('file'))
            self.trackmenu.addentry(entry)
            if self.currentsong.get('file') == track.get('file'):
                self.trackmenu.setpos()

        self.setactivemenu(self.trackmenu)

    def selecttrack(self):
        if (self.currentsong.get('file') != self.trackmenu.getentry().filename):
            self.mpdaddalbum(self.artistmenu.getentry(), self.albummenu.getentry())
            self.mpd.play(self.trackmenu.getpos())
        self.mpd.pause(0)
        self.setactivemenu(self.playback)

    def mpdaddalbum(self, artist, album):
        self.currentartist = artist
        self.currentalbum = album
        self.mpd.clear()
        songs = self.mpd.find("ARTIST", artist.name, "ALBUM", album.name)
        for song in songs:
            self.mpd.add(song.get('file'))

    def main(self):
            self.playbackmode = 2
            self.currentstatus = {}
            self.currentsong = {}
            self.pygameinit()
            
            self.mpdinit()
            self.createartistmenu()
            self.createalbummenu()
            self.createtrackmenu()
            self.createplayback()  
            self.activemenu = self.artistmenu
            self.updatempd()

            self.currentartist = Entry(self.currentsong.get('artist'))
            self.currentalbum = Entry(self.currentsong.get('album'))
            self.addartists(self.currentartist.name)
            self.currentalbum = self.selectartist(self.currentartist, False)
            
            state = self.currentstatus.get('state')
            if state == 'stop': self.mpd.play(0)
            if self.currentalbum is not None and self.currentartist is not None and (state == 'play' or state == 'pause'):
                self.mpd.pause(0)
                self.setactivemenu(self.playback)
            else:
                self.setactivemenu(self.artistmenu)
           
            running = True
            timelast = time.time()
            while running:
                changed = self.updatempd()

                for event in pygame.event.get():
                    if (event.type == pygame.QUIT):
                        return
                    elif (event.type == pygame.KEYDOWN):
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
                        timelast = time.time()     

                if time.time() - timelast > 15 and self.currentstatus.get('state') == 'play' and self.activemenu != self.playback:
                    self.setactivemenu(self.playback)
                    changed = True

                if changed: self.rendermenu()
                time.sleep(0.05)
