"""lab0 Вариант 5 Демёхина Арина Руслановна КИ21-17/1Б"""
from sys import exit as sys_exit

import pygame
import numpy as np
from numba import njit

FPS = 15  # Количество кадров в сек для основного цикла

W = 1000  # Ширина окна
H = 480  # Высота окна
menu_size = (W // 5, H)  # Размер Surface с текстом
frac_size = (W - menu_size[0], H)  # Размер Surface с фракталом

off_x, off_y = 0, 0  # Переменные сдвига фрактала
SCALE = 2  # Изначальный размер изображения
ITERATORS = 100  # Изначальное количество итераций

comp_c = complex(-0.745, -0.1)  # Изначальная формула c для z = z^2 + c

pygame.init()


def make_renders(surface: pygame.Surface, text: str, color: tuple, pos: tuple) -> None:
    """
    Функция отрисовки текста построчно
    :param surface: Surface на который отрисовываем текст
    :param text: Сам текст
    :param color: Цвет текста
    :param pos: Позиция текста на Surface
    """
    for x_iter, line in enumerate(text.split("\n")):
        surface.blit(font.render(line, True, color), (pos[0], pos[1] + x_iter * F_SIZE))


sc = pygame.display.set_mode((W, H))
fract_surface = pygame.Surface(frac_size)
another_subway_surface = pygame.Surface(menu_size)

F_SIZE = 20
font = pygame.font.SysFont("serif", F_SIZE)
pygame.display.set_caption("Множества Жюлиа")


@njit(fastmath=True)
def get_points(complex_c: complex, sc_ale: float,
               offset_x: float, offset_y: float,
               res=np.full(frac_size + (3,), [0, 0, 0]),
               n_iter=100) -> np.array:
    """
    Функция получения точек раскрашенных, согласно скорости удаления от отрезка [-2, 2]

    :param complex_c: Комплексное число прибавляемое к числу z любой точки
    :param sc_ale: Мера приближения фрактала
    :param offset_x: На сколько пикселей фрактал будет сдвинут по оси X
    :param offset_y: На сколько пикселей фрактал будет сдвинут по оси Y
    :param res: np.array() заполненный точками с черным цветом
    :param n_iter: Количество итераций каждой точки
    :return: np.array() с раскрашенными точками, согласно скорости удаления от отрезка [-2, 2]
    """
    y_p = frac_size[1] // 2
    x_p = frac_size[0] // 2
    # O(x_p, y_p, n_iter) = 2 * x_p * 2 * y_p
    for coord_y in range(-y_p, y_p):
        for coord_x in range(-x_p, x_p):
            real_n = coord_x / x_p * sc_ale + offset_x / x_p
            image_n = coord_y / y_p * sc_ale + offset_y / y_p
            func_z = real_n + 1j * image_n
            iter_n = 0
            for iter_n in range(n_iter):
                func_z = func_z ** 2 + complex_c
                if func_z.real ** 2 + func_z.imag ** 2 > 4:
                    break

            if iter_n == n_iter - 1:
                red_c = green_c = blue_c = 0
            else:
                red_c = (iter_n % 10) * 32 + 128
                green_c = (iter_n % 10) * 64
                blue_c = (iter_n % 10) * 16 + 128
            res[coord_x + x_p, coord_y + y_p] = np.array((red_c, green_c, blue_c))
    return res


def draw_surfs() -> None:
    """
    Функция отрисовки Surface с фракталом и Surface с пояснительным текстом
    """
    pygame.surfarray.blit_array(fract_surface, get_points(comp_c, SCALE,
                                                          off_x, off_y, n_iter=ITERATORS))
    pygame.Surface.blit(sc, fract_surface, (0, 0))
    another_subway_surface.fill((0, 255, 0))
    make_renders(another_subway_surface,
                 f"""SIZE: {1 / SCALE:.3f}
ITERATIONS:{ITERATORS}
OFFSET X:{off_x:.3f}
OFFSET Y:{off_y:.3f}
C ={comp_c.real:.3f} {"-" if comp_c.imag < 0 else "+"} {abs(comp_c.imag):.3f}i 

ARROWS - MOVE
W - SIZE ↓
S - SIZE ↑
E - ITERATIONS ↑
D - ITERATIONS ↓
Z - REAL INC
X - REAL DEC
C - IMAG INC
V - IMAG DEC

R - RESET
""",
                 (0, 0, 0),
                 (10, 10))
    pygame.Surface.blit(sc, another_subway_surface, (frac_size[0], 0))


clock = pygame.time.Clock()
draw_surfs()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys_exit()
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:  # Приведения фрактала к изначальному виду
                comp_c = complex(-0.745, -0.1)
                off_x, off_y = 0, 0
                SCALE = 2
                ITERATORS = 100

            if event.key == pygame.K_UP:  # Смещение камеры по оси Y вверх
                off_y -= 50 * SCALE
            if event.key == pygame.K_DOWN:  # Смещение камеры по оси Y вниз
                off_y += 50 * SCALE

            if event.key == pygame.K_LEFT:  # Смещение камеры по оси X вверх
                off_x -= 50 * SCALE
            if event.key == pygame.K_RIGHT:  # Смещение камеры по оси X вниз
                off_x += 50 * SCALE

            if event.key == pygame.K_w:  # Отдаление камеры
                if SCALE * 2 <= 2:
                    SCALE *= 2
            if event.key == pygame.K_s:  # Приближение камеры
                SCALE /= 2

            if event.key == pygame.K_e:  # Увеличение кол-ва итерация
                ITERATORS += 10
            if event.key == pygame.K_d:  # Уменьшение кол-ва итераций
                ITERATORS -= 10

            if event.key == pygame.K_z:  # Прибавление реальной части c
                comp_c = complex(comp_c.real + 0.005, comp_c.imag)
            if event.key == pygame.K_x:  # Уменьшение реальной части comp_c
                comp_c = complex(comp_c.real - 0.005, comp_c.imag)
            if event.key == pygame.K_c:  # Прибавление мнимой части comp_c
                comp_c = complex(comp_c.real, comp_c.imag + 0.005)
            if event.key == pygame.K_v:  # Уменьшение мнимой части c
                comp_c = complex(comp_c.real, comp_c.imag - 0.005)

            draw_surfs()

    pygame.display.update()
    clock.tick(FPS)
