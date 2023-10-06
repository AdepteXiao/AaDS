import argparse
import os
import imageio
import sys
from math import ceil
from random import randrange, choice, sample
from typing import List
import constants as c
import pygame as pg
from PIL import Image


class Cell:
    tile_stat_col = {
        "wall": c.BLUE,
        "unchecked": c.WHITE,
        "way": c.RED,
        "checked": c.GREEN
    }

    def __init__(self, surface, x, y, c_type):
        """
        Класс клетки лабиринта
        :param surface: окно pygame
        :param x: координата х
        :param y: координата у
        :param c_type: тип клетки
        """
        self.x = x
        self.y = y
        self.surf = surface
        self.c_type = c_type
        self.status = 'unchecked'
        self.rect = pg.Rect(
            self.x * c.CELL_SIZE,
            self.y * c.CELL_SIZE,
            c.CELL_SIZE,
            c.CELL_SIZE
        )
        self.children = []
        self.parent = None

    def render(self):
        """
        Метод отрисовки клетки лабиринта
        """
        pg.draw.rect(self.surf, Cell.tile_stat_col[self.c_type], self.rect)

    def __repr__(self):
        wall_type = "maze_wall" if self.x == c.WIDTH or \
                                   self.y == c.HEIGHT or \
                                   self.x == 0 or \
                                   self.y == 0 else "wall"
        return f"Cell({self.x}, {self.y}, " \
               f"{wall_type if self.c_type == 'wall' else self.c_type})"


class Map:

    def __init__(self, surface: pg.Surface, clock: pg.time.Clock, width,
                 height):
        """
        Класс лабиринта
        :param surface: окно pygame
        :param clock:
        :param width: ширина лабиринта
        :param height: высота лабиринта
        """
        self.width = width
        self.height = height
        self.cells = []
        self.surface = surface
        self.gen_space()
        self.clock = clock

    def gen_space(self):
        """
        Метод отрисовки поля и создания массива клеток лабиринта
        """
        for y in range(0, self.height):
            line = []
            for x in range(0, self.width):
                if x == 0 or y == 0 or x == self.width - 1 or \
                        y == self.height - 1:
                    line.append(Cell(self.surface, x, y, "wall"))
                else:
                    line.append(Cell(self.surface, x, y, "unchecked"))
            self.cells.append(line)

    def dividing(self):
        """
        Метод создания лабиринта
        """

        def divide_cur(m_rect):
            """
            Метод создания области лабиринта
            :param m_rect: размер и координаты поля
            """
            if m_rect.w <= 3 or m_rect.h <= 3:
                return
            x2 = m_rect.x + m_rect.w
            y2 = m_rect.y + m_rect.h
            wall_x = randrange(m_rect.x + 2, x2 - 1, 2)
            wall_y = randrange(m_rect.y + 2, y2 - 1, 2)

            top, bot, left, right = [], [], [], []
            for y in range(m_rect.y + 1, y2):
                for x in range(m_rect.x + 1, x2):
                    if x == wall_x or y == wall_y:
                        self.cells[y][x].c_type = "wall"
                        if c.IS_REALTIME:
                            self.render()
                            if c.IS_GIF is True:
                                self.save_for_gif()
                                print('сохранение')
                        if x < wall_x:
                            left.append(self.cells[y][x])
                        elif x > wall_x:
                            right.append(self.cells[y][x])
                        elif y < wall_y:
                            top.append(self.cells[y][x])
                        elif y > wall_y:
                            bot.append(self.cells[y][x])

            # if holes is not None:
            #     for cell in holes:
            #         if cell.x == wall_x or cell.y == wall_y:
            #             list_of_statements = [
            #                 self.cells[cell.y + 1][
            #                     cell.x].c_type == 'wall',
            #                 self.cells[cell.y - 1][
            #                     cell.x].c_type == 'wall',
            #                 self.cells[cell.y][
            #                     cell.x + 1].c_type == 'wall',
            #                 self.cells[cell.y][
            #                     cell.x - 1].c_type == 'wall']
            #             mirror = [self.cells[cell.y - 1][cell.x],
            #                       self.cells[cell.y + 1][cell.x],
            #                       self.cells[cell.y][cell.x - 1],
            #                       self.cells[cell.y][cell.x + 1]]
            #             if sum(list_of_statements) == 3:
            #                 for i, state in enumerate(list_of_statements):
            #                     if not state:
            #                         mirror[i].c_type = 'way'
            #                         print(f'done: {mirror[i]}')
            #                         break
            #             if sum(list_of_statements) == 4:
            #                 print(f'Чета тут херня какая то: {cell}')

            to_hole = sample([top, bot, left, right], k=3)
            for wall in to_hole:
                hole = choice([cell for cell in wall
                               if not (cell.x % 2 == 0 and cell.y % 2 == 0)])
                hole.c_type = "unchecked"
                if c.IS_REALTIME:
                    self.render()
                    if c.IS_GIF is True:
                        self.save_for_gif()

            top_left = pg.Rect(
                m_rect.x,
                m_rect.y,
                wall_x - m_rect.x,
                wall_y - m_rect.y
            )
            top_right = pg.Rect(
                wall_x,
                m_rect.y,
                m_rect.w - top_left.w,
                top_left.h
            )
            bot_left = pg.Rect(
                m_rect.x,
                m_rect.y + top_left.h,
                top_left.w,
                m_rect.h - top_left.h
            )
            bot_right = pg.Rect(
                wall_x,
                wall_y,
                top_right.w,
                bot_left.h
            )

            for cur_rect in [top_left, top_right, bot_left, bot_right]:
                divide_cur(cur_rect)

        divide_cur(pg.Rect(0, 0, self.width - 1, self.height - 1))

    def find_way(self, start_cell: Cell, end_cell: Cell):
        """
        Поиск пути при помощи обхода в ширину
        :param start_cell: начальная клетка
        :param end_cell: конечная клетка
        """

        def find_neighbours(cell: Cell) -> List[Cell]:
            """
            Метод поиска соседних свободных клеток
            :param cell: клетка
            :return: список соседей
            """
            neighbours = [
                self.cells[cell.y][cell.x - 1],
                self.cells[cell.y][cell.x + 1],
                self.cells[cell.y - 1][cell.x],
                self.cells[cell.y + 1][cell.x]
            ]
            return [tile for tile in neighbours if tile.c_type != "wall"]

        # print(f"Ищем путь из {start_cell} в {end_cell}")
        depth = 1
        marked = {depth: [start_cell]}
        while end_cell.parent is None:
            marked[depth + 1] = []
            for cur_cell in marked[depth]:
                neighb = find_neighbours(cur_cell)
                cur_cell.children = neighb
                for ne in neighb:
                    if ne.parent is None:
                        ne.parent = cur_cell
                        if ne.c_type == "unchecked":
                            ne.c_type = "checked"
                        marked[depth + 1].append(ne)
            depth += 1
            self.render()
            if c.IS_GIF is True:
                self.save_for_gif()

        cur_cell = end_cell
        while cur_cell != start_cell:
            cur_cell.parent.c_type = "way"
            cur_cell = cur_cell.parent
            self.render()
            if c.IS_GIF is True:
                self.save_for_gif()

    def render(self):
        """
        Метод вывода лабиринта на экран
        """
        for line in self.cells:
            for cell in line:
                cell.render()
        pg.display.flip()
        self.clock.tick()

    def reset(self):
        """
        Пересоздание лабиринта
        """
        self.cells.clear()
        self.gen_space()
        self.dividing()

    def reset_ways(self):
        """
        Сброс отрисованных путей
        """
        for line in self.cells:
            for cell in line:
                cell.children.clear()
                cell.parent = None
                if cell.c_type == "way" or cell.c_type == "checked":
                    cell.c_type = "unchecked"

    def save_to_img(self, filepath=None):
        """
        Сохранение в картинку
        :param filepath: путь для сохранения
        """
        if filepath is None:
            i = 1
            while True:
                new_filepath = f"./results/image{i}.png"
                if not os.path.exists(new_filepath):
                    filepath = new_filepath
                    break
                i += 1
        pg.image.save(self.surface, filepath)

    def save_to_txt(self, filepath=None):
        """
        Сохранение в текстовый файл
        :param filepath: путь к файлу
        """
        if filepath is None:
            i = 1
            while True:
                new_filepath = f"./results/text_maze_{i}.txt"
                if not os.path.exists(new_filepath):
                    filepath = new_filepath
                    break
                i += 1
        with open(filepath, "w", encoding='utf-8') as file:
            for line in self.cells:
                for cell in line:
                    if cell.c_type == "wall":
                        file.write("▓▓")
                    if cell.c_type == "unchecked":
                        file.write("  ")
                file.write('\n')

    def generate_from_txt(self, filepath):
        """
        Генерация лабиринта из txt
        :param filepath: путь до файла
        """
        with open(filepath, "r", encoding='utf-8') as file:
            length = max(c.HEIGHT, c.WIDTH)
            c.CELL_SIZE = length // len(file.readline().strip())
            for y, line in enumerate(file):
                for x, cell in enumerate(line[:-1:2]):
                    if cell == "▓":
                        self.cells[y][x].c_type = "wall"
                    if cell == " ":
                        self.cells[y][x].c_type = "unchecked"

    def generate_from_png(self, image):
        """
        Генерация из картинки
        :param image: изображение
        """
        for y in range(0, image.height - 1):
            for x in range(0, image.width - 1):
                r, g, b = image.getpixel((x, y))
                if 127 < r <= 255 and 127 < g <= 255 and 127 < b <= 255:
                    self.cells[y][x].c_type = "unchecked"
                else:
                    self.cells[y][x].c_type = "wall"

    def save_for_gif(self):
        filepath = f'./gif_images/image{c.IMAGES_COUNT}.png'
        # img_pil = Image.fromarray(pg.surfarray.array2d(
        #     self.surface))
        # print('saving')
        # img_pil.save(filepath)
        pg.image.save(self.surface, filepath)
        c.IMAGES_FOR_GIF.append(filepath)
        c.IMAGES_COUNT += 1


def main():
    """
    Точка входа
    """
    parser = argparse.ArgumentParser(description='Построение лабиринта')
    parser.add_argument('-W', '--width', type=int,
                        default=None,
                        help='Ширина изображения')
    parser.add_argument('-H', '--height', type=int,
                        default=None,
                        help='Высота изображения')
    parser.add_argument('-cs', '--cell_size', type=int,
                        default=None,
                        help='Размер клетки лабиринта')
    parser.add_argument('-i', '--input_path', type=str,
                        help='Путь для загрузки лабиринта')
    parser.add_argument('-o', '--output_path', type=str,
                        help='Путь для сохранения лабиринта')
    parser.add_argument('-gf', '--make_gif', type=bool,
                        default=False,
                        help='Путь для сохранения лабиринта')

    args = parser.parse_args()
    if args.input_path is not None and not os.path.isfile(args.input_path):
        print(f"Файл не найден: {args.input_path}")
        sys.exit()

    in_file_type = ''
    out_file_type = ''

    if args.input_path:
        if args.input_path.endswith(".txt"):
            in_file_type = "txt"
        elif args.input_path.endswith(".png"):
            in_file_type = "png"
        else:
            print(f"Невозможно прочитать из файла {args.input_path}")
            sys.exit()

    if args.output_path:
        if args.output_path.endswith(".txt"):
            out_file_type = "txt"
        elif args.output_path.endswith(".png"):
            out_file_type = "png"
        else:
            print(f'Невозможно сохранить в файл {args.output_path}')
            sys.exit()

    c.WIDTH, c.HEIGHT = (args.width, args.height) \
        if args.width is not None and args.height is not None \
        else (c.WIDTH, c.HEIGHT)
    c.CELL_SIZE = args.cell_size if args.cell_size is not None else c.CELL_SIZE

    pg.init()
    to_way = []
    clock = pg.time.Clock()

    if in_file_type == 'txt':
        screen = pg.display.set_mode((c.WIDTH, c.HEIGHT))
        m_w, m_h = ceil(c.WIDTH / c.CELL_SIZE), ceil(c.HEIGHT / c.CELL_SIZE)
        tile_map = Map(screen, clock, m_w, m_h)
        tile_map.generate_from_txt(args.input_path)

    elif in_file_type == 'png':
        image = Image.open(args.input_path)
        c.CELL_SIZE = 1
        c.WIDTH, c.HEIGHT = image.size
        screen = pg.display.set_mode((c.WIDTH, c.HEIGHT))
        m_w, m_h = ceil(c.WIDTH / c.CELL_SIZE), ceil(c.HEIGHT / c.CELL_SIZE)
        tile_map = Map(screen, clock, m_w, m_h)
        tile_map.generate_from_png(image)

    else:
        screen = pg.display.set_mode((c.WIDTH, c.HEIGHT))
        m_w, m_h = ceil(c.WIDTH / c.CELL_SIZE), ceil(c.HEIGHT / c.CELL_SIZE)
        tile_map = Map(screen, clock, m_w, m_h)
        tile_map.dividing()

    tile_map.render()
    pg.display.flip()

    if out_file_type == 'txt':
        tile_map.save_to_txt(args.output_path)
    elif out_file_type == 'png':
        tile_map.save_to_img(args.output_path)

    way_found = False
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                if c.IS_GIF is True:
                    images = [Image.open(file) for file in c.IMAGES_FOR_GIF]
                    images[0].save('animated.gif',
                                   save_all=True,
                                   append_images=images[1:],
                                   duration=50,
                                   loop=0)
                exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg.mouse.get_pos()
                tile_x, tile_y = x // c.CELL_SIZE, y // c.CELL_SIZE
                cell = tile_map.cells[tile_y][tile_x]
                if way_found:
                    tile_map.reset_ways()
                    way_found = False
                if cell.c_type == "unchecked":
                    cell.c_type = "way"
                    to_way.append(cell)
                    if len(to_way) == 2:
                        tile_map.find_way(*to_way)
                        to_way.clear()
                        way_found = True
                elif cell.c_type == "way":
                    cell.c_type = "unchecked"
                    to_way.remove(cell)

        tile_map.render()


if __name__ == '__main__':
    main()
