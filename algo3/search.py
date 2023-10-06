"""
Модуль в котором реализован поиска подстрок в строке методом
Кнута-Морриса-Пратта
"""
from typing import Optional, Union


def pi_array(key):
    """
    Создание вспомогательного массива пи
    :param key: подстрока для нахождения
    :return: массив пи
    """
    p = [0] * len(key)
    j = 0
    i = 1
    while i < len(key):
        if key[j] == key[i]:
            p[i] = j + 1
            i += 1
            j += 1
        else:
            if j == 0:
                p[i] = 0
                i += 1
            else:
                j = p[j - 1]
    return p


def kmp(string, sub_string,
        case_sensitivity: bool = False, method: str = 'first',
        count: int = None):
    """
    Алгоритм по нахождению индексов первых элементов всех вхождений для
    одного ключевого слова
    :param string: строка
    :param sub_string: подстрока для поиска
    :param case_sensitivity: чувствительность к регистру
    :param method: метод обхода строки
    :param count: необходимое количество вхождений
    :return: множество индексов
    """
    if not case_sensitivity:
        string = string.lower()
        sub_string = sub_string.lower()
    if method == 'last':
        string = string[::-1]
        sub_string = sub_string[::-1]

    res = []
    p = pi_array(sub_string)
    key_len = len(sub_string)
    txt_len = len(string)
    i = 0
    j = 0
    while i < txt_len and count != 0:
        if string[i] == sub_string[j]:
            i += 1
            j += 1
            if j == key_len:
                if count:
                    count -= 1
                if method == 'first':
                    res.append(i - j)
                else:
                    res.append(txt_len - i)
                i -= j - 1
                j = 0
        else:
            if j > 0:
                j = p[j - 1]
            else:
                i += 1
    if not res:
        return
    return tuple(res)


def search(string: str, sub_string: Union[str, tuple[str, ...]],
           case_sensitivity: bool = False, method: str = 'first',
           count: Optional[int] = None, ) -> Optional[
        Union[tuple[int, ...], dict[str, tuple[int, ...]]]]:
    """
    Нахождение индексов первых элементов2 всех вхождений всех строк
    :param string: строка
    :param sub_string: подстрока для поиска
    :param case_sensitivity: чувствительность к регистру
    :param method: метод обхода строки
    :param count: необходимое количество вхождений
    :return: None если не найдено ни одного вхождения, иначе либо
    множество индексов, если одно ключевое слово, либо
    словарь {ключ: множество индексов} если ключей несколько
    """
    if isinstance(sub_string, str):
        return kmp(string, sub_string, case_sensitivity, method, count)
    res = {}
    for st in sub_string:
        res[st] = kmp(string, st, case_sensitivity, method, count)
    if all(map(lambda x: x is None, res.values())):
        return None
    return res


# if __name__ == '__main__':
#
#     print(search('ababbababa', ('aba', 'bba'), False, 'first', 4))
