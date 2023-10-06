from typing import Union, Iterable, Optional

# from natural_external_sort.taper import CsvTaper, TxtTaper, generate_csv_input
from taper import CsvTaper, TxtTaper


def get_io(path: str, mode: str, type_data: str, is_temp=False,
           delimiter=",", header=None, key=None) -> Union[TxtTaper, CsvTaper]:
    """
    Функция получения экземпляра класса взаимодействия с файлом
    :param path: путь файла
    :param mode: вариант открытия файла
    :param type_data: тип данных
    :param is_temp: флаг временности файла
    :param delimiter: разделитель
    :param header: заголовок столбца
    :param key: ключ для сортировки
    :return: экземпляр класса TxtTaper или CsvTaper
    """
    if path.endswith(".txt"):
        return TxtTaper(path, mode, type_data, is_temp)
    else:
        return CsvTaper(path, mode, type_data, is_temp, delimiter, header, key)


def merge_to_one(src: list[Union[CsvTaper, TxtTaper]], out: Union[CsvTaper, TxtTaper], reverse=False) -> None:
    """
    Функция слияния всех файлов в один
    :param src: исходные файлы
    :param out: выходной файл
    :param reverse: флаг сортировки по невозразстанию
    """
    for file in src:
        file.change_mode("r")
    vals_list = [file.read() for file in src]

    is_txt = True if src[0].filename.endswith(".txt") else False

    def find_val() -> Union[bool, str]:
        """
        Метод поиска максимального или минимального значения
        :return: Максимальное или минимальное значение, False если список пустой
        """
        func = max if reverse else min
        filtered_list = [val for val in vals_list if val is not None]

        if not filtered_list:
            return False
        if is_txt:
            return func(filtered_list)
        else:
            return func(filtered_list,
                        key=lambda x: x[src[0].key])

    while (need_val := find_val()) is not False:
        need_ind = vals_list.index(need_val)
        out.write(need_val)
        vals_list[need_ind] = src[need_ind].read()


def my_sort(src: Union[Iterable, str] = "input.txt",
            output: Optional[str] = None,
            reverse: bool = False,
            type_data: Optional[str] = None,
            key: Optional[str] = None,
            delimiter: str = ",") -> None:
    """
    Сортировка
    :param src: входной(ые) файл(ы)
    :param output: выходной файл
    :param reverse: флаг сортировки (по возрастанию или убыванию)
    :param type_data: тип данных
    :param key: ключ сортировки
    :param delimiter: разделитель
    """
    opened_src = []
    if isinstance(src, str):
        opened_src.append(get_io(src, "r",
                                 type_data=type_data,
                                 delimiter=delimiter,
                                 key=key))
    else:
        for file in src:
            opened_src.append(get_io(file, "r",
                                     type_data=type_data,
                                     delimiter=delimiter,
                                     key=key))

    src_ext = opened_src[0].filename.split(".")[-1]
    src_header = opened_src[0].header if hasattr(opened_src[0], "header") else None

    def external_sort(inp, num) -> Union[TxtTaper, CsvTaper]:
        """
        Естественная сортировка
        :param inp: входной файл
        :param num: номер входного файла
        :return: экземпляр Taper, в котором хранится отсортированная информация
        """
        tape0 = get_io(f"tape0_{num}.{src_ext}", "w", type_data=type_data,
                       delimiter=delimiter, header=src_header, key=key,
                       is_temp=True)
        inp.copy_to(tape0)
        tape0.change_mode("r")

        tape1 = get_io(f"tape1_{num}.{src_ext}", "w", type_data=type_data,
                       delimiter=delimiter, header=src_header, key=key,
                       is_temp=True)
        tape2 = get_io(f"tape2_{num}.{src_ext}", "w", type_data=type_data,
                       delimiter=delimiter, header=src_header, key=key,
                       is_temp=True)

        if inp.is_empty():
            return tape0

        def cmp(a, b) -> bool:
            """
            Метод сравнения двух элементов
            :param a: первый элемент сравнения
            :param b: второй элемент сравнения
            :return: True или False
            """
            if src_ext == "txt":
                return a >= b if reverse else a <= b
            else:
                return a[key] >= b[key] if reverse else a[key] <= b[key]

        def split() -> None:
            """
            Метод разделения файла на два по алгоритму сортировки
            """
            tape0.change_mode("r")
            tape1.change_mode("w")
            tape2.change_mode("w")
            prev = tape0.read()
            if prev is None:
                return
            tape1.write(prev)
            is_tape1 = True
            while (cur := tape0.read()) is not None:
                cur_tape = tape1 if is_tape1 else tape2
                if cmp(prev, cur):
                    # print(prev, cur, cmp(cur, prev))
                    cur_tape.write(cur)
                else:
                    is_tape1 = not is_tape1
                    cur_tape = tape1 if is_tape1 else tape2
                    cur_tape.write(cur)
                prev = cur

        def merge() -> bool:
            """
            Метод слияния файлов
            :return:
            """
            tape0.change_mode("w")
            tape1.change_mode("r")
            tape2.change_mode("r")
            if tape1.is_empty() != tape2.is_empty():
                if tape1.is_empty():
                    tape2.copy_to(tape0)
                else:
                    tape1.copy_to(tape0)
                return False
            merge_to_one([tape1, tape2], out=tape0, reverse=reverse)
            return True

        while True:
            split()
            if not merge():
                return tape0

    res_files = []

    for n, file in enumerate(opened_src):
        res_files.append(external_sort(file, n))

    if output:
        out = get_io(output, "w", type_data=type_data,
                     delimiter=delimiter, header=src_header, key=key,
                     is_temp=False)
        merge_to_one(res_files, out, reverse)
    else:
        for ind, file in enumerate(res_files):
            out = opened_src[ind]
            file.change_mode("r")
            out.change_mode("w")
            file.copy_to(out)


# if __name__ == '__main__':
#     for i in range(1, 4):
#         name_csv = f"inp{i}.csv"
#         name_txt = f"inp{i}.txt"
#         generate_csv_input(name_csv)
#         generate_input(name_txt)

