import os
import struct
import sys

from PIL import Image


class World:
    def __init__(self, worldpath, datapath):
        print 'loading world at', worldpath
        # load tile types
        self.tiletypes = []
        with open(os.path.join(datapath, 'tiles.csv'), 'rb') as tiles:
            for line in tiles.readlines():
                id, name, frames, r, g, b, a = [l.strip() for l in line.split(', ')]
                self.tiletypes.append({
                    'name': name,
                    'frames': frames == '1',
                    'colour': (int(r), int(g), int(b), int(a))
                    })

        # load wall types
        self.walltypes = []
        with open(os.path.join(datapath, 'walls.csv'), 'rb') as walls:
            for line in walls.readlines():
                id, name, r, g, b, a = [l.strip() for l in line.split(', ')]
                self.walltypes.append({
                    'name': name,
                    'colour': (int(r), int(g), int(b), int(a))
                    })

        # load other colours
        self.colours = {}
        with open(os.path.join(datapath, 'colours.csv'), 'rb') as colours:
            for line in colours.readlines():
                name, r, g, b, a = [l.strip() for l in line.split(', ')]
                self.colours[name] = (int(r), int(g), int(b), int(a))

        # compatible map version
        version = 37  # 1.1.1

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
        width, height = self.header['width'], self.header['height']
        image = Image.new('RGB', (width, height))
        img = image.load()
        imagedata = []
        for y in range(height):
            self._display_progress(y + 1, height)
            for x in range(width):
                tile = self.tiles[x * height + y]

                # draw background
                if y < self.header['groundlevel']:
                    colour = self.colours['sky'][:3]
                elif y < self.header['rocklevel'] + 37:  # not sure why this number is off by 37
                    colour = self.colours['earth'][:3]
                elif y < height - 200:  # another magic number i'd prefer to do without
                    colour = self.colours['rock'][:3]
                else:
                    colour = self.colours['hell'][:3]

                # draw wall
                if 'walltype' in tile:
                    colour = self.walltypes[tile['walltype']]['colour'][:3]
                    # this line would be used if there were any walls with alpha values
                    # colour = self._combine_alpha(self.walltypes[tile['walltype']]['colour'],
                    #                              colour)

                # draw tile
                if 'type' in tile:
                    colour = self._combine_alpha(self.tiletypes[tile['type']]['colour'], colour)

                # draw liquid
                if 'liquidlevel' in tile:
                    lcolour = self.colours['lava'] if tile['lava'] else self.colours['water']
                    colour = self._combine_alpha(lcolour, colour, tile['liquidlevel'])

                img[x, y] = colour

        print 'saving image...'
        image.save(imgpath)
        print 'done.'

    def _combine_alpha(self, (fr, fg, fb, fa), (br, bg, bb), a=255):
        if fa == 255 and a == 255:
            return (fr, fg, fb)
        a /= 255.0 * fa / 255.0
        return (
            int(fr * a + br * (1 - a)),
            int(fg * a + bg * (1 - a)),
            int(fb * a + bb * (1 - a))
            )

    def _read_header(self):
        header = {}
        for key, type in [('version', 'dword'),
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
        tiles = []
        runlength = 0
        for x in range(width):
            self._display_progress(x + 1, width)
            for y in range(height):
                if runlength > 0:
                    # copy the previous tile this many times
                    tiles.append(tile)
                    runlength -= 1

                else:
                    tile = {}
                    if self._read_data('bool'):  # tile present?
                        tile['type'] = self._read_data('byte')
                        if self.tiletypes[tile['type']]['frames']:  # tile has multiple frames?
                            texu = self._read_data('word')
                            texv = self._read_data('word')
                            tile['texture'] = (texu, texv)
                    if self._read_data('bool'):  # has wall?
                        tile['walltype'] = self._read_data('byte')
                    if self._read_data('bool'):  # has liquid?
                        tile['liquidlevel'] = self._read_data('byte')
                        tile['lava'] = self._read_data('bool')
                    if self._read_data('bool'):  # has wire?
                        tile['wire'] = True

                    tiles.append(tile)
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
        for npc in ['merchant', 'nurse', 'armsdealer', 'dryad', 'guide', 'clothier',
                    'demolitionist', 'tinkerer', 'wizard', 'mechanic']:
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
            if length >= 128:
                length += (self._read_data('byte') - 1) * 128
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
