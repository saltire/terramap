import struct
import sys

from PIL import Image

class World:
    def __init__(self, path):
        
        self.xtiles = []
        with open('tiles.txt', 'r') as tiles:
            for line in tiles.readlines():
                id, line = line.split(' ', 1)
                if line.strip()[-1:] == '*':
                    line = line.rsplit(' ', 1)[0]
                    self.xtiles.append(int(id))
            print self.xtiles
                    
        with open(path, 'rb') as self.file:
            level = {}
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
                level[key] = self.read_data(type)
                print key, level[key]
            print self.file.tell()
        
            print 'reading tiles...'
            tiles = {}
            more = 0
            for x in range(level['width']):
                self.display_progress(x + 1, level['width'])
                
                for y in range(level['height']):
                    
                    if more:
                        tiles[(x, y)] = tile
                        more -= 1
                        #print (x, y), more
                        
                    else:
                        tile = {}
                        if self.read_data('bool'):
                            tile['type'] = self.read_data('byte')
                            if tile['type'] in self.xtiles:
                                texu = self.read_data('word')
                                texv = self.read_data('word')
                                tile['tex'] = (texu, texv)
                        if self.read_data('bool'):
                            tile['walltype'] = self.read_data('byte')
                        if self.read_data('bool'):
                            tile['liquidlevel'] = self.read_data('byte')
                            tile['lava'] = self.read_data('bool')
                        if self.read_data('bool'):
                            tile['wire'] = True
                            
                        tiles[(x, y)] = tile
                        more = self.read_data('word')
                                                
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
            image.save('D:\\code\\python\\terramap\\img\\map.png')
            
                                    
            chests = []
            for chest in range(1000):
                if self.read_data('bool'):
                    x = self.read_data('dword')
                    y = self.read_data('dword')
                    items = []
                    for i in range(20):
                        stack = self.read_data('byte')
                        name = self.read_data('pstring') if stack > 0 else ''
                        items.append((stack, name))
                    chests.append(((x, y), items))
            print chests
            
            signs = []
            for sign in range(1000):
                if self.read_data('bool'):
                    text = self.read_data('pstring')
                    x = self.read_data('dword')
                    y = self.read_data('dword')
                    signs.append(((x, y), text))
            print signs
            
            npcs = []
            while self.read_data('bool'):
                name = self.read_data('pstring')
                x = self.read_data('float')
                y = self.read_data('float')
                homeless = self.read_data('bool')
                homex = self.read_data('dword')
                homey = self.read_data('dword')
                npcs.append((name, (x, y), homeless, (homex, homey)))
            print npcs
            
            
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
    World('\\\\ZOYD\\Users\\Marcus\\My Documents\\My Games\\Terraria\\Worlds\\world1.wld')