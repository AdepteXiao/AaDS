import argparse
from random import shuffle
import pygame as pg
from math import ceil, log2
from typing import Optional, Callable
from my_sort import my_sort as ms

from functools import wraps
from time import time


def timing(f: Callable):
    """
    Декоратор для засечения времени выполнения отрисовки
    @param f: функция, время которой засекаем
    """

    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(
            f'func: {f.__name__} len: {len(args[0])} '
            f'time: {te - ts:2.4f} sec')
        return result

    return wrap


def draw_sort(array: list, reverse: Optional[bool] = False):
    """
    Функция отрисовки процесса сортировки
    @param array: сортируемый список
    @param reverse: флаг определяющий вариант сортировки, True по убыванию, False по возрастанию
    """
    pg.init()
    width, height = 800, 600
    screen = pg.display.set_mode((width, height))
    pg.display.set_caption("IntroSort visualize")

    ar_len = len(array)
    last_index = ar_len - 1
    max_element = max(array)

    if ar_len <= 100:
        tick = 20
    else:
        tick = 1

    def draw_array_col(red: int, grinefiy=False):
        """
        Отрисовка нового состояния массива
        @param red: текущее положение изменяемого элемента
        @param grinefiy: нужно ли нам отрисовывать отсортированный массив
        """
        norm_x = width / ar_len
        norm_w = norm_x if norm_x > 1 else 1
        screen.fill((0, 0, 0))
        h_caf = (height - 100) / max_element

        for index, value in enumerate(array):

            norm_h = value * h_caf
            norm_y = height - norm_h

            if index != red or value == max_element:
                cur_color = (255, 255, 255)
            else:
                cur_color = (255, 0, 0)

            if grinefiy:
                if index <= red:
                    cur_color = (0, 255, 0)

            pg.draw.rect(screen, cur_color, (ceil(norm_x * index), norm_y, ceil(norm_w), norm_h))

        pg.display.update()
        pg.time.wait(tick)

    @timing
    def my_sort(array_to_sort: list):
        """
        Алгоритм сортировки
        :param array_to_sort: сортируемый список
        """
        key = lambda x: x
        cmp = lambda x, y: x < y

        def intro_sort(begin=0, end=None, depth=0):
            """
            Интроспективная сортировка
            :param begin: начальный элемент
            :param end: конечный элемент
            :param depth: глубина рекурсии
            :return: отсортированный список
            """
            def heap_sort(heap, start, stop):
                """
                Сортировка кучами (пирамидальная сортировка)
                :param heap: Сортируемый список
                :param start:
                :param stop:
                :return: отсортированный список
                """
                last_heap_index = len(heap) - 1

                def percolate_down(idx, max_idx=None):
                    """
                    Сравнение корня и вытекающих из него элементов
                    :param idx: текущий индекс
                    :param max_idx: максимальный индекс, учавствующий в сравнении
                    """
                    if max_idx is None:
                        max_idx = last_heap_index
                    while idx < max_idx:
                        largest_idx = idx
                        left = 2 * idx + 1
                        right = 2 * idx + 2

                        if left <= max_idx and (reverse == cmp(key(heap[left]),
                                                               key(heap[largest_idx]))):
                            largest_idx = left
                        if right <= max_idx and (reverse == cmp(key(heap[right]),
                                                                key(heap[largest_idx]))):
                            largest_idx = right

                        if largest_idx != idx:
                            heap[idx], heap[largest_idx] = heap[largest_idx], heap[idx]
                            array[start:stop] = heap
                            draw_array_col(start + idx)
                            idx = largest_idx
                        else:
                            break

                for index in range(last_heap_index // 2, -1, -1):
                    percolate_down(index)

                for index in range(last_heap_index, 0, -1):
                    heap[0], heap[index] = heap[index], heap[0]

                    percolate_down(0, index - 1)
                return heap

            def partition():
                """
                Алгоритм быстрой сортировки
                :return: сортированный список
                """
                pivot_idx = begin
                pivot = array[pivot_idx]

                array[end], array[pivot_idx] = array[pivot_idx], array[end]
                first_larger = begin
                for idx in range(begin, end):
                    if reverse != cmp(key(array[idx]), key(pivot)):
                        array[idx], array[first_larger] = array[first_larger], array[idx]
                        draw_array_col(begin + idx)
                        first_larger += 1

                array[end], array[first_larger] = array[first_larger], array[end]
                draw_array_col(begin)
                return first_larger

            if end is None:
                end = last_index
            if ar_len != 0:
                if depth < log2(ar_len):
                    if begin < end:
                        mid = partition()
                        intro_sort(begin, mid - 1, depth + 1)
                        intro_sort(mid + 1, end, depth + 1)
                else:
                    array[begin:end + 1] = heap_sort(array[begin:end + 1], begin, end + 1)
                draw_array_col(begin)
            else:
                return array

        intro_sort()

        for i in range(len(array)):
            draw_array_col(i, grinefiy=True)

        return array_to_sort

    my_sort(array)
    run = True
    while run:
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                run = False


def main():
    """
    Точка входа из для CLI
    """
    parser = argparse.ArgumentParser(description="Сортировка методом слияния")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--array", "-a", dest="array", type=int, nargs="+",
                       help="Список чисел через пробел")
    group.add_argument("--file_path", "-fp", dest="file_path",
                       help="Путь к файлу с числами расположенными через пробел")
    group.add_argument("--randomized_array", "-ra", dest="ra_len", type=int,
                       help="Длина для создания рандомного массива")
    parser.add_argument("--reverse", "-r", dest="reverse",
                        action=argparse.BooleanOptionalAction,
                        help="Если указано - сортирует по невозрастанию")
    parser.add_argument("--visualize", "-v", dest="visualize",
                        action=argparse.BooleanOptionalAction,
                        help="визуализация сортировки")
    args = parser.parse_args()

    res = {"array": None,
           "reverse": False}

    if args.array:
        res["array"] = args.array
    elif args.file_path:
        with open(args.file_path, "r") as file:
            res["array"] = list(map(lambda x: int(x.replace("\n", "")), file.readlines()))
    elif args.ra_len:
        tmp = [i for i in range(1, args.ra_len + 1)]
        shuffle(tmp)
        res["array"] = tmp

    if args.reverse:
        res["reverse"] = args.reverse

    if args.visualize:
        draw_sort(**res)
    else:
        print(ms(**res))


if __name__ == '__main__':
    # arr_to_s = [i for i in range(1, 1000)]
    # shuffle(arr_to_s)
    # draw_sort(arr_to_s, reverse=True)
    main()
