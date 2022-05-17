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


class Bird:
    def __init__(self, x: float, y: float) -> None:
        self._images: List[pg.Surface] = BIRD_IMGS
        self._max_rotation: float = 25.0
        self._rotation_velocity: float = 20.0
        self._animation_time: float = 5.0

        self.x: float = x
        self.y: float = y
        self.tilt: float = 0.0
        self.tick_count: int = 0
        self.velocity: float = 0.0
        self.height: float = self.y
        self.img_count: int = 0
        self.image: pg.Surface = self._images[0]

    def jump(self) -> None:
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self) -> None:
        self.tick_count += 1

        position_change: float = min(
            self.velocity * self.tick_count + 1.5 * self.tick_count**2, 16.0
        )

        if position_change < 0:
            position_change -= 2.0

        self.y += position_change

        if position_change < 0 or self.y < self.height + 50.0:
            if self.tilt < self._max_rotation:
                self.tilt = self._max_rotation
        else:
            if self.tilt > -90.0:
                self.tilt -= self._rotation_velocity

    def draw(self, win) -> None:
        self.img_count += 1

        if self.img_count < self._animation_time:
            self.image = self._images[0]
        elif self.img_count < self._animation_time * 2:
            self.image = self._images[1]
        elif self.img_count < self._animation_time * 3:
            self.image = self._images[2]
        elif self.img_count < self._animation_time * 4:
            self.image = self._images[1]
        elif self.img_count == self._animation_time * 4 + 1:
            self.image = self._images[0]
            self.img_count = 0

        if self.tilt <= -80.0:
            self.image = self._images[1]
            self.img_count = self._animation_time * 2

        rotated_image = pg.transform.rotate(self.image, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.image.get_rect(topleft=(self.x, self.y)).center
        )
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self) -> pg.mask.Mask:
        return pg.mask.from_surface(self.image)


def draw_window(win, bird: Bird) -> None:
    win.blit(BG_IMG, (0, 0))
    bird.draw(win)
    pg.display.update()


def main():
    bird = Bird(200, 200)
    win = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    clock = pg.time.Clock()
    run = True
    while run:
        clock.tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    bird.jump()
        bird.move()
        draw_window(win, bird)
    pg.quit()
    quit()


main()
