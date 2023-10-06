import csv
import os
from io import UnsupportedOperation
from typing import Union

TEMP_DIR = "files"
TxtLine = Union[str, int, float]
CsvLine = dict[str, Union[str, int, float]]


class Taper:
    """
    Класс ввода вывода
    """
    def __init__(self, filename: str, mode: str, type_data: str, is_temp: bool) -> None:
        """
        Инициализация экземпляра
        :param filename: имя файла
        :param mode: вариант открытия файла
        :param type_data: тип данных
        :param is_temp: флаг временности файла
        """
        self.filename = filename
        self.mode = mode
        self.is_temp = is_temp
        self.descr = {"i": int, "s": str, "f": float}[type_data]

        if self.is_temp and not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)

        self.path = os.path.join(TEMP_DIR, filename) if is_temp else filename

        open_args = {"file": self.path,
                     "mode": mode,
                     "encoding": "utf-8"}
        if self.path.endswith(".csv"):
            open_args["newline"] = ""

        self.file = open(**open_args)

    def read(self) -> None:
        """
        Метод чтения файла
        """
        if self.mode != "r":
            raise UnsupportedOperation("not readable")

    def write(self, data: Union[TxtLine, CsvLine]) -> None:
        """
        Метод  записи в файл
        :param data: Данные для записи
        """
        if self.mode != "w":
            raise UnsupportedOperation("not writable")

    def change_mode(self, new_mode: str) -> None:
        """
        Метод смены варианта открытия файла
        :param new_mode: новый вариант
        """
        self.mode = new_mode
        self.file.close()

    def copy_to(self, dest) -> None:
        """
        Метод копирования
        :param dest: файл куда копировать
        """
        if dest.mode != "w" or type(self) != type(dest):
            raise TypeError(f"cant be copied to this file {repr(dest)}")

    def is_empty(self) -> None:
        """
        Метод проверки на пустоту
        """
        pass

    def __repr__(self) -> str:
        """
        Метод строкового представления информации о текущем файле
        :return: информация
        """
        return f"{self.__class__.__name__}(" \
               f"path={self.path}, " \
               f"mode={self.mode}, " \
               f"is_temp={self.is_temp})"

    def __del__(self) -> None:
        """
        Метод удаления файла
        """
        # print(f"{self.filename} closed")
        self.file.close()
        if self.is_temp:
            os.remove(self.path)
        if os.path.exists(TEMP_DIR) and not os.listdir(TEMP_DIR):
            os.rmdir(TEMP_DIR)


class TxtTaper(Taper):
    """
    Класс ввода вывода .txt файла
    """
    def __init__(self, filename: str, mode: str, type_data: str, is_temp=False):
        """
        Инициализация экземпляра
        :param filename: имя файла
        :param mode: вариант открытия файла
        :param type_data: тип данных
        :param is_temp: флаг временности файла
        """
        super().__init__(filename, mode, type_data, is_temp)

    def read(self) -> Union[TxtLine, None]:
        """
        Метод чтения .txt файла
        :return: None если файл пустой, тип и строку из элементов файла
        """
        super().read()
        res = self.file.readline().replace("\n", "")
        if res == "":
            return None
        return self.descr(res)

    def write(self, data: TxtLine) -> None:
        """
        Метод записи в .txt файл
        :param data: данные для записи
        """
        super().write(data)
        self.file.write(f"{data}\n")

    def copy_to(self, dest) -> None:
        """
        Метод копирования в .txt файл
        :param dest: файл получатель
        """
        super().copy_to(dest)
        while (char := self.file.read()) != "":
            dest.file.write(char)

    def is_empty(self) -> bool:
        """
        Проверка txt файла на пустоту
        :return: True если файл пустой, False в противном случае
        """
        self.file.seek(0, 0)
        data = self.file.read()
        self.file.seek(0, 0)
        if not data or data == "\n":
            return True
        return False

    def change_mode(self, new_mode: str) -> None:
        """
        Метод смены варианта открытия файла .txt
        :param new_mode: новый вариант
        """
        super().change_mode(new_mode)
        self.file = open(self.path, self.mode)


class CsvTaper(Taper):
    """
    Класс ввода вывода .txt файла
    """
    def __init__(self, filename: str, mode: str, type_data: str, is_temp: bool,
                 delimiter=",", header=None, key=None):
        """
        Инициализация экземпляра
        :param filename: имя файла
        :param mode: вариант открытия файла
        :param type_data: тип данных
        :param is_temp: флаг временности файла
        :param delimiter: разделитель
        :param header: заголовок столбца
        :param key: ключ для сортировки
        """
        if header is None and mode == "w":
            raise TypeError("cant write without header")

        super().__init__(filename, mode, type_data, is_temp)
        self.header = header
        self.delimiter = delimiter

        if mode == "r":
            self.connector = csv.DictReader(self.file, delimiter=delimiter)
            self.header = self.connector.fieldnames
        else:
            self.connector = csv.DictWriter(self.file, header, delimiter=delimiter)
            self.connector.writeheader()
        self.key = key if key else self.header[0]
        if self.key not in self.header:
            raise ValueError(f"couldn't find key value ({self.key}) in header")

    def read(self) -> Union[CsvLine, None]:
        """
        Метод чтения .csv файла
        :return: None если файл пустой, иначе
        """
        super().read()
        try:
            res = next(self.connector)  # noqa
            res[self.key] = self.descr(res[self.key])
        except StopIteration:
            return None
        return res

    def write(self, data: CsvLine) -> None:
        """
        Метод записи в .csv файл
        :param data: данные для записи
        """
        super().write(data)
        self.connector.writerow(data)

    def copy_to(self, dest) -> None:
        """
        Метод копирования в .csv файл
        :param dest: файл назначения
        """
        while (res := self.read()) is not None:
            dest.write(res)

    def is_empty(self) -> bool:
        """
        Метод проверки на пустоту файла .csv
        :return: True если пустой, иначе False
        """
        self.change_mode("r")
        try:
            next(self.connector)  # noqa
        except StopIteration:
            return True
        self.change_mode("r")
        return False

    def change_mode(self, new_mode: str) -> None:
        """
        Метод смены варианта открытия файла .csv
        :param new_mode: новый вариант
        """
        super().change_mode(new_mode)
        self.file = open(self.path, self.mode, newline="")
        if self.mode == "r":
            self.connector = csv.DictReader(self.file,
                                            delimiter=self.delimiter)
        else:
            self.connector = csv.DictWriter(self.file, self.header,
                                            delimiter=self.delimiter)
            self.connector.writeheader()


# def generate_input(file_name: str = "input.txt") -> None:
#     """
#     Генерация случайного входного txt файла
#     :param file_name: имя файла
#     """
#     from random import shuffle, randint
#
#     with open(file_name, "w") as file:
#         res = [randint(-1000, 1000) for _ in range(200)]
#         shuffle(res)
#         # res = [randint(-100, 100)]
#         # for i in range(1, 10):
#         #     res.append(randint(res[i - 1], res[i - 1] + 100))
#         # res.reverse()
#         for i in res:
#             file.write(f"{i}\n")
#
#
# def generate_csv_input(file_name: str = "input.csv", delimiter=","):
#     """
#     Генерация случайного входного csv файла
#     :param file_name: имя файла
#     :param delimiter: разделитель между столбцами
#     """
#     from random import randint
#     rows = list("abcd")
#     with open(file_name, "w", newline="") as file:
#         writer = csv.DictWriter(file, rows, delimiter=delimiter)
#         writer.writeheader()
#         for _ in range(100):
#             writer.writerow({row: randint(-100, 1000) for row in rows})

# if __name__ == '__main__':
    # generate_csv_input(delimiter="|")
    # tape = CsvTaper("input.csv", "r", type_data="i", is_temp=False, key="a",
    #                 delimiter="|")
    # while (line := tape.read()) is not None:
    #     print(line)
