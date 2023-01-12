from __future__ import annotations

import os.path
import sys
from typing import Tuple

import pygame as pg

colors = pg.Color


def load_image(name: str, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


class Player(pg.sprite.Sprite):
    def __init__(self, *group, pos: Tuple[int, int] = (0, 0), size: Tuple[int, int] = (24, 40)):
        super(Player, self).__init__(*group)

        self.image = pg.transform.scale(load_image('mar.png'), size)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


class SplashScreen(pg.sprite.Sprite):
    def __init__(self, *groups, pos: Tuple[int, int] = (0, 0), size: Tuple[int, int] = None):
        super(SplashScreen, self).__init__(*groups)

        self.image = load_image('fon.jpg')
        self.image = pg.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def delete(self):
        del self.image
        del self.rect
        del self


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = 50

        self.ground = load_image('grass.png')
        self.gr_rect = self.ground.get_rect()
        self.box = load_image('box.png')
        self.box_rect = self.box.get_rect()
        self.player = Player()
        self.load_level('map1.txt')

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def get_cell_pos(self, cell_coords: Tuple[int, int]) -> Tuple[int, int]:
        x, y = cell_coords
        return x * self.cell_size + self.left, y * self.cell_size + self.top

    def render(self, surface: pg.Surface):
        for y in range(self.height):
            for x in range(self.width):

                if self.board[x][y] == 0:
                    self.gr_rect.topleft = (x * self.cell_size + self.left, y * self.cell_size + self.left)
                    surface.blit(self.ground, self.gr_rect)
                elif self.board[x][y] == 1:
                    self.box_rect.topleft = (x * self.cell_size + self.left, y * self.cell_size + self.left)
                    surface.blit(self.box, self.box_rect)
                elif self.board[x][y] == 2:
                    _x, _y = self.get_cell_pos((x, y))
                    self.player.rect.topleft = _x + self.cell_size // 2 - 14 // 2, _y + self.cell_size // 2 - 40 // 2
                    self.gr_rect.topleft = (x * self.cell_size + self.left, y * self.cell_size + self.left)
                    surface.blit(self.ground, self.gr_rect)
                    surface.blit(self.player.image, self.player.rect)

    def on_click(self, cell_coords):
        x, y = cell_coords
        state = self.board[x][y]

    def get_cell(self, mouse_pos):
        for y in range(self.height):
            for x in range(self.width):
                x1, y1 = x * self.cell_size + self.left, y * self.cell_size + self.top
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size

                if mouse_pos[0] in range(x1, x2) and mouse_pos[1] in range(y1, y2):
                    return x, y
        return

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def load_level(self, name: str):
        with open(file=os.path.abspath(f'data/{name}'), mode='r', encoding='utf-8') as file:
            lines = file.readlines()[1:]
            board = list()
            for line in lines:
                line = line[:-1] if line.endswith('\n') else line
                line: list = line.split(' ')
                line = list(map(int, line))
                board.append(line)
            self.board = board
            self.width, self.height = len(board), len(board[0])

    def step_left(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[x][y] == 2:
                    state = self.board[x - 1][y]

                    if x > 0 and state == 0:
                        self.board[x - 1][y] = 2
                        self.board[x][y] = state
                    else:
                        ...

    def step_right(self):
        is_continue = True

        for y in range(self.height):
            for x in range(self.width):
                if self.board[x][y] == 2:
                    state = self.board[x + 1][y]

                    if x < self.width - 1 and state == 0:
                        self.board[x + 1][y] = 2
                        self.board[x][y] = state
                        is_continue = False
                    else:
                        ...
                    if not is_continue:
                        break
            if not is_continue:
                break

    def step_up(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[x][y] == 2:
                    state = self.board[x][y - 1]

                    if y > 0 and state == 0:
                        self.board[x][y - 1] = 2
                        self.board[x][y] = state
                    else:
                        ...

    def step_down(self):
        is_continue = True

        for y in range(self.height):
            for x in range(self.width):
                if self.board[x][y] == 2:
                    state = self.board[x][y + 1]

                    if y < self.height - 1 and state == 0:
                        self.board[x][y + 1] = 2
                        self.board[x][y] = state
                        is_continue = False
                    else:
                        ...
                    if not is_continue:
                        break
            if not is_continue:
                break

    def update(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.step_left()
        elif keys[pg.K_RIGHT]:
            self.step_right()
        elif keys[pg.K_DOWN]:
            self.step_down()
        elif keys[pg.K_UP]:
            self.step_up()


class App:
    def __init__(self, size: Tuple[int, int] = (600, 600)):
        self.is_run = False
        self.is_splash = True
        self.FPS = 10
        self.SIZE = self.WIDTH, self.HEIGHT = size

        pg.init()

        self.screen = pg.display.set_mode(self.SIZE)
        self.board = Board(self.WIDTH // 50, self.HEIGHT // 50)
        self.all_sprites = pg.sprite.Group()
        self.splash_screen = SplashScreen(self.all_sprites, size=self.SIZE)
        self.clock = pg.time.Clock()

    def run(self):
        self.is_run = True

        while self.is_run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.is_run = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.is_splash:
                        self.splash_screen.delete()
                        self.is_splash = False

            # Update
            self.all_sprites.update()
            self.board.update()

            # Render
            self.screen.fill(colors('black'))

            if self.is_splash:
                self.all_sprites.draw(self.screen)
            else:
                self.board.render(self.screen)

            self.clock.tick(self.FPS)
            pg.display.flip()
        pg.quit()


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()
