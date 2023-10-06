import argparse
from sort import my_sort


def main():
    parser = argparse.ArgumentParser("Внешняя естественная сортировка")
    parser.add_argument("-i", "--input", dest="inp", type=str,
                        nargs="+", help="Входные файлы")
    parser.add_argument("-o", "--output", dest="out", type=str, default=None,
                        help="Выходной файл")
    parser.add_argument("-td", "--type_data", dest="type_data", type=str,
                        default="s", help="Тип входных данных")
    parser.add_argument("-r", "--reverse", dest="reverse", default=False,
                        action=argparse.BooleanOptionalAction,
                        help="Флаг обратной сортировки")
    parser.add_argument("-k", "--key", dest="key", default=None, type=str,
                        help="Ключ столбца csv файла")
    parser.add_argument("-d", "--delimiter", dest="delimiter", default=",",
                        type=str, help="Разделитель для csv файла")
    args = parser.parse_args()
    kwargs = {"src": args.inp,
              "output": args.out,
              "type_data": args.type_data,
              "reverse": args.reverse,
              "key": args.key,
              "delimiter": args.delimiter
              }
    my_sort(**kwargs)


if __name__ == '__main__':
    main()
