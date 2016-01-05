import sys

from terramap.world import World


worldpath = sys.argv[1]
imgpath = sys.argv[2] if len(sys.argv) > 2 else 'map.png'

World(worldpath, 'data').draw_map(imgpath)
