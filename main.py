from __future__ import annotations

import multiprocessing
import random

import os.path
import sys
import threading
from time import time
from typing import Tuple
import pygame as pg

from multiprocessing import Process
from threading import Thread

colors = pg.Color

group_sprite_green_doorV = pg.sprite.Group()  # Группа зелённых дверей
group_sprite_red_doorV = pg.sprite.Group()  # Группа красных дверей

group_sprite_green_doorH = pg.sprite.Group()  # Группа зелённых дверей
group_sprite_red_doorH = pg.sprite.Group()  # Группа красных дверей

greenVH = pg.sprite.Group()
redVH = pg.sprite.Group()
all_obj = pg.sprite.Group()
all_objV = pg.sprite.Group()
all_objH = pg.sprite.Group()

key = pg.sprite.Group()
group_sprite_wall = pg.sprite.Group()  # группа обычных блоков
group_sprite_surf = pg.sprite.Group()  # Группа поверхности

all_sprites = pg.sprite.Group()

"""Раздеение групп спрайтов на четверти"""

"""Параметры экрана: Буферизация|Разрешение"""
size: Tuple[int, int] = (1280, 720)  # Разрешение экрана
SIZE = WIDTH, HEIGHT = size
flags = pg.DOUBLEBUF  # Полныйэкран|Буферизация
screen = pg.display.set_mode(flags=flags)

"""Персонажи"""
player = pg.sprite.Group()  # сам игрок
mobV = pg.sprite.Group()  # Группа вертикальных врагов
mobH = pg.sprite.Group()  # Группа горизонтальных врагов
dict_vector_enemyV = {}  # Направление движения вертикальных врагов (верх или низ)
dict_vector_enemyH = {}  # Направление движения горизонтальных врагов (лево или право)
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
        global dict_vector_enemyV, numV

        dict_vector_enemyV[numV] = random.choice([-1, 1])
        numV += 1

        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y
        )


class EnemyH(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(mobH)
        global dict_vector_enemyH, numH

        dict_vector_enemyH[numH] = random.choice([-1, 1])
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


generate_level('lvl1.txt')

collisions_objectV = {}
collisions_objectH = {}


class Enemy:

    def vectorH_enemy(self):
        for numh, mh in enumerate(mobH):
            (x1h, y1h, x2h, y2h) = mh.rect
            mh.rect = (x1h + dict_vector_enemyH[numh], y1h, x2h, y2h)

            if pg.sprite.collide_rect(collisions_objectH[numh][0], mh) or \
                    pg.sprite.collide_rect(collisions_objectH[numh][1], mh):
                (x1h, y1h, x2h, y2h) = mh.rect
                mh.rect = (x1h - dict_vector_enemyH[numh], y1h, x2h, y2h)
                if dict_vector_enemyH[numh] == 1:
                    dict_vector_enemyH[numh] = -1
                elif dict_vector_enemyH[numh] == -1:
                    dict_vector_enemyH[numh] = 1

    def vectorV_enemy(self):
        for numv, mv in enumerate(mobV):
            (x1v, y1v, x2v, y2v) = mv.rect
            mv.rect = (x1v, y1v + dict_vector_enemyV[numv], x2v, y2v)

            if pg.sprite.collide_rect(collisions_objectV[numv][0], mv) or \
                    pg.sprite.collide_rect(collisions_objectV[numv][1], mv):
                (x1h, y1h, x2h, y2h) = mv.rect
                mv.rect = (x1h, y1h - dict_vector_enemyV[numv], x2h, y2h)
                if dict_vector_enemyV[numv] == 1:
                    dict_vector_enemyV[numv] = -1

                elif dict_vector_enemyV[numv] == -1:
                    dict_vector_enemyV[numv] = 1


class App:

    def __init__(self):
        super().__init__()
        global screen

        self.screen = screen
        self.is_run = False
        self.FPS = 60

        pg.init()

        self.clock = pg.time.Clock()

    def run(self):
        self.is_run = True

        ''' Открытие БД и проверка, на каком уровне игрок с последующей передачей в | generate_level() | имени уровня'''

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

        check_wall()
        check_red()
        check_green()

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
        if len(list((e for e in enemy if pg.sprite.collide_mask(player.sprites()[0], e)))) > 0:
            exit()
        else:
            Enemy().vectorH_enemy()
            Enemy().vectorV_enemy()


greenVH.add(group_sprite_green_doorH, group_sprite_green_doorV)
redVH.add(group_sprite_red_doorV, group_sprite_red_doorH)
all_obj.add(group_sprite_wall, redVH, greenVH)


"""Два класса <<Enemy_dubler>> и <<A>> созданы для оптимизации уровня с врагами"""
class Enemy_dubler:

    def vectorH_enemy(self):
        for numh, mh in enumerate(mobH):
            (x1h, y1h, x2h, y2h) = mh.rect
            mh.rect = (x1h + dict_vector_enemyH[numh], y1h, x2h, y2h)
            gen = list((j for j in all_obj if pg.sprite.collide_mask(mh, j)))

            if len(gen) > 0:
                (x1h, y1h, x2h, y2h) = mh.rect
                mh.rect = (x1h - dict_vector_enemyH[numh], y1h, x2h, y2h)
                if dict_vector_enemyH[numh] == 1:
                    dict_vector_enemyH[numh] = -1
                elif dict_vector_enemyH[numh] == -1:
                    dict_vector_enemyH[numh] = 1
                return [gen[0], numh]

    def vectorV_enemy(self):
        for numv, mv in enumerate(mobV):
            (x1v, y1v, x2v, y2v) = mv.rect
            mv.rect = (x1v, y1v + dict_vector_enemyV[numv], x2v, y2v)
            gen = list((j for j in all_obj if pg.sprite.collide_mask(mv, j)))

            if len(gen) > 0:
                (x1h, y1h, x2h, y2h) = mv.rect
                mv.rect = (x1h, y1h - dict_vector_enemyV[numv], x2h, y2h)
                if dict_vector_enemyV[numv] == 1:
                    dict_vector_enemyV[numv] = -1

                elif dict_vector_enemyV[numv] == -1:
                    dict_vector_enemyV[numv] = 1

                return [gen[0], numv]


class A:
    def __init__(self, V=False, H=False):
        if V:

            init = Enemy_dubler()

            c = True
            sp = []
            CONST = len(dict_vector_enemyV)
            while c:
                V = init.vectorV_enemy()
                if V != None:
                    collision = V[0]
                    if V[1] not in collisions_objectV:
                        collisions_objectV[V[1]] = [collision]
                    elif V[1] in collisions_objectV:
                        a = collisions_objectV[V[1]]
                        if (a[0] != collision) and (len(collisions_objectV[V[1]]) < 3):
                            a = [a[0], collision]
                            collisions_objectV[V[1]] = a

                    for i in collisions_objectV:

                        if len(collisions_objectV[i]) == 2 and i not in sp:
                            sp.append(i)

                        if len(sp) == CONST:
                            sorted(collisions_objectV)
                            print(f'collisions_objectV: {collisions_objectV}')
                            c = False
                            break
        if H:
            init = Enemy_dubler()

            cc = True
            sp = []
            CONST = len(dict_vector_enemyH)

            while cc:
                H = init.vectorH_enemy()
                if H != None:
                    collision = H[0]
                    if H[1] not in collisions_objectH:
                        collisions_objectH[H[1]] = [collision]
                    elif H[1] in collisions_objectH:
                        a = collisions_objectH[H[1]]
                        if (a[0] != collision) and (len(collisions_objectH[H[1]]) < 3):
                            a = [a[0], collision]
                            collisions_objectH[H[1]] = a

                    for i in collisions_objectH:

                        if len(collisions_objectH[i]) == 2 and i not in sp:
                            sp.append(i)

                        if len(sp) == CONST:
                            sorted(collisions_objectH)
                            print(f'collisions_objectH: {collisions_objectH}')
                            cc = False
                            break


def miscalculation():

    thr1 = Thread(target=A, args=(False, True))
    thr2 = Thread(target=A, args=(True, False))

    thr1.start()
    thr2.start()

    thr1.join()
    thr2.join()




def main():
    miscalculation()

    app = App()
    app.lvl_restart()
    app.run()


if __name__ == '__main__':
    main()
