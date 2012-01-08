import struct
import sys

from PIL import Image

class World:
    def __init__(self, path):
        
        # load tile properties
        self.xtiles = []
        with open('tiles.csv', 'rb') as tiles:
            for line in tiles.readlines():
                id, type, special = line.strip().split(',')
                if special == '1':
                    self.xtiles.append(int(id))
                    
        with open(path, 'rb') as self.file:
            header = self.read_header()
            if header['version'] != 37:
                print 'Incompatible map version:', header['version']
                sys.exit(0)

            tiles = self.read_tiles(header['width'], header['height'])
            chests = self.read_chests()
            signs = self.read_signs()
            npcs = self.read_npcs()
            npcnames = self.read_npcnames()
        
        self.generate_image(tiles)

            
    def read_header(self):
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
            header[key] = self.read_data(type)
        return header

        
    def read_tiles(self, width, height):
        print 'reading tiles...'
        tiles = {}
        runlength = 0
        for x in range(width):
            self.display_progress(x + 1, width)
            for y in range(height):
                if runlength > 0:
                    # copy the previous tile this many times
                    tiles[(x, y)] = tile
                    runlength -= 1
                    
                else:
                    tile = {}
                    if self.read_data('bool'): # tile present?
                        tile['type'] = self.read_data('byte')
                        if tile['type'] in self.xtiles: # tile has multiple states?
                            texu = self.read_data('word')
                            texv = self.read_data('word')
                            tile['texture'] = (texu, texv)
                    if self.read_data('bool'): # has wall?
                        tile['walltype'] = self.read_data('byte')
                    if self.read_data('bool'): # has liquid?
                        tile['liquidlevel'] = self.read_data('byte')
                        tile['lava'] = self.read_data('bool')
                    if self.read_data('bool'): # has wire?
                        tile['wire'] = True
                        
                    tiles[(x, y)] = tile
                    runlength = self.read_data('word')
                    
        return tiles

                            
    def read_chests(self):            
        chests = []
        for chest in range(1000):
            if self.read_data('bool'):
                x = self.read_data('dword')
                y = self.read_data('dword')
                items = []
                for i in range(20):
                    count = self.read_data('byte')
                    name = self.read_data('pstring') if count > 0 else ''
                    prefix = self.read_data('byte') if count > 0 else 0
                    items.append((count, name, prefix))
                chests.append(((x, y), items))
        return chests

            
    def read_signs(self):
        signs = []
        for sign in range(1000):
            if self.read_data('bool'):
                text = self.read_data('pstring')
                x = self.read_data('dword')
                y = self.read_data('dword')
                signs.append(((x, y), text))
        return signs


    def read_npcs(self):        
        npcs = []
        while self.read_data('bool'):
            name = self.read_data('pstring')
            x = self.read_data('float')
            y = self.read_data('float')
            homeless = self.read_data('bool')
            homex = self.read_data('dword')
            homey = self.read_data('dword')
            npcs.append((name, (x, y), homeless, (homex, homey)))
        return npcs


    def read_npcnames(self):        
        npcnames = {}
        for npc in ['merchant', 'nurse', 'armsdealer', 'dryad', 'guide', 'clothier', 'demolitionist', 'tinkerer', 'wizard', 'mechanic']:
            npcnames[npc] = self.read_data('pstring')
        return npcnames
    
    
    def generate_image(self, tiles):
        print 'generating image...'
        image = Image.new('RGB', (level['width'], level['height']))
        imagedata = []
        for y in range(level['height']):
            self.display_progress(y + 1, level['height'])
            for x in range(level['width']):
                colour = (0, 0, 0) if 'type' in tiles[(x, y)] else (255, 255, 255)
                imagedata.append(colour)
        image.putdata(imagedata)
        print 'saving image...'
        image.save('map.png')
        print 'done.'
            
            
    def display_progress(self, divisor, dividend, interval=10):
        if divisor % (dividend / interval) == 0:
            print '{0}% done.'.format(int(divisor / float(dividend) * 100))
            
    
    def read_data(self, type):
        if type == 'dword':
            return struct.unpack('<I', self.file.read(4))[0]
        
        elif type == 'pstring':
            length = self.read_data('byte')
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
        


if __name__ == '__main__':
    path = sys.argv[1]
    World(path)