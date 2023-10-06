"""
Модуль командного интерфейса функции search
"""

import argparse
from typing import Optional

from search import search


class ColoredChar:
    """
    Класс символа, поддерживающего раскраску
    """
    def __init__(self, char: str):
        """
        Конструктор класса раскрашенного символа
        :param char: символ, поддерживающий раскраску
        """
        self.char = char
        self.color = 0

    def __str__(self):
        """
        Строка, содержащая символ и ANSI последовательность с указанием цвета
        """
        return f"\033[{self.color};{30 if self.color else 0}m" \
               f"{self.char}\033[0;0m"


def paint_string(string: str, subs: Optional[dict[str, tuple[int, int, int]]]):
    """
    Фнкция раскраски строки, согласно переданным подстрокам
    :param string: строка, которую раскрашиваем
    :param subs: подстроки, согласно которым производим раскраску
    :return: раскрашенная строка
    """
    colors = [101, 103, 102, 104, 106, 105]
    if subs is None:
        return string
    sorted_subs = sorted(list(subs.items()), key=lambda x: len(x[0]),
                         reverse=True)
    painted_string = [ColoredChar(char) for char in string]
    for i, sub in enumerate(sorted_subs):
        sub, indexes = sub
        if indexes is None:
            continue
        color = colors[i]
        for index in indexes:
            for j in range(index, index + len(sub)):
                painted_string[j].color = color

    return "".join(map(str, painted_string))


def main():
    """
    Точка входа для CLI
    """
    parser = argparse.ArgumentParser(
        description="реализация алгоритма Кнута-Морриса_Пратта")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--string", "-s", dest="string",
                       type=str, help="Строка для поиска подстроки")
    group.add_argument("--file_path", "-fp", dest="path",
                       type=str, help="Файл для поиска подстроки")

    parser.add_argument("--sub_string", "-ss", dest="sub_string",
                        type=str, nargs="+",
                        help="Искомая подстрока")
    parser.add_argument("--case_sensitivity",
                        action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Чувствительность к регистру")
    parser.add_argument("--method", "-m", dest="method",
                        type=str, default="first",
                        help="Метод обхода строки - с начала или конца")
    parser.add_argument("--count", "-c", dest="count",
                        type=int, default=None,
                        help="Количество вхождений")

    args = parser.parse_args()
    if (args.path is None and args.string is None) or args.sub_string is None:
        raise parser.error("Строка и/или подстрока не указаны")
    if len(args.sub_string) > 6:
        raise parser.error("Количество подстрок не может превышать 6")

    if args.path is not None:
        try:
            with open(args.path, "r", encoding="utf-8") as file:
                args.string = file.read()
        except FileNotFoundError as exception:
            parser.error(f'Файл {exception.filename} не найден')

    tupl_ind = search(args.string, args.sub_string, args.case_sensitivity,
                      args.method, args.count)

    print(f'Строка: "{args.string}"')

    print(f'Подстрока(и): {args.sub_string}')

    print(f'Индексы: {str(tupl_ind)}')

    print(f"Раскрашенная строка:\n {paint_string(args.string, tupl_ind)}")


if __name__ == '__main__':
    main()
