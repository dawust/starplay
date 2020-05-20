import time
import pygame
from mpd import MPDClient
import menus
from constants import *
import slirc
import random

class Entry:
    def __init__(self, name, filename=None):
        self.name = name
        self.filename = filename
        self.next = None
        self.prev = None
        self.marker = None

class Song:
    def __init__(self, artist, album, track, index):
        self.artist = artist
        self.album = album
        self.track = track
        self.index = index

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
        pygame.display.init()
        pygame.display.set_caption("splay")
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        size = (1024,576)
        self.surface = pygame.display.set_mode(size)
        pygame.mouse.set_visible(False)

    def createartistmenu(self):
        self.artistmenu = menus.Menu(self.surface, self, "Artists")
        self.artistmenu.setevententer(lambda: self.selectartist(self.artistmenu.getentry()))
        self.artistmenu.seteventbackspace(self.leaveplayer)

    def createalbummenu(self):
        self.albummenu = menus.Menu(self.surface, self)
        self.albummenu.setevententer(lambda: self.selectalbum(self.artistmenu.getentry(), self.albummenu.getentry()))
        self.albummenu.seteventbackspace(lambda: self.setactivemenu(self.artistmenu))

    def createtrackmenu(self):
        self.trackmenu = menus.Menu(self.surface, self)
        self.trackmenu.setevententer(self.selecttrack)
        self.trackmenu.seteventbackspace(lambda: self.setactivemenu(self.albummenu))
        self.trackmenu.seteventcontrol(self.makereservation)

    def createplayback(self):
        self.playback = menus.Playscreen(self.surface, self)
        self.playback.setevententer(self.mpd.pause)
        def selectalbumcurrent():
            self.selectartist(self.currentartist)
            self.selectalbum(self.currentartist, self.currentalbum)
        self.playback.seteventbackspace(selectalbumcurrent)
        self.playback.seteventcontrol(self.makereservation)
        
    def createrandomplayback(self):
        self.randomplayback = menus.Playscreen(self.surface, self)
        self.randomplayback.setevententer(self.mpd.pause)
        self.randomplayback.seteventbackspace(lambda: self.setactivemenu(self.artistmenu))

    def leaveplayer(self):
        self.locked = 1
        slirc.sendenter(self.sockserial)
        
    def setactivemenu(self, menu):
        self.activemenu = menu

    def addartists(self):
        self.artistmenu.clear()
        self.artistmenu.addentry(self.randomentry)
        self.artistmenu.setpos()
        artists = self.mpd.list("ALBUMARTIST")
        for artist in sorted(artists, key=lambda s: s.lower()):
            self.artistmenu.addentry(Entry(artist))
            if self.currentartist.name == artist and self.playbackmode != 1: self.artistmenu.setpos()
    
    def selectartist(self, artist):
        if artist == self.randomentry:
            self.selectrandomplayback()
            return self.randomentry
    
        ret = Entry("XXX")
        albums = self.mpd.list("ALBUM", "ALBUMARTIST", artist.name)
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
        tracks = self.mpd.find("ALBUMARTIST", artist.name, "ALBUM", album.name)
        self.trackmenu.clear()
        self.trackmenu.setname(album.name)
        for track in tracks:
            entry = Entry(track.get('title'), track.get('file'))
            self.trackmenu.addentry(entry)
            if self.currentsong.get('file') == track.get('file'):
                self.trackmenu.setpos()
        
        self.settrackmarker()
        self.setactivemenu(self.trackmenu)

    def selecttrack(self):
        if self.playbackmode != 0 or (self.currentsong.get('file') != self.trackmenu.getentry().filename):
            self.playtrack(Song(self.artistmenu.getentry(), self.albummenu.getentry(), self.trackmenu.getentry(), self.trackmenu.getpos()))
        self.mpd.pause(0)
        self.setactivemenu(self.playback)
 
    def playtrack(self, track):
        self.playbackmode = 0
        self.mpd.random(0)
        self.cancelreservation()
        self.mpdaddalbum(track.artist, track.album)
        self.addartists()
        self.mpd.play(track.index)
       
    def selectrandomplayback(self):
        if self.playbackmode != 1:
            self.playbackmode = 1
            self.mpd.random(1)
            self.cancelreservation()
            self.mpd.clear()
            self.mpd.findadd('base', 'sorted')
            self.mpd.play(0)
            self.mpd.next()
        self.mpd.pause(0)
        self.setactivemenu(self.randomplayback)

    def makereservation(self):
        self.reservation = Song(self.artistmenu.getentry(), self.albummenu.getentry(), self.trackmenu.getentry(), self.trackmenu.getpos())
        self.settrackmarker()

    def cancelreservation(self):
        self.reservation = None

    def settrackmarker(self):
        if self.reservation:
            song = self.reservation
            for entry in self.trackmenu.entries:
                entryismarked = song.artist.name == self.artistmenu.getentry().name and song.album.name == self.albummenu.getentry().name and song.track.name == entry.name
                entry.marker = "XXX" if entryismarked else None
        
    def mpdaddalbum(self, artist, album):
        self.currentartist = artist
        self.currentalbum = album
        self.mpd.clear()
        self.mpd.findadd("ALBUMARTIST", artist.name, "ALBUM", album.name)

    def prevtrackalbum(self):
        self.cancelreservation()
        playtime = self.currentstatus.get('time').split(':')
        timenow = int(playtime[0])
        if timenow > 10:
            self.mpd.seekcur(0)
        elif self.playbackmode == 0 and self.currentstatus.get('song') == '0':
            self.mpdaddalbum(self.currentartist, self.currentalbum.prev)
            self.currentstatus = self.mpd.status()
            self.mpd.play(int(self.currentstatus.get('playlistlength', 1)) - 1)
        else:
            self.mpd.previous()

    def nexttrackalbum(self):
        self.cancelreservation()
        self.mpd.next()

    def playbackfinished(self):
        if self.playbackmode == 0: 
            self.mpdaddalbum(self.currentartist, self.currentalbum.next)
        self.mpd.play(0)
            
    def updatempd(self):
        newstatus = self.mpd.status()
        changed = (newstatus.get('time') != self.currentstatus.get('time'))
        self.currentstatus = newstatus

        newsong = self.mpd.currentsong()
        if (newsong != self.currentsong):
            if (self.reservation):
                self.playtrack(self.reservation)
                self.currentstatus = self.mpd.status()
                newsong = self.mpd.currentsong()
            elif (not newsong and self.currentsong):
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

    def getactiveplaybackmenu(self):
        return self.playback if self.playbackmode == 0 else self.randomplayback

    def resetplayer(self):
        self.mpd.update()
        self.addartists()
        self.setactivemenu(self.artistmenu)

    def main(self):
        self.randomentry = Entry("--- Random ---")
        self.locklatched = 0
        self.locked = 1
        self.playbackmode = 0
        self.activemenu = None
        self.lastmenu = None
        self.currentartist = None
        self.currentalbum = None
        self.currentstatus = {}
        self.currentsong = {}
        self.reservation = None
        self.pygameinit() 
        self.mpdinit()
        self.sockserial = slirc.connect()
        self.createartistmenu()
        self.createalbummenu()
        self.createtrackmenu()
        self.createplayback()
        self.createrandomplayback()
        self.setactivemenu(self.artistmenu)

        self.updatempd()

        randomstate = self.currentstatus.get('random')
        if randomstate == "1":
            self.playbackmode = 1

        self.currentartist = Entry(self.currentsong.get('albumartist') or self.currentsong.get('artist'))
        self.currentalbum = Entry(self.currentsong.get('album'))
        self.addartists()
        self.currentalbum = self.selectartist(self.currentartist)
        
        state = self.currentstatus.get('state') 
        if state == 'stop': self.mpd.clear()
        if state == 'play' or state == 'pause':
            self.mpd.pause(0)
            if self.playbackmode == 1:
                self.selectrandomplayback()
            else:
                self.setactivemenu(self.playback)
        else:
            self.setactivemenu(self.artistmenu)

        changed = True
        running = True
        timelast = time.time()
        while running:
            if self.locklatched == 1 and time.time() - timelast >= 1:
                self.locked = 1
                self.locklatched = 0
            
            for key in slirc.nextcodes(self.sockserial):
                if self.locklatched == 1:
                   self.locked = 0 if key == 'e' or key == 'E' else 1
                   self.locklatched = 0

                if self.locked == 0:
                    if key == 'l': self.prevtrackalbum()
                    if key == 'r': self.nexttrackalbum()
                    
                    if key == 'L': self.resetplayer()
                    if key == 'R': self.activemenu.keycontrol()

                    if key == 'b': self.activemenu.keybackspace()
                    if key == 'e' or key == 'E':
                        self.activemenu.keyenter()
                        slirc.sendback(self.sockserial)
                    if key == 'c': self.activemenu.keyenter()

                    if key == 'u': self.activemenu.keyup()
                    if key == 'd': self.activemenu.keydown()
                
                    if key == 'D': self.activemenu.keypgdn()
                    if key == 'U': self.activemenu.keypgup()

                if key == 'x' and self.locked == 0: self.locklatched = 1
                if key == 'C': self.locked = 0
                if key == 'B': self.nexttrackalbum()

                changed = True
                timelast = time.time()     

            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    return
                elif (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        return
                    elif (event.key == pygame.K_DOWN): self.activemenu.keydown()
                    elif (event.key == pygame.K_UP): self.activemenu.keyup()
                    elif (event.key == pygame.K_LEFT): self.prevtrackalbum()
                    elif (event.key == pygame.K_RIGHT): self.nexttrackalbum()
                    elif (event.key == pygame.K_RETURN): self.activemenu.keyenter()
                    elif (event.key == pygame.K_BACKSPACE): self.activemenu.keybackspace()
                    elif (event.key == pygame.K_PAGEDOWN): self.activemenu.keypgdn()
                    elif (event.key == pygame.K_PAGEUP): self.activemenu.keypgup()
                    elif (event.key == pygame.K_c): self.locked = 0
                    elif (event.key == pygame.K_u): self.resetplayer()
                    elif (event.key == pygame.K_r): self.activemenu.keycontrol()

                    changed = True
                    timelast = time.time()     

            if time.time() - timelast > 15 and self.currentstatus.get('state') == 'play' and self.activemenu != self.getactiveplaybackmenu():
                self.addartists()
                self.selectartist(self.currentartist)
                self.setactivemenu(self.getactiveplaybackmenu())
                changed = True

            try:
                changed |= self.updatempd()
                if changed: self.rendermenu()
            except Exception:
                self.resetplayer()

            time.sleep(0.05)
            
