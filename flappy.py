import os
import random
import time
from typing import List

import neat as nt
import pygame as pg

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS: List[pg.Surface] = [
    pg.transform.scale2x(pg.image.load(os.path.join("images", bird)))
    for bird in ["bird1.png", "bird2.png", "bird3.png"]
]
PIPE_IMG: pg.Surface = pg.transform.scale2x(
    pg.image.load(os.path.join("images", "pipe.png"))
)
BASE_IMG: pg.Surface = pg.transform.scale2x(
    pg.image.load(os.path.join("images", "base.png"))
)
BG_IMG: pg.Surface = pg.transform.scale2x(
    pg.image.load(os.path.join("images", "bg.png"))
)
