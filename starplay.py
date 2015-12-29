import time
import pygame
from mpd import MPDClient
import menus
from constants import *

class Entry:
    def __init__(self, name, filename=None):
        self.name = name
        self.filename = filename
        self.next = None
        self.prev = None

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

    def createartistmenu(self):
        self.artistmenu = menus.Menu(self.surface, self, "Artists")
        self.artistmenu.setevententer(lambda: self.selectartist(self.artistmenu.getentry()))
        self.artistmenu.seteventbackspace(lambda: None)

    def createalbummenu(self):
        self.albummenu = menus.Menu(self.surface, self)
        self.albummenu.setevententer(lambda: self.selectalbum(self.artistmenu.getentry(), self.albummenu.getentry()))
        self.albummenu.seteventbackspace(lambda: self.setactivemenu(self.artistmenu))

    def createtrackmenu(self):
        self.trackmenu = menus.Menu(self.surface, self)
        self.trackmenu.setevententer(self.selecttrack)
        self.trackmenu.seteventbackspace(lambda: self.setactivemenu(self.albummenu))

    def createplayback(self):
        self.playback = menus.Playscreen(self.surface, self)
        self.playback.setevententer(self.mpd.pause)
        self.playback.seteventbackspace(lambda: self.selectalbum(self.currentartist, self.currentalbum))

    def setactivemenu(self, menu):
        self.activemenu = menu

    def addartists(self):
        self.artistmenu.clear()
        artists = self.mpd.list("ARTIST")
        for artist in sorted(artists, key=lambda s: s.lower()):
            self.artistmenu.addentry(Entry(artist))
            if self.currentartist.name == artist: self.artistmenu.setpos()

    def selectartist(self, artist):
        ret = Entry("XXX")
        albums = self.mpd.list("ALBUM", "ARTIST", artist.name)
        self.albummenu.clear()
        self.albummenu.setname(artist.name)
        prev = None
        first = None
        for album in sorted(albums, key=lambda s: s.lower()):
            entry = Entry(album)
            if prev is not None:
                entry.prev = prev
                prev.next = entry
            else:
                first = entry
            prev = entry 
            self.albummenu.addentry(entry)
            if self.currentalbum.name == album:
                self.albummenu.setpos()
                ret = entry
        if prev is not None: 
            prev.next = first
            first.prev = prev

        self.setactivemenu(self.albummenu)
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
        if self.currentsong.get('file') != self.trackmenu.getentry().filename:
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

    def togglemode(self):
        if self.playbackmode == 0:
            self.playbackmode = 1
        elif self.playbackmode == 1:
            self.playbackmode = 2
        elif self.playbackmode == 2:
            self.playbackmode = 0

    def prevtrackalbum(self):
        if self.playbackmode == 2 and self.currentstatus.get('song') == '0':
            self.mpdaddalbum(self.currentartist, self.currentalbum.prev)
            self.currentstatus = self.mpd.status()
            self.mpd.play(int(self.currentstatus.get('playlistlength', 1)) - 1)
        else:
            self.mpd.previous()

    def nexttrackalbum(self):
        if (int(self.currentstatus.get('song', 0)) == int(self.currentstatus.get('playlistlength', 1)) - 1): 
            self.playbackfinished()
        else:
            self.mpd.next()

    def playbackfinished(self):
        if self.playbackmode == 0: 
            self.mpd.clear()
            if self.activemenu == self.playback: self.selectartist(self.currentartist)
        elif self.playbackmode == 1:
            self.mpd.play(0)
        elif self.playbackmode == 2:
            self.mpdaddalbum(self.currentartist, self.currentalbum.next)
            self.mpd.play(0)

    def updatempd(self):
        newstatus = self.mpd.status()
        changed = (newstatus.get('time') != self.currentstatus.get('time'))
        self.currentstatus = newstatus

        newsong = self.mpd.currentsong()
        if (newsong != self.currentsong):
            if (not newsong and self.currentsong):
                self.playbackfinished()
                self.currentstatus = self.mpd.status()
                newsong = self.mpd.currentsong()
            self.currentsong = newsong
            self.activemenu.changedsong()
            changed = True

        return changed

    def rendermenu(self):
        if self.lastmenu != self.activemenu: self.activemenu.changedsong()
        self.lastmenu = self.activemenu
        self.activemenu.render()
        pygame.display.update()

    def main(self):
            self.playbackmode = 2
            self.activemenu = None
            self.lastmenu = None
            self.currentartist = None
            self.currentalbum = None
            self.currentstatus = {}
            self.currentsong = {}
            self.pygameinit() 
            self.mpdinit()

            self.createartistmenu()
            self.createalbummenu()
            self.createtrackmenu()
            self.createplayback()  
            self.setactivemenu(self.artistmenu)

            self.updatempd()
            self.currentartist = Entry(self.currentsong.get('artist'))
            self.currentalbum = Entry(self.currentsong.get('album'))
            self.addartists()
            self.currentalbum = self.selectartist(self.currentartist)
            
            state = self.currentstatus.get('state') 
            if state == 'stop': self.mpd.clear()
            if state == 'play' or state == 'pause':
                self.mpd.pause(0)
                self.setactivemenu(self.playback)
            else:
                self.setactivemenu(self.artistmenu)

            changed = True
            running = True
            timelast = time.time()
            while running:
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
                            self.prevtrackalbum()
                        elif (event.key == pygame.K_RIGHT):
                            self.nexttrackalbum()
                        elif (event.key == pygame.K_RETURN):
                            self.activemenu.keyenter()
                        elif (event.key == pygame.K_BACKSPACE):
                            self.activemenu.keybackspace()
                        elif (event.key == pygame.K_m):
                            self.togglemode()
                        elif (event.key == pygame.K_u):
                            self.mpd.update()
                            self.addartists()
                            self.setactivemenu(self.artistmenu)

                        changed = True
                        timelast = time.time()     

                if time.time() - timelast > 15 and self.currentstatus.get('state') == 'play' and self.activemenu != self.playback:
                    self.addartists()
                    self.selectartist(self.currentartist)
                    self.setactivemenu(self.playback)
                    changed = True

                if changed: self.rendermenu()
                time.sleep(0.05)
                
                changed = self.updatempd()
