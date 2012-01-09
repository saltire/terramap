import struct
import sys

from PIL import Image

class World:
    def __init__(self, worldpath, tilelist):
        # load tile properties
        self.xtiles = []
        with open(tilelist, 'rb') as tiles:
            for line in tiles.readlines():
                id, type, special = line.strip().split(',')
                if special == '1':
                    self.xtiles.append(int(id))

        # compatible map version
        version = 37 # 1.1.1
                    
        with open(worldpath, 'rb') as self.file:
            self.header = self._read_header()
            if self.header['version'] != version:
                print 'Incompatible map version:', self.header['version']
                sys.exit(0)

            self.tiles = self._read_tiles(self.header['width'], self.header['height'])
            self.chests = self._read_chests()
            self.signs = self._read_signs()
            self.npcs = self._read_npcs()
            self.npcnames = self._read_npcnames()

            
    def draw_map(self, imgpath):
        print 'generating image...'
        image = Image.new('RGB', (self.header['width'], self.header['height']))
        img = image.load()
        imagedata = []
        for y in range(self.header['height']):
            self._display_progress(y + 1, self.header['height'])
            for x in range(self.header['width']):
                colour = (0, 0, 0) if 'type' in self.tiles[(x, y)] else (255, 255, 255)
                img[x, y] = colour
                
        print 'saving image...'
        image.save(imgpath)
        print 'done.'
            
            
    def _read_header(self):
        header = {}
        for key, type in [
                          ('version', 'dword'),
                          ('title', 'pstring'),
                          ('id', 'dword'),
                          ('bounds', 'rect'),
                          ('height', 'dword'),
                          ('width', 'dword'),
                          ('spawnx', 'dword'),
                          ('spawny', 'dword'),
                          ('groundlevel', 'double'),
                          ('rocklevel', 'double'),
                          ('time', 'double'),
                          ('night', 'bool'),
                          ('moonphase', 'dword'),
                          ('bloodmoon', 'bool'),
                          ('dungeonx', 'dword'),
                          ('dungeony', 'dword'),
                          ('boss1defeated', 'bool'),
                          ('boss2defeated', 'bool'),
                          ('boss3defeated', 'bool'),
                          ('goblinsaved', 'bool'),
                          ('wizardsaved', 'bool'),
                          ('mechanicsaved', 'bool'),
                          ('goblinsdefeated', 'bool'),
                          ('clowndefeated', 'bool'),
                          ('frostdefeated', 'bool'),
                          ('orbdestroyed', 'bool'),
                          ('meteor', 'bool'),
                          ('orbsdestroyed', 'byte'),
                          ('altarsdestroyed', 'dword'),
                          ('hardmode', 'bool'),
                          ('goblintime', 'dword'),
                          ('goblinsize', 'dword'),
                          ('goblintype', 'dword'),
                          ('goblinx', 'double')
                          ]:
            header[key] = self._read_data(type)
        return header

        
    def _read_tiles(self, width, height):
        print 'reading {0}x{1} tiles...'.format(width, height)
        tiles = {}
        runlength = 0
        for x in range(width):
            self._display_progress(x + 1, width)
            for y in range(height):
                if runlength > 0:
                    # copy the previous tile this many times
                    tiles[x, y] = tile
                    runlength -= 1
                    
                else:
                    tile = {}
                    if self._read_data('bool'): # tile present?
                        tile['type'] = self._read_data('byte')
                        if tile['type'] in self.xtiles: # tile has multiple states?
                            texu = self._read_data('word')
                            texv = self._read_data('word')
                            tile['texture'] = (texu, texv)
                    if self._read_data('bool'): # has wall?
                        tile['walltype'] = self._read_data('byte')
                    if self._read_data('bool'): # has liquid?
                        tile['liquidlevel'] = self._read_data('byte')
                        tile['lava'] = self._read_data('bool')
                    if self._read_data('bool'): # has wire?
                        tile['wire'] = True

                    tiles[x, y] = tile
                    runlength = self._read_data('word')
                    
        return tiles

                            
    def _read_chests(self):
        print 'reading chests...'          
        chests = []
        for i in range(1000):
            if self._read_data('bool'):
                x = self._read_data('dword')
                y = self._read_data('dword')
                items = []
                for j in range(20):
                    count = self._read_data('byte')
                    name = self._read_data('pstring') if count > 0 else ''
                    prefix = self._read_data('byte') if count > 0 else 0
                    items.append((count, name, prefix))
                chests.append(((x, y), items))
        return chests

            
    def _read_signs(self):
        print 'reading signs...'
        signs = []
        for i in range(1000):
            if self._read_data('bool'):
                text = self._read_data('pstring')
                x = self._read_data('dword')
                y = self._read_data('dword')
                signs.append(((x, y), text))
        return signs


    def _read_npcs(self):
        print 'reading npcs...'
        npcs = []
        while self._read_data('bool'):
            name = self._read_data('pstring')
            x = self._read_data('float')
            y = self._read_data('float')
            homeless = self._read_data('bool')
            homex = self._read_data('dword')
            homey = self._read_data('dword')
            npcs.append((name, (x, y), homeless, (homex, homey)))
        return npcs


    def _read_npcnames(self):    
        print 'reading npc names...'    
        npcnames = {}
        for npc in ['merchant', 'nurse', 'armsdealer', 'dryad', 'guide', 'clothier', 'demolitionist', 'tinkerer', 'wizard', 'mechanic']:
            npcnames[npc] = self._read_data('pstring')
        return npcnames
    
    
    def _display_progress(self, divisor, dividend, interval=10):
        if divisor % (dividend / interval) == 0:
            print '{0}% done.'.format(int(divisor / float(dividend) * 100))
            
    
    def _read_data(self, type):
        if type == 'dword':
            return struct.unpack('<I', self.file.read(4))[0]
        
        elif type == 'pstring':
            length = self._read_data('byte')
            return struct.unpack('{0}s'.format(length), self.file.read(length))[0]
        
        elif type == 'rect':
            return struct.unpack('<iiii', self.file.read(16))
        
        elif type == 'double':
            return struct.unpack('<d', self.file.read(8))[0]
        
        elif type == 'bool':
                return struct.unpack('?', self.file.read(1))[0]
            
        elif type == 'byte':
            return struct.unpack('B', self.file.read(1))[0]
        
        elif type == 'word':
            return struct.unpack('<H', self.file.read(2))[0]
        
        elif type == 'float':
            return struct.unpack('<f', self.file.read(4))[0]
