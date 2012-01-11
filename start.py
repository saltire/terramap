import sys

from terramap import world


worldpath = sys.argv[1]
world.World(worldpath, 'data').draw_map('map.png')
