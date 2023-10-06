from typing import Optional, Union
from collections import defaultdict


def get_ngrams(text, n):
    words = text.split()
    ngrams = defaultdict(list)
    for num, word in enumerate(words):
        if len(word) > n:
            for i in range(len(word)-n+1):
                ngrams[word[i:i+n]].append(word)
        else:
            ngrams[word].append(word)
    return ngrams


def caps_sens(text):
    return text.lower()


def search(text: str, sub_string: Union[str, tuple[str, ...]],
           case_sensitivity: bool = False, method: str = 'first',
           count: Optional[int] = None):
    """
    Нахождение индексов первых элементов всех вхождений всех строк
    :param text: текст
    :param sub_string: строка для поиска
    :param case_sensitivity: чувствительность к регистру
    :param method: метод обхода текста
    :param count: необходимое количество вхождений
    :return: None если не найдено ни одного вхождения,
    """
    res = []
    if not case_sensitivity:
        text = text.lower()
        sub_string = sub_string.lower()
    if method == 'last':
        text = text[::-1]
        sub_string = sub_string[::-1]
    text_ngrams = get_ngrams(text, 3)
    substr_ngrams = get_ngrams(sub_string, 3)
    for key_s in substr_ngrams.keys():
        for key_t in text_ngrams.keys():
            if key_t == key_s:
                res.append(text_ngrams[key_t])
    return res


if __name__ == '__main__':
    text = "Параллельный поиск подстроки в строке"
    search(text, 'тро')
    # ngrams = get_ngrams(text, 3)
    # print(ngrams)
