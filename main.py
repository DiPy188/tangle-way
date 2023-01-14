from __future__ import annotations

import os.path
import sys
from typing import Tuple

import pygame as pg

colors = pg.Color

group_sprite_green_door = pg.sprite.Group() #Группа зелённых дверей
group_sprite_red_door = pg.sprite.Group() #Группа красных дверей
group_sprite_wall = pg.sprite.Group() #группа обычных блоков
group_sprite_surf = pg.sprite.Group() #Группа поверхности
all_sprites = pg.sprite.Group()
player = pg.sprite.Group() #сам игрок

def load_image(name, colorkey=None):
    fullname = os.path.join('data/', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image



def generate_level(name):
    level = list()
    if os.path.isfile(f'data/' + name):
        with open(file=f'data/' + name) as r:
            lines = r.readlines()

        for i in lines:
            if i != 'pos':
                level.append(('').join(i.split()))

        #Создание игрового поля
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '0': #0 - трава
                    Surface('grass', x, y)
                elif level[y][x] == '1': #1 - стена
                    Wall('wall', x, y)
                elif level[y][x] == '2': #2 - зелёная дверь
                    Green('green_door', x, y)
                elif level[y][x] == '3': #3 - красная дверь
                    Red('red_door', x, y)

        Player(lines[-1].split()[0], lines[-1].split()[1]) #сам игрок

objects = {
    'green_door': load_image('green_door.png'),
    'red_door': load_image('red_door.png'),
    'wall': load_image('wall.png'),
    'grass': load_image('grass.png'),
    'player': load_image('player.png')
          }
tile_width = tile_height = 50 #Размер для отступа от спрайта


#Ниже заполнение игрового поля спрайтами
class Green(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_green_door)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

class Red(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_red_door)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

class Wall(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_wall)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

class Surface(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_surf)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player)
        self.x = int(x)
        self.y = int(y)
        self.image = load_image('player.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)














class App:

    def __init__(self, size: Tuple[int, int] = (1280, 720)):
        self.is_run = False
        self.is_splash = True
        self.FPS = 40
        self.SIZE = self.WIDTH, self.HEIGHT = size

        pg.init()

        self.screen = pg.display.set_mode(self.SIZE)
        self.clock = pg.time.Clock()

    def run(self):
        self.is_run = True

        ''' Открытие БД и проверка, на каком уровне игрок с последующей передачей в | generate_level() | имени уровня'''
        generate_level('map1.txt')

        all_sprites.add(group_sprite_wall, group_sprite_green_door, group_sprite_red_door, group_sprite_surf, player)
        all_sprites.draw(self.screen)

        self.c = False #для проверки условий столкнулся спрайт или нет

        self.door_r = True #
        self.door_g = True #

        while self.is_run:
            keys = pg.key.get_pressed()
            for event in pg.event.get():

                if event.type == pg.QUIT:
                    self.is_run = False

            if keys[pg.K_UP] or keys[pg.K_w]:
                self.Move_pl(y=-1)

            if keys[pg.K_DOWN] or keys[pg.K_s]:
                self.Move_pl(y=1)

            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.Move_pl(x=-1)

            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.Move_pl(x=1)

            if keys[pg.K_r]:
                self.lvl_restart()


            self.clock.tick(self.FPS)
            all_sprites.draw(self.screen)
            pg.display.flip()

        pg.quit()

    def Move_pl(self, x=0, y=0):
        for i in player:
            # Прибавляем координаты игрока
            (x1, y1, x2, y2) = i.rect
            i.rect = (x1 + x, y1 + y, x2, y2)
            for j in group_sprite_wall:
                # Если он пересек стену | c = True |
                if pg.sprite.collide_mask(i, j):
                    self.c = True
                    break

            """Столкновение с дверьми"""
            if self.door_r == True:
                for j in group_sprite_red_door:
                    if pg.sprite.collide_mask(i, j) and self.c is False:
                        i.rect = (x1 + (75 * x), y1 + y, x2, y2)
                        self.door_r = False
                        self.door_g = True
                        break

            elif self.door_r == False:
                for j in group_sprite_red_door:
                    if pg.sprite.collide_mask(i, j) and self.c is False:
                        i.rect = (x1 - x, y1 - y, x2, y2)
                        break


            if self.door_g == True:
                for j in group_sprite_green_door:
                    if pg.sprite.collide_mask(i, j) and self.c is False:
                        i.rect = (x1 + (75 * x), y1 + y, x2, y2)
                        self.door_g = False
                        self.door_r = True
                        break

            elif self.door_g == False:
                for j in group_sprite_green_door:
                    if pg.sprite.collide_mask(i, j) and self.c is False:
                        i.rect = (x1 - x, y1 - y, x2, y2)
                        break

            # если условие на пересечение стены выполнено, то возращаем игрока на предыдущую позицию
            if self.c:
                (x1, y1, x2, y2) = i.rect
                i.rect = (x1 - x, y1 - y, x2, y2)

        self.c = False

    def lvl_restart(self):
        for i in all_sprites:
            i.kill()
        for i in group_sprite_wall:
            i.kill()
        for i in group_sprite_green_door:
            i.kill()
        for i in group_sprite_red_door:
            i.kill()
        for i in group_sprite_surf:
            i.kill()
        generate_level('map1.txt')
        all_sprites.add(group_sprite_wall, group_sprite_green_door, group_sprite_red_door, group_sprite_surf,
                        player)
        all_sprites.draw(self.screen)
        self.c = False  # для проверки условий столкнулся спрайт c стеной или нет

        self.door_r = True  #
        self.door_g = True  #

def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()
