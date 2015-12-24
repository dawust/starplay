#!/usr/bin/env python3
import time
import pygame
from mpd import MPDClient
import menus

class Starplay:

    def mpdinit(self):
        running = False
        while not running:
            try:
                self.mpd = MPDClient()
                self.mpd.connect("10.1.1.3", 6600)
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
        self.artistmenu = menus.Menu(self.surface, "Artists")
        artists = self.mpd.list("ARTIST")
        for artist in sorted(artists, key=lambda s: s.lower()):
            self.artistmenu.addentry(menus.Entry(artist))
        self.artistmenu.setevententer(self.selectartist)
        self.artistmenu.seteventbackspace(lambda: None)

    def createalbummenu(self):
        self.albummenu = menus.Menu(self.surface)
        self.albummenu.setevententer(self.selectalbum)
        self.albummenu.seteventbackspace(lambda: self.setactivemenu(self.artistmenu))

    def createtrackmenu(self):
        self.trackmenu = menus.Menu(self.surface)
        self.trackmenu.setevententer(self.selecttrack)
        self.trackmenu.seteventbackspace(lambda: self.setactivemenu(self.albummenu))

    def createplayback(self):
        self.playback = menus.Playscreen(self.surface)
        self.playback.setevententer(self.mpd.pause)
        self.playback.seteventbackspace(self.selectalbum)

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
        return changed

    def setactivemenu(self, menu):
        self.activemenu = menu
        self.updatempd(update=True)
        self.rendermenu()

    def selectartist(self):
        artist = self.artistmenu.getentry().name
        if self.albummenu.getname() != artist:
            albums = self.mpd.list("ALBUM", "ARTIST", artist)
            self.albummenu.clear()
            self.albummenu.setname(artist)
            for album in sorted(albums, key=lambda s: s.lower()):
                self.albummenu.addentry(menus.Entry(album))
        self.setactivemenu(self.albummenu)

    def selectalbum(self):
        artist = self.artistmenu.getentry().name
        album = self.albummenu.getentry().name
        tracks = self.mpd.find("ARTIST", artist, "ALBUM", album)
        self.trackmenu.clear()
        self.trackmenu.setname(album)
        for track in tracks:
            self.trackmenu.addentry(menus.Entry(track.get('title'), track.get('file')))
            if self.currentsong.get('file') == track.get('file'):
                self.trackmenu.setpos(int(self.currentstatus.get('song')))
        self.setactivemenu(self.trackmenu)

    def selecttrack(self):
        if (self.currentsong.get('file') != self.trackmenu.getentry().filename):
            self.mpd.clear()
            songs = self.mpd.find("ARTIST", self.artistmenu.getentry().name , "ALBUM", self.albummenu.getentry().name)
            for song in songs:
                self.mpd.add(song.get('file'))
            self.mpd.play(self.trackmenu.getpos())
        self.mpd.pause(0)
        self.setactivemenu(self.playback)

    def main(self):
            self.currentstatus = {}
            self.currentsong = {}
            self.pygameinit()
            
            self.mpdinit()
            self.createartistmenu()
            self.createalbummenu()
            self.createtrackmenu()
            self.createplayback()  

            self.setactivemenu(self.artistmenu)
           
            running = True
            while running:
                changed = self.updatempd()
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

                if changed: self.rendermenu()
                time.sleep(0.05)

if __name__ == "__main__":
    Starplay().main()
