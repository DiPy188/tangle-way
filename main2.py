from __future__ import annotations
from typing import Tuple

import pygame as pg
import random
import os.path
import sys
from threading import Thread
from screeninfo import get_monitors

get_monitors()

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

gold_key = pg.sprite.Group()
count_gold_key = 0
exit_doors = pg.sprite.Group()

group_sprite_wall = pg.sprite.Group()  # группа обычных блоков
group_sprite_surf = pg.sprite.Group()  # Группа поверхности

all_sprites = pg.sprite.Group()

"""Раздеение групп спрайтов на четверти"""
quarter_1 = pg.sprite.Group()
quarter_2 = pg.sprite.Group()
quarter_3 = pg.sprite.Group()
quarter_4 = pg.sprite.Group()
quarter_5 = pg.sprite.Group()
quarter_6 = pg.sprite.Group()
quarter_7 = pg.sprite.Group()
quarter_8 = pg.sprite.Group()
quarter_9 = pg.sprite.Group()

list_quarter = [quarter_1, quarter_2, quarter_3, quarter_4, quarter_5, quarter_6, quarter_7, quarter_8, quarter_9]

"""Параметры экрана: Буферизация|Разрешение"""
x_monitor, y_monitor = get_monitors()[0].width, get_monitors()[0].height

size: Tuple[int, int] = (x_monitor, y_monitor)  # Разрешение экрана
print(size)
SIZE = WIDTH, HEIGHT = size
flags = pg.DOUBLEBUF  # Полныйэкран|Буферизация
screen = pg.display.set_mode(flags=flags)

"""Персонажи"""
player = pg.sprite.Group()  # сам игрок
mobV = pg.sprite.Group()  # Группа вертикальных врагов
mobH = pg.sprite.Group()  # Группа горизонтальных врагов

collisions_objectV = {}
collisions_objectH = {}

copy_collisions_objectV = {}
copy_collisions_objectH = {}

dict_vector_enemyV = {}  # Направление движения вертикальных врагов (верх или низ)
dict_vector_enemyH = {}  # Направление движения горизонтальных врагов (лево или право)
numV = 0  # Номер спрайта, для определения направления скорости после столкновения
numH = 0  # Номер спрайта, для определения направления скорости после столкновения

enemy = pg.sprite.Group()
tile_width = tile_height = 50  # Размер для отступа от спрайта


def load_image(name, colorkey=None):
    fullname = os.path.join('data/', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname).convert_alpha()
    return image


# Фон
bg = load_image("bg.png")
bg = pg.transform.scale(bg, (x_monitor, y_monitor))
rect = bg.get_rect()
rect.topleft = (0, 0)

objects = {
    'green_door': load_image('green_door.png'),
    'red_door': load_image('red_door.png'),
    'wall': load_image('wall.png'),
    'player': load_image('player.png'),
    'enemy': load_image('enemy.png'),
    'enemy2': load_image('enemy2.png'),
    'key': load_image('key.png'),
    'exit': load_image('exit.png')
}

max_len_x = 0
max_len_y = 0

SDVIG_X = 0
SDVIG_Y = 0


def generate_level(name):
    global max_len_x, max_len_y
    max_len_x = 0
    max_len_y = 0

    level = list()
    if os.path.isfile(f'data/' + name):
        with open(file=f'data/' + name) as r:
            lines = r.readlines()
        for i in lines:
            level.append(('').join(i.split()))
        del level[-2]

        max_len_y = len(level) * 50
        # Создание игрового поля
        for y in range(len(level)):
            for x in range(len(level[y])):
                if len(level[y]) > max_len_x:
                    max_len_x = len(level[y])
                    print(len(level[y]))
                if level[y][x] == 's':  # s - поверхность
                    continue
                elif level[y][x] == 'w':  # w - стена
                    Wall('wall', x, y)
                elif level[y][x] == 'G':  # G - зелёная дверь вертикальна
                    GreenV('green_door', x, y)
                elif level[y][x] == 'R':  # R - красная дверь вертикальна
                    RedV('red_door', x, y)
                elif level[y][x] == 'g':  # g - зелёная дверь горизонтальна
                    GreenH('green_door', x, y)
                elif level[y][x] == 'r':  # r - красная дверь горизонтальна
                    RedH('red_door', x, y)
                elif level[y][x] == 'E':  # E - Враг двигается по вертикали
                    EnemyV(x, y)
                elif level[y][x] == 'e':  # e - Враг двигается по горизонтали
                    EnemyH(x, y)
                elif level[y][x] == 'k':  # k - ключ, небходиммый для прохождения уровня
                    Key('key', x, y)
                elif level[y][x] == 'x':
                    Exit('exit', x, y)
                elif level[y][x] == 'P':
                    Player(x, y)  # сам игрок
        max_len_x = max_len_x * 50

        print(max_len_x, max_len_y)


# Ниже заполнение игрового поля спрайтами
class GreenV(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_green_doorV)
        self.image = objects[sprite_name]

        x = tile_width * pos_x
        y = tile_height * pos_y
        self.rect = self.image.get_rect().move(x, y)


class RedV(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_red_doorV)
        self.image = objects[sprite_name]
        x = tile_width * pos_x
        y = tile_height * pos_y
        self.rect = self.image.get_rect().move(x, y)


class GreenH(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_green_doorH)
        self.image = objects[sprite_name]
        self.image = pg.transform.rotate(self.image, 90)
        x = tile_width * pos_x
        y = tile_height * pos_y
        self.rect = self.image.get_rect().move(x, y)


class RedH(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_red_doorH)
        self.image = objects[sprite_name]
        self.image = pg.transform.rotate(self.image, 90)
        x = tile_width * pos_x
        y = tile_height * pos_y
        self.rect = self.image.get_rect().move(x, y)


class Wall(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(group_sprite_wall)
        self.image = objects[sprite_name]
        x = tile_width * pos_x
        y = tile_height * pos_y
        self.rect = self.image.get_rect().move(x, y)


class EnemyV(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(mobV)
        global dict_vector_enemyV, numV

        dict_vector_enemyV[numV] = 50
        numV += 1
        sprite_name = random.choice(['enemy', 'enemy2'])
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y
        )


class EnemyH(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(mobH)
        global dict_vector_enemyH, numH

        dict_vector_enemyH[numH] = 50
        numH += 1
        sprite_name = random.choice(['enemy', 'enemy2'])
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y
        )


class Key(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(gold_key)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y
        )


class Exit(pg.sprite.Sprite):
    def __init__(self, sprite_name, pos_x, pos_y):
        super().__init__(exit_doors)
        self.image = objects[sprite_name]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y
        )


class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player)
        self.x = int(x) * tile_width
        self.y = int(y) * tile_height
        self.image = load_image('player.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)


"""toto"""
lvl_chooise = input('Введите номер уровня: 1/2/3 и т.д.')
generate_level(f'lvl{lvl_chooise}.txt')


class Enemy_move:

    def vectorH_enemy(self):
        try:
            for numh, mh in enumerate(mobH):
                (x1h, y1h, x2h, y2h) = mh.rect
                mh.rect = (x1h + dict_vector_enemyH[numh], y1h, x2h, y2h)
                if (collisions_objectH[numh][0][0] < mh.rect[0] + mh.rect[2]) or \
                        (collisions_objectH[numh][1][1] > mh.rect[0]):
                    (x1h, y1h, x2h, y2h) = mh.rect
                    mh.rect = (x1h - dict_vector_enemyH[numh], y1h, x2h, y2h)
                    if dict_vector_enemyH[numh] > 0:
                        dict_vector_enemyH[numh] = -1
                        mh.image = pg.transform.flip(mh.image, True, False)
                    elif dict_vector_enemyH[numh] < 0:
                        dict_vector_enemyH[numh] = 1
                        mh.image = pg.transform.flip(mh.image, True, False)
        except:
            pass

    def vectorV_enemy(self):
        try:
            for numv, mv in enumerate(mobV):
                (x1v, y1v, x2v, y2v) = mv.rect
                mv.rect = (x1v, y1v + dict_vector_enemyV[numv], x2v, y2v)
                if (collisions_objectV[numv][0][0] < mv.rect[1] + mv.rect[3]) or \
                        (collisions_objectV[numv][1][1] > mv.rect[1]):

                    (x1h, y1h, x2h, y2h) = mv.rect
                    mv.rect = (x1h, y1h - dict_vector_enemyV[numv], x2h, y2h)
                    if dict_vector_enemyV[numv] > 0:
                        dict_vector_enemyV[numv] = -1
                        mobV.sprites()[numv].image = pg.transform.flip(mobV.sprites()[numv].image, True, False)


                    elif dict_vector_enemyV[numv] < 0:
                        dict_vector_enemyV[numv] = 1
                        mobV.sprites()[numv].image = pg.transform.flip(mobV.sprites()[numv].image, True, False)
        except:
            pass


class App:

    def __init__(self):
        super().__init__()
        global screen

        self.screen = screen
        self.is_run = False
        self.FPS = 59
        pg.init()
        self.clock = pg.time.Clock()
        self.direction = 0
        self.direction_flag = None

    def run(self):
        global bg, rect
        self.is_run = True

        ''' Открытие БД и проверка, на каком уровне игрок с последующей передачей в | generate_level() | имени уровня'''
        ####

        all_sprites.draw(self.screen)
        self.door_r = True  #
        self.door_g = True  #

        x, y = 0, 0  # Передвижение игрока

        while self.is_run:
            self.Enemy()
            keys = pg.key.get_pressed()

            for event in pg.event.get():

                if event.type == pg.QUIT:
                    self.is_run = False

            if keys[pg.K_UP] or keys[pg.K_w]:
                y = -2

            elif keys[pg.K_DOWN] or keys[pg.K_s]:
                y = 2

            if keys[pg.K_LEFT] or keys[pg.K_a]:
                x = -2

            elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                x = 2

            if keys[pg.K_r]:
                self.lvl_restart()

            self.Move_pl(x, y)
            x, y = 0, 0

            self.clock.tick(self.FPS)
            self.screen.fill('black')
            self.screen.blit(bg, rect.topleft)

            all_sprites.draw(self.screen)
            pg.display.flip()

        pg.quit()

    def Move_pl(self, x=0, y=0):
        global count_gold_key
        Camera()
        i = player.sprites()[0]

        """Для определения направления игрока"""
        if (x > 0 and self.direction_flag is False) or self.direction_flag is None:  # Работает
            player.sprites()[0].image = pg.transform.flip(player.sprites()[0].image, True, False)
            self.direction_flag = True

        elif (x < 0 and self.direction_flag is True) or self.direction_flag is None:  # Работает
            player.sprites()[0].image = pg.transform.flip(player.sprites()[0].image, True, False)
            self.direction_flag = False

        key_check = list((sprite for sprite in gold_key if pg.sprite.collide_mask(i, sprite)))
        if key_check:
            key_check[0].kill()
            count_gold_key += 1

        def check_wall_quater(condition=0):  # Работает
            quarter = None
            (x1, y1, x2, y2) = i.rect
            if condition == 1:
                quarter = quarter_1
            elif condition == 2:
                quarter = quarter_2
            elif condition == 3:
                quarter = quarter_3
            elif condition == 4:
                quarter = quarter_4
            elif condition == 5:
                quarter = quarter_5
            elif condition == 6:
                quarter = quarter_6
            elif condition == 7:
                quarter = quarter_7
            elif condition == 8:
                quarter = quarter_8
            elif condition == 9:
                quarter = quarter_9

            gen = list((sprite for sprite in quarter if pg.sprite.collide_mask(i, sprite)))
            try:
                gen = gen[0]
                if gen in redVH:
                    if self.door_r is True:
                        if gen in group_sprite_red_doorV:
                            self.collision_door_V(i, x, gen, param='red')

                        elif gen in group_sprite_red_doorH:
                            self.collision_door_H(i, y, gen, param='red')
                    else:
                        i.rect = (x1 - x, y1 - y, x2, y2)

                elif gen in greenVH:
                    if self.door_g is True:
                        if gen in group_sprite_green_doorV:
                            self.collision_door_V(i, x, gen, param='green')
                        elif gen in group_sprite_green_doorH:
                            self.collision_door_H(i, y, gen, param='green')
                    else:
                        i.rect = (x1 - x, y1 - y, x2, y2)

                elif gen in group_sprite_wall:
                    i.rect = (x1 - x, y1 - y, x2, y2)
                if gen in exit_doors:
                    print(len(gold_key), count_gold_key)
                    if len(gold_key) == 0:
                        print('Win')
                        self.lvl_restart()
                    else:
                        i.rect = (x1 - x, y1 - y, x2, y2)
            except:
                pass

        # Прибавляем координаты игрока
        (x1, y1, x2, y2) = i.rect
        i.rect = (x1 + x, y1 + y, x2, y2)
        ms_sdg_Y = SDVIG_Y
        ms_sdg_X = SDVIG_X
        if ms_sdg_Y > 0:
            ms_sdg_Y = -abs(ms_sdg_Y)
        if ms_sdg_Y < 0:
            ms_sdg_Y = abs(ms_sdg_Y)

        if ms_sdg_X > 0:
            ms_sdg_X = -abs(ms_sdg_X)
        if ms_sdg_X < 0:
            ms_sdg_X = abs(ms_sdg_X)

        x1 += ms_sdg_X + x
        y1 += ms_sdg_Y + y
        try:
            check_wall_quater(self.all_quarter_condition(x1=x1, y1=y1, x2=x2, y2=y2))
        except:
            print('За границей поля!')
            self.lvl_restart()

    def all_quarter_condition(self, x1=0, y1=0, x2=0, y2=0, sprite=None):
        """Деление экрана на 9 равных частей"""
        if ((0 <= x1 <= max_len_x / 3) or (0 <= x1 + x2 <= max_len_x / 3)) and (
                (0 <= y1 <= max_len_y / 3) or (0 <= y1 + y2 <= max_len_y / 3)):  # 1/9
            if sprite:
                quarter_1.add(sprite)
            else:
                return 1

        if ((max_len_x / 3 <= x1 <= max_len_x - max_len_x / 3) or (
                max_len_x / 3 <= x1 + x2 <= max_len_x - max_len_x / 3)) and (
                (0 <= y1 <= max_len_y / 3) or (0 <= y1 + y2 <= max_len_y / 3)):  # 2/9
            if sprite:
                quarter_2.add(sprite)
            else:
                return 2

        if ((max_len_x - max_len_x / 3 <= x1 <= max_len_x) or (max_len_x - max_len_x / 3 <= x1 + x2 <= max_len_x)) and (
                (0 <= y1 <= max_len_y / 3) or (0 <= y1 + y2 <= max_len_y / 3)):  # 3/9
            if sprite:
                quarter_3.add(sprite)
            else:
                return 3

        if ((0 <= x1 <= max_len_x / 3) or (0 <= x1 + x2 <= max_len_x / 3)) and (
                (max_len_y / 3 <= y1 <= max_len_y - max_len_y / 3) or (
                max_len_y / 3 <= y1 + y2 <= max_len_y - max_len_y / 3)):  # 4/9
            if sprite:
                quarter_4.add(sprite)
            else:
                return 4

        if ((max_len_x / 3 <= x1 <= max_len_x - max_len_x / 3) or (
                max_len_x / 3 <= x1 + x2 <= max_len_x - max_len_x / 3)) and (
                (max_len_y / 3 <= y1 <= max_len_y - max_len_y / 3) or (
                max_len_y / 3 <= y1 + y2 <= max_len_y - max_len_y / 3)):  # 5/9
            if sprite:
                quarter_5.add(sprite)
            else:
                return 5

        if ((max_len_x - max_len_x / 3 <= x1 <= max_len_x) or (max_len_x - max_len_x / 3 <= x1 + x2 <= max_len_x)) and \
                ((max_len_y / 3 <= y1 <= max_len_y - max_len_y / 3) or (
                        max_len_y / 3 <= y1 + y2 <= max_len_y - max_len_y / 3)):  # 6/9
            if sprite:
                quarter_6.add(sprite)
            else:
                return 6

        if ((0 <= x1 <= max_len_x / 3) or (0 <= x1 + x2 <= max_len_x / 3)) and (
                (max_len_y - max_len_y / 3 <= y1 <= max_len_y) or (
                max_len_y - max_len_y / 3 <= y1 + y2 <= max_len_y)):  # 7/9
            if sprite:
                quarter_7.add(sprite)
            else:
                return 7

        if ((max_len_x / 3 <= x1 <= max_len_x - max_len_x / 3) or (
                max_len_x / 3 <= x1 + x2 <= max_len_x - max_len_x / 3)) and (
                (max_len_y - max_len_y / 3 <= y1 <= max_len_y) or (
                max_len_y - max_len_y / 3 <= y1 + y2 <= max_len_y)):  # 8/9
            if sprite:
                quarter_8.add(sprite)
            else:
                return 8

        if ((max_len_x - max_len_x / 3 <= x1 <= max_len_x) or (max_len_x - max_len_x / 3 <= x1 + x2 <= max_len_x)) and (
                (max_len_y - max_len_y / 3 <= y1 <= max_len_y) or (
                max_len_y - max_len_y / 3 <= y1 + y2 <= max_len_y)):  # 9/9
            if sprite:
                quarter_9.add(sprite)
            else:
                return 9

    def lvl_restart(self):
        global SDVIG_X, SDVIG_Y, count_gold_key

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
        for i in all_obj:
            i.kill()

        """открытие бд для уровня"""
        generate_level(f'lvl{lvl_chooise}.txt')
        count_gold_key = 0

        all_sprites.add(group_sprite_wall, gold_key, exit_doors, player, mobH, mobV, group_sprite_green_doorV,
                        group_sprite_red_doorV,
                        group_sprite_green_doorH,
                        group_sprite_red_doorH)
        enemy.add(mobH, mobV)
        greenVH.add(group_sprite_green_doorV, group_sprite_green_doorH)
        redVH.add(group_sprite_red_doorV, group_sprite_red_doorH)
        all_obj.add(group_sprite_wall, greenVH, redVH, exit_doors)

        for sprite in all_obj:
            (x1, y1, x2, y2) = sprite.rect
            self.all_quarter_condition(x1, y1, x2, y2, sprite)

        for i in list_quarter:
            print(i)

        print('-' * 20)
        print(all_obj)
        print(mobV)
        print(mobH)

        all_sprites.draw(self.screen)
        self.door_r = True  # Красная, В какую дверь игрок может войти (по умолчанию в любую)
        self.door_g = True  # Зелёная, В какую дверь игрок может войти (по умолчанию в любую)
        self.direction_flag = None

        for _, key in enumerate(collisions_objectH):
            collis1, collis2 = collisions_objectH[key]

            collis1[0] -= SDVIG_X
            collis2[1] -= SDVIG_X

            collisions_objectH[key] = [collis1, collis2]

        for _, key in enumerate(collisions_objectV):
            collis1, collis2 = collisions_objectV[key]

            collis1[0] -= SDVIG_Y
            collis2[1] -= SDVIG_Y

            collisions_objectV[key] = [collis1, collis2]

        SDVIG_X = 0
        SDVIG_Y = 0
        dict_vector_enemyV.clear()
        dict_vector_enemyH.clear()

        for num1 in range(len(mobV)):
            dict_vector_enemyV[num1] = random.choice([-1, 1])

        for num2 in range(len(mobH)):
            x = random.choice([-1, 1])
            dict_vector_enemyH[num2] = x

            if x > 0:
                mobH.sprites()[num2].image = pg.transform.flip(mobH.sprites()[num2].image, True, False)

    def Enemy(self):
        if len(list((e for e in enemy if pg.sprite.collide_mask(player.sprites()[0], e)))) > 0:
            self.lvl_restart()
        else:
            Enemy_move().vectorH_enemy()
            Enemy_move().vectorV_enemy()

    def collision_door_H(self, i, y, sprite, param=None):

        if y < 0:
            if i.rect[1] + i.rect[3] - 7 < sprite.rect[1]:
                if param == 'green':
                    self.door_r = True
                    self.door_g = False

                elif param == 'red':
                    self.door_r = False
                    self.door_g = True

        if y > 0:
            if i.rect[1] + 4 > sprite.rect[1] + sprite.rect[3]:
                if param == 'green':
                    self.door_r = True
                    self.door_g = False

                elif param == 'red':
                    self.door_r = False
                    self.door_g = True

    def collision_door_V(self, i, x, sprite, param=None):
        if x > 0:
            if i.rect[0] + 5 > sprite.rect[0] + sprite.rect[2]:
                if param == 'green':
                    self.door_r = True
                    self.door_g = False

                elif param == 'red':
                    self.door_r = False
                    self.door_g = True


        elif x < 0:
            if i.rect[0] + i.rect[2] - 4 <= sprite.rect[0]:
                if param == 'green':
                    self.door_r = True
                    self.door_g = False

                elif param == 'red':
                    self.door_r = False
                    self.door_g = True


class Camera:

    def __init__(self):
        global SDVIG_X, SDVIG_Y, screen
        (x, y, x2, y2) = player.sprites()[0].rect

        self.screen = screen
        self.clock = pg.time.Clock()
        self.FPS = 59

        if x + x2 > WIDTH:
            self.move_left()

        elif x < 0:
            self.move_right()

        if y + y2 > HEIGHT:
            self.move_down()

        elif y < 0:
            self.move_up()

    def move_right(self):
        global SDVIG_X
        counter = 1000
        if x_monitor - counter < 0:
            counter += x_monitor - counter - 50

        counter_e = counter
        SDVIG_X += counter
        a = 0
        c = True

        def sdvig_enemy_r():
            for _, key in enumerate(collisions_objectH):
                collis1, collis2 = collisions_objectH[key]

                collis1[0] += counter_e
                collis2[1] += counter_e

                collisions_objectH[key] = [collis1, collis2]

        thr = Thread(target=sdvig_enemy_r())
        thr.start()
        thr.join()

        while c:
            a += 10
            for sprite in all_sprites:
                (x, y, x1, y1) = sprite.rect
                sprite.rect = (x + 10, y, x1, y1)

            screen.fill('black')
            self.screen.blit(bg, rect.topleft)
            all_sprites.draw(self.screen)
            pg.display.flip()
            self.clock.tick(self.FPS)

            if a == counter:
                c = False

    def move_left(self):
        global SDVIG_X
        counter = -1000
        if x_monitor + counter < 0:
            counter -= x_monitor + counter - 50

        counter_e = counter
        a = 0
        c = True
        SDVIG_X += counter

        def sdvig_enemy_l():
            for _, key in enumerate(collisions_objectH):
                collis1, collis2 = collisions_objectH[key]

                collis1[0] += counter_e
                collis2[1] += counter_e

                collisions_objectH[key] = [collis1, collis2]

        thr = Thread(target=sdvig_enemy_l())
        thr.start()
        thr.join()

        while c:
            a -= 10
            for sprite in all_sprites:
                (x, y, x1, y1) = sprite.rect
                sprite.rect = (x - 10, y, x1, y1)
            screen.fill('black')
            self.screen.blit(bg, rect.topleft)
            all_sprites.draw(self.screen)
            pg.display.flip()
            self.clock.tick(self.FPS)

            if a == counter:
                c = False

    def move_up(self):
        global SDVIG_Y
        counter = 1000
        if y_monitor - counter < 0:
            counter += y_monitor - counter - 50

        counter_e = counter
        a = 0
        c = True
        SDVIG_Y += counter

        def sdvig_enemy_up():
            for _, key in enumerate(collisions_objectV):
                collis1, collis2 = collisions_objectV[key]

                collis1[0] += counter_e
                collis2[1] += counter_e

                collisions_objectV[key] = [collis1, collis2]

        thr = Thread(sdvig_enemy_up())
        thr.start()
        thr.join()

        while c:
            a += 10
            for sprite in all_sprites:
                (x, y, x1, y1) = sprite.rect
                sprite.rect = (x, y + 10, x1, y1)
            screen.fill('black')
            self.screen.blit(bg, rect.topleft)
            all_sprites.draw(self.screen)
            pg.display.flip()
            self.clock.tick(self.FPS)

            if a == counter:
                c = False

    def move_down(self):
        global SDVIG_Y
        counter = -1000
        if y_monitor + counter < 0:
            counter -= x_monitor + counter - 50

        counter_e = counter
        a = 0
        c = True
        SDVIG_Y += counter

        def sdvig_enemy_d():
            for _, key in enumerate(collisions_objectV):
                collis1, collis2 = collisions_objectV[key]

                collis1[0] += counter_e
                collis2[1] += counter_e

                collisions_objectV[key] = [collis1, collis2]

        thr = Thread(target=sdvig_enemy_d())
        thr.start()
        thr.join()

        while c:
            a -= 10
            for sprite in all_sprites:
                (x, y, x1, y1) = sprite.rect
                sprite.rect = (x, y - 10, x1, y1)
            screen.fill('black')
            self.screen.blit(bg, rect.topleft)
            all_sprites.draw(self.screen)
            pg.display.flip()
            self.clock.tick(self.FPS)

            if a == counter:
                c = False


greenVH.add(group_sprite_green_doorH, group_sprite_green_doorV)
redVH.add(group_sprite_red_doorV, group_sprite_red_doorH)
all_obj.add(group_sprite_wall, redVH, greenVH)

"""Два класса <<Enemy_dubler>> и <<A>> созданы для оптимизации уровня с врагами"""


class Enemy_dubler:

    def vectorH_enemy(self):
        for numh, mh in enumerate(mobH):
            if (numh not in collisions_objectH) or (len(collisions_objectH[numh]) != 2):
                (x1h, y1h, x2h, y2h) = mh.rect
                mh.rect = (x1h + dict_vector_enemyH[numh], y1h, x2h, y2h)

                gen = list((j for j in all_obj if pg.sprite.collide_mask(mh, j)))

                if len(gen) > 0:
                    (x1h, y1h, x2h, y2h) = mh.rect
                    mh.rect = (x1h - dict_vector_enemyH[numh], y1h, x2h, y2h)
                    if dict_vector_enemyH[numh] > 0:
                        dict_vector_enemyH[numh] = -50
                    elif dict_vector_enemyH[numh] < 0:
                        dict_vector_enemyH[numh] = 50
                    return [gen[0], numh]

    def vectorV_enemy(self):

        for numv, mv in enumerate(mobV):
            if (numv not in collisions_objectV) or len(collisions_objectV[numv]) != 2:
                (x1v, y1v, x2v, y2v) = mv.rect
                mv.rect = (x1v, y1v + dict_vector_enemyV[numv], x2v, y2v)
                gen = list((j for j in all_obj if pg.sprite.collide_mask(mv, j)))

                if len(gen) > 0:
                    (x1v, y1v, x2v, y2v) = mv.rect
                    mv.rect = (x1v, y1v - dict_vector_enemyV[numv], x2v, y2v)
                    if dict_vector_enemyV[numv] > 0:
                        dict_vector_enemyV[numv] = -50

                    elif dict_vector_enemyV[numv] < 0:
                        dict_vector_enemyV[numv] = 50

                    return [gen[0], numv]


class A:
    def __init__(self, V=False, H=False):

        if V:
            initV = Enemy_dubler()

            cV = True
            spV = []
            CONSTV = len(dict_vector_enemyV)
            print(len(spV), CONSTV)
            while cV:
                V = initV.vectorV_enemy()

                if V != None:
                    collisionV = V[0]
                    if V[1] not in collisions_objectV:
                        collisions_objectV[V[1]] = [[collisionV.rect[1], collisionV.rect[1] + collisionV.rect[3]]]
                    elif V[1] in collisions_objectV:
                        aV = collisions_objectV[V[1]]
                        if (aV[0][0] != collisionV.rect[1] and aV[0][1] != collisionV.rect[1] + collisionV.rect[3]) \
                                and (len(collisions_objectV[V[1]]) < 3):
                            aV = [aV[0], [collisionV.rect[1], collisionV.rect[1] + collisionV.rect[3]]]
                            collisions_objectV[V[1]] = aV

                    for i in collisions_objectV:

                        if len(collisions_objectV[i]) == 2 and i not in spV:
                            spV.append(i)

                        if len(spV) == CONSTV:
                            cV = False
                            break
        if H:
            initH = Enemy_dubler()

            cH = True
            spH = []
            CONSTH = len(dict_vector_enemyH)

            while cH:
                H = initH.vectorH_enemy()
                if H != None:
                    collisionH = H[0]
                    if H[1] not in collisions_objectH:
                        collisions_objectH[H[1]] = [[collisionH.rect[0], collisionH.rect[0] + collisionH.rect[2]]]
                    elif H[1] in collisions_objectH:
                        aH = collisions_objectH[H[1]]
                        if (aH[0][0] != collisionH.rect[0] and aH[0][1] != collisionH.rect[0] + collisionH.rect[2]) \
                                and (len(collisions_objectH[H[1]]) < 3):
                            aH = [aH[0], [collisionH.rect[0], collisionH.rect[0] + collisionH.rect[2]]]

                            collisions_objectH[H[1]] = aH

                    for i in collisions_objectH:

                        if len(collisions_objectH[i]) == 2 and i not in spH:
                            spH.append(i)

                        if len(spH) == CONSTH:
                            sorted(collisions_objectH)
                            cH = False
                            break


def miscalculation():
    thr1 = Thread(target=A, args=(False, True))
    thr2 = Thread(target=A, args=(True, False))

    thr1.start()
    thr2.start()

    thr1.join()
    thr2.join()


def main():
    if mobH or mobV:
        miscalculation()

    print(0, max_len_x / 3, max_len_x - max_len_x / 3, max_len_x)
    print(0, max_len_y / 3, max_len_y - max_len_y / 3, max_len_y)

    app = App()
    app.lvl_restart()
    app.run()


if __name__ == '__main__':
    main()
