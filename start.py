import sys

from terramap import world


worldpath = sys.argv[1]
world.World(worldpath, 'tiles.csv').draw_map('map.png')
