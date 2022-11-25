import os
import random
from typing import List

import neat as nt
import pygame as pg

pg.font.init()

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

SCORE_FONT = pg.font.SysFont("roboto", 50)


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


class Pipe:
    def __init__(self, x: float) -> None:
        self._gap: float = 200.0
        self._velocity: float = 5.0
        self.x: float = x
        self.height: float = 0.0
        self.top: float = 0.0
        self.bottom: float = 0.0
        self.pipe_top = pg.transform.flip(PIPE_IMG, False, True)
        self.pipe_bottom = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self) -> None:
        self.height = random.randrange(50, 450)
        self.top = self.height - self.pipe_top.get_height()
        self.bottom = self.height + self._gap

    def move(self) -> None:
        self.x -= self._velocity

    def draw(self, win) -> bool:
        win.blit(self.pipe_top, (self.x, self.top))
        win.blit(self.pipe_bottom, (self.x, self.bottom))

    def collide(self, bird: Bird) -> None:
        bird_mask: pg.mask.Mask = bird.get_mask()
        top_mask: pg.mask.Mask = pg.mask.from_surface(self.pipe_top)
        bottom_mask: pg.mask.Mask = pg.mask.from_surface(self.pipe_bottom)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        return t_point or b_point


class Base:
    def __init__(self, y: float) -> None:
        self._velocity: float = 5.0
        self._width: float = BASE_IMG.get_width()
        self._image: pg.Surface = BASE_IMG

        self.y: float = y
        self.x1: float = 0.0
        self.x2: float = self._width

    def move(self) -> None:
        self.x1 -= self._velocity
        self.x2 -= self._velocity

        if self.x1 + self._width < 0:
            self.x1 = self.x2 + self._width
        if self.x2 + self._width < 0:
            self.x2 = self.x1 + self._width

    def draw(self, win) -> None:
        win.blit(self._image, (self.x1, self.y))
        win.blit(self._image, (self.x2, self.y))


def draw_window(
    win, base: Base, pipes: List[Pipe], birds: List[Bird], score: int
) -> None:
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = SCORE_FONT.render(f"Score: {score}", True, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pg.display.update()


def fitness(genomes, config: nt.config.Config) -> None:
    nets: List[nt.nn.FeedForwardNetwork] = []
    ge = []
    birds: List[Bird] = []

    for _, g in genomes:
        g.fitness = 0
        nets.append(nt.nn.FeedForwardNetwork.create(g, config))
        birds.append(Bird(230, 350))
        ge.append(g)

    base: Base = Base(WIN_HEIGHT - 70)
    pipes: List[Pipe] = [Pipe(700)]
    win = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    clock = pg.time.Clock()
    score: int = 0
    run = True
    while run:
        clock.tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        pipe_idx: int = 0
        if len(birds) > 0:
            if (
                len(pipes) > 1
                and birds[0].x > pipes[0].x + pipes[0].pipe_top.get_width()
            ):
                pipe_idx = 1
        else:
            run = False

        for idx, bird in enumerate(birds):
            bird.move()
            ge[idx].fitness += 0.1
            output = nets[idx].activate(
                (
                    bird.y,
                    abs(bird.y - pipes[pipe_idx].height),
                    abs(bird.y - pipes[pipe_idx].bottom),
                )
            )
            if output[0] > 0.5:
                bird.jump()

        base.move()
        pipes_to_remove: List[Pipe] = []
        add_pipe: bool = False
        for pipe in pipes:
            for idx, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[idx].fitness -= 1
                    nets.pop(idx)
                    birds.pop(idx)
                    ge.pop(idx)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.pipe_top.get_width() < 0:
                pipes_to_remove.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
        for r_pipe in pipes_to_remove:
            pipes.remove(r_pipe)

        for idx, bird in enumerate(birds):
            bird.move()
            if bird.y + bird.image.get_height() >= WIN_HEIGHT - 70 or bird.y < 0:
                nets.pop(idx)
                birds.pop(idx)
                ge.pop(idx)

        draw_window(win, base, pipes, birds, score)


def run(config_path: str) -> None:
    config = nt.config.Config(
        nt.DefaultGenome,
        nt.DefaultReproduction,
        nt.DefaultSpeciesSet,
        nt.DefaultStagnation,
        config_path,
    )

    population = nt.Population(config)
    population.add_reporter(nt.StdOutReporter(True))
    population.add_reporter(nt.StatisticsReporter())

    winner = population.run(fitness, 50)


if __name__ == "__main__":
    local_dir: str = os.path.dirname(__file__)
    config_path: str = os.path.join(local_dir, "config_neat.txt")
    run(config_path)
