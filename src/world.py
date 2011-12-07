import struct

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
            #print self.file.tell()
        
            tiles = {}
            for x in range(1):
                if (x + 1) % (level['width'] / 10) == 0:
                    print 'read {0}% of tiles'.format(int((x + 1) / float(level['width']) * 100))
                
                for y in range(level['height']):
                    
                    try:
                        tiles[(x, y)] = {}
                        if self.read_data('bool'):
                            tiles[(x, y)]['type'] = self.read_data('byte')
                            if tiles[(x, y)]['type'] in self.xtiles:
                                texu = self.read_data('word')
                                texv = self.read_data('word')
                                tiles[(x, y)]['tex'] = (texu, texv)
                        tiles[(x, y)]['lighted'] = self.read_data('bool')
                        if self.read_data('bool'):
                            tiles[(x, y)]['walltype'] = self.read_data('byte')
                        if self.read_data('bool'):
                            tiles[(x, y)]['liquidlevel'] = self.read_data('byte')
                            tiles[(x, y)]['lava'] = self.read_data('bool')
                    
                    except struct.error:
                        print 'error', (x, y), self.file.tell()
                        
                    print (x, y), tiles[(x, y)]
                        
            print 'generating image...'
            image = Image.new('RGB', (level['width'], level['height']))
            imagedata = []
            for y in range(level['width']):
                for x in range(level['height']):
                    colour = (255, 255, 255) if tiles[(x, y)]['type'] == 0 else (0, 0, 0) 
                    imagedata.append(color)
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
    World('C:\\Users\\Marcus\\My Documents\\My Games\\Terraria\\Worlds\\world1.wld')