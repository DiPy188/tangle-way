from __future__ import annotations

import random
from threading import Thread

import os.path
import sys
from typing import Tuple

import pygame as pg

colors = pg.Color

group_sprite_green_doorV = pg.sprite.Group()  # Группа зелённых дверей
group_sprite_red_doorV = pg.sprite.Group()  # Группа красных дверей

group_sprite_green_doorH = pg.sprite.Group()  # Группа зелённых дверей
group_sprite_red_doorH = pg.sprite.Group()  # Группа красных дверей

greenVH = pg.sprite.Group()
redVH = pg.sprite.Group()
all_obj = pg.sprite.Group()

key = pg.sprite.Group()
group_sprite_wall = pg.sprite.Group()  # группа обычных блоков
group_sprite_surf = pg.sprite.Group()  # Группа поверхности

all_sprites = pg.sprite.Group()

"""Параметры экрана: Буферизация|Разрешение"""
size: Tuple[int, int] = (1280, 720)  # Разрешение экрана
SIZE = WIDTH, HEIGHT = size
flags = pg.FULLSCREEN | pg.DOUBLEBUF  # Полныйэкран|Буферизация
screen = pg.display.set_mode(flags=flags)

"""Персонажи"""
player = pg.sprite.Group()  # сам игрок
mobV = pg.sprite.Group()  # Группа вертикальных врагов
mobH = pg.sprite.Group()  # Группа горизонтальных врагов
vector_enemyV = {}  # Направление движения вертикальных врагов (верх или низ)
vector_enemyH = {}  # Направление движения горизонтальных врагов (лево или право)
numV = 0  # Номер спрайта, для определения направления скорости после столкновения
numH = 0  # Номер спрайта, для определения направления скорости после столкновения

enemy = pg.sprite.Group()
enemy.add(mobH, mobV)


def load_image(name, colorkey=None):
    fullname = os.path.join('data/', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname).convert_alpha()
    return image


def generate_level(name):
    level = list()
    if os.path.isfile(f'data/' + name):
        with open(file=f'data/' + name) as r:
            lines = r.readlines()
        for i in lines:
            level.append(('').join(i.split()))
        del level[-2]

        # Создание игрового поля
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == 's':  # 0 - поверхность
                    Surface('grass', x, y)
                elif level[y][x] == 'w':  # 1 - стена
                    Wall('wall', x, y)
                elif level[y][x] == 'G':  # 2 - зелёная дверь вертикальна
                    GreenV('green_door', x, y)
                elif level[y][x] == 'R':  # 3 - красная дверь вертикальна
                    RedV('red_door', x, y)
                elif level[y][x] == 'g':  # 2 - зелёная дверь горизонтальна
                    GreenH('green_door', x, y)
                elif level[y][x] == 'r':  # 3 - красная дверь горизонтальна
                    RedH('red_door', x, y)
                elif level[y][x] == 'E':  # e - Враг двигается по вертикали
                    Surface('grass', x, y)
                    EnemyV('enemy', x, y)
                elif level[y][x] == 'e':  # e - Враг двигается по горизонтали
                    Surface('grass', x, y)
                    EnemyH('enemy', x, y)
                elif level[y][x] == 'k':
                    Surface('grass', x, y)
                    Key('key', x, y)

        Player(lines[-1].split()[0], lines[-1].split()[1])  # сам игрок


objects = {
    'green_door': load_image('green_door.png'),
    'red_door': load_image('red_door.png'),
    'wall': load_image('wall.png'),
    'grass': load_image('grass.png'),
    'player': load_image('player.png'),
    'enemy': load_image('enemy.png'),
    'key': load_image('key.png')
}
tile_width = tile_height = 50  # Размер для отступа от спрайта


# Ниже заполнение игрового поля спрайтами
class GreenV(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_green_doorV)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class RedV(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_red_doorV)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class GreenH(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_green_doorH)
        self.image = objects[sprite_name]
        self.image = pg.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class RedH(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_red_doorH)
        self.image = objects[sprite_name]
        self.image = pg.transform.rotate(self.image, 90)
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
        # self.image = objects[sprite_name]
        # self.rect = self.image.get_rect().move(
        #     tile_width * pos_x, tile_height * pos_y)


class EnemyV(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(mobV)
        global vector_enemyV, numV

        vector_enemyV[numV] = random.choice([-1, 1])
        numV += 1

        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y
        )


class EnemyH(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(mobH)
        global vector_enemyH, numH

        vector_enemyH[numH] = random.choice([-1, 1])
        numH += 1
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y
        )


class Key(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(key)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y
        )


class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player)
        self.x = int(x)
        self.y = int(y)
        self.image = load_image('player.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)


class App:

    def __init__(self):
        super().__init__()
        global screen

        self.screen = screen
        self.is_run = False
        self.FPS = 60

        pg.init()

        self.clock = pg.time.Clock()

        self.left_edge = False
        self.right_edge = False
        self.up_edge = False
        self.down_edge = False
        self.door_coords = (0, 0, 0, 0)

    def run(self):
        self.is_run = True

        ''' Открытие БД и проверка, на каком уровне игрок с последующей передачей в | generate_level() | имени уровня'''
        generate_level('lvl1.txt')

        """объеденение всех спрайтов в группы """
        all_sprites.add(group_sprite_wall, player, mobH, mobV, group_sprite_green_doorV, group_sprite_red_doorV,
                        group_sprite_green_doorH,
                        group_sprite_red_doorH, key)
        enemy.add(mobH, mobV)
        greenVH.add(group_sprite_green_doorH, group_sprite_green_doorV)
        redVH.add(group_sprite_red_doorV, group_sprite_red_doorH)
        all_obj.add(group_sprite_wall, greenVH, redVH)

        all_sprites.draw(self.screen)
        self.door_r = True  #
        self.door_g = True  #

        while self.is_run:
            self.Enemy()
            keys = pg.key.get_pressed()
            for event in pg.event.get():

                if event.type == pg.QUIT:
                    self.is_run = False

            if keys[pg.K_UP] or keys[pg.K_w]:
                self.Move_pl(y=-2)

            if keys[pg.K_DOWN] or keys[pg.K_s]:
                self.Move_pl(y=2)

            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.Move_pl(x=-2)

            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.Move_pl(x=2)

            if keys[pg.K_r]:
                self.lvl_restart()

            self.clock.tick(self.FPS)
            self.screen.fill('black')
            all_sprites.draw(self.screen)
            pg.display.flip()

        pg.quit()

    def Move_pl(self, x=0, y=0):
        i = player.sprites()[0]

        # Прибавляем координаты игрока
        (x1, y1, x2, y2) = i.rect
        i.rect = (x1 + x, y1 + y, x2, y2)

        def check_wall():
            if len(list(
                    (wall_spr for wall_spr in group_sprite_wall.sprites() if pg.sprite.collide_mask(i, wall_spr)))) > 0:
                (x1, y1, x2, y2) = i.rect
                i.rect = (x1 - x, y1 - y, x2, y2)

        """Столкновение с дверьми"""

        # красная
        def check_red():
            if self.door_r == True:
                generator_2 = list(
                    (redV_spr for redV_spr in group_sprite_red_doorV.sprites() if pg.sprite.collide_mask(i, redV_spr)))
                generator_3 = list(
                    (redH_spr for redH_spr in group_sprite_red_doorH if pg.sprite.collide_mask(i, redH_spr)))

                if len(generator_2) > 0:
                    if x > 0:  # x - вектор движения

                        """Определение: пересекает ли правая грань спрайта игрока - спрайт двери"""

                        if i.rect[0] + 4 > generator_2[0].rect[0] + generator_2[0].rect[2]:
                            self.door_r = False
                            self.door_g = True




                    elif x < 0:

                        """Определение: пересекает ли правая грань спрайта игрока - спрайт двери"""
                        if i.rect[0] + i.rect[2] - 2 < generator_2[0].rect[0]:
                            self.door_r = False
                            self.door_g = True

                if len(generator_3) > 0:
                    print(1)
                    if y < 0:
                        if i.rect[1] + i.rect[3] - 2 < generator_3[0].rect[1]:
                            self.door_r = False
                            self.door_g = True

                    if y > 0:
                        if i.rect[1] + 4 > generator_3[0].rect[1] + generator_3[0].rect[3]:
                            self.door_r = False
                            self.door_g = True


            elif self.door_r == False:
                if len(list((red_door for red_door in redVH if pg.sprite.collide_mask(i, red_door)))) > 0:
                    (x1, y1, x2, y2) = i.rect
                    i.rect = (x1 - x, y1 - y, x2, y2)

        # зелёная
        def check_green():
            if self.door_g == True:
                generator_2 = list(
                    (greenV_spr for greenV_spr in group_sprite_green_doorV if
                     pg.sprite.collide_mask(i, greenV_spr)))
                generator_3 = list(
                    (greenH_spr for greenH_spr in group_sprite_green_doorH if
                     pg.sprite.collide_mask(i, greenH_spr)))

                if len(generator_2) > 0:
                    if x > 0:  # x - вектор движения

                        """Определение: пересекает ли правая грань спрайта игрока - спрайт двери"""

                        if i.rect[0] + 4 > generator_2[0].rect[0] + generator_2[0].rect[2]:
                            self.door_r = True
                            self.door_g = False




                    elif x < 0:

                        """Определение: пересекает ли правая грань спрайта игрока - спрайт двери"""
                        if i.rect[0] + i.rect[2] - 2 < generator_2[0].rect[0]:
                            self.door_r = True
                            self.door_g = False

                if len(generator_3) > 0:
                    if y < 0:
                        if i.rect[1] + i.rect[3] - 2 < generator_3[0].rect[1]:
                            self.door_r = True
                            self.door_g = False

                    if y > 0:
                        if i.rect[1] + 4 > generator_3[0].rect[1] + generator_3[0].rect[3]:
                            self.door_r = True
                            self.door_g = False


            elif self.door_g == False:
                if len(list((door_g for door_g in greenVH if pg.sprite.collide_mask(i, door_g)))) > 0:
                    (x1, y1, x2, y2) = i.rect
                    i.rect = (x1 - x, y1 - y, x2, y2)

        thr_wall = Thread(target=check_wall())
        thr_red = Thread(target=check_red())
        thr_green = Thread(target=check_green())

        thr_wall.start()
        thr_red.start()
        thr_green.start()

        thr_wall.join()
        thr_red.join()
        thr_green.join()

    def lvl_restart(self):
        for i in all_sprites:
            i.kill()
        for i in group_sprite_wall:
            i.kill()
        for i in group_sprite_green_doorV:
            i.kill()
        for i in group_sprite_red_doorV:
            i.kill()
        for i in group_sprite_green_doorH:
            i.kill()
        for i in group_sprite_red_doorH:
            i.kill()
        for i in greenVH:
            i.kill()
        for i in redVH:
            i.kill()
        for i in enemy:
            i.kill()
        for i in player:
            i.kill()
        for i in mobH:
            i.kill()
        for i in mobV:
            i.kill()
        for i in key:
            i.kill()
        for i in all_obj:
            i.kill()

        """открытие бд для уровня"""
        generate_level('lvl1.txt')

        all_sprites.add(group_sprite_wall, player, mobH, mobV, group_sprite_green_doorV, group_sprite_red_doorV,
                        group_sprite_green_doorH,
                        group_sprite_red_doorH, key)
        enemy.add(mobH, mobV)
        greenVH.add(group_sprite_green_doorH, group_sprite_green_doorV)
        redVH.add(group_sprite_red_doorV, group_sprite_red_doorH)
        all_obj.add(group_sprite_wall, greenVH, redVH)
        all_sprites.draw(self.screen)

        self.door_r = True  # Красная, В какую дверь игрок может войти (по умолчанию в любую)
        self.door_g = True  # Зелёная, В какую дверь игрок может войти (по умолчанию в любую)

    def Enemy(self):
        def vectorH_enemy():
            for numh, mh in enumerate(mobH):
                (x1h, y1h, x2h, y2h) = mh.rect
                mh.rect = (x1h + vector_enemyH[numh], y1h, x2h, y2h)

                if len(list((j for j in all_obj if pg.sprite.collide_mask(mh, j)))) > 0:
                    (x1h, y1h, x2h, y2h) = mh.rect
                    mh.rect = (x1h - vector_enemyH[numh], y1h, x2h, y2h)
                    if vector_enemyH[numh] == 1:
                        vector_enemyH[numh] = -1
                    elif vector_enemyH[numh] == -1:
                        vector_enemyH[numh] = 1

        def vectorV_enemy():
            for numv, mv in enumerate(mobV):
                (x1v, y1v, x2v, y2v) = mv.rect
                mv.rect = (x1v, y1v + vector_enemyV[numv], x2v, y2v)

                if len(list((j for j in all_obj if pg.sprite.collide_mask(mv, j)))) > 0:
                    if vector_enemyV[numv] == 1:
                        vector_enemyV[numv] = -1
                        (x1v, y1v, x2v, y2v) = mv.rect
                        mv.rect = (x1v, y1v + vector_enemyV[numv], x2v, y2v)

                    elif vector_enemyV[numv] == -1:
                        vector_enemyV[numv] = 1
                        (x1v, y1v, x2v, y2v) = mv.rect
                        mv.rect = (x1v, y1v + vector_enemyV[numv], x2v, y2v)

        """Проверка на столкновение с врагом"""
        if len(list((e for e in enemy if pg.sprite.collide_mask(player.sprites()[0], e)))) > 0:
            exit()
        enemy_thr1 = Thread(target=vectorH_enemy)
        enemy_thr2 = Thread(target=vectorV_enemy)

        enemy_thr1.start()
        enemy_thr2.start()

        enemy_thr1.join()
        enemy_thr2.join()


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()
