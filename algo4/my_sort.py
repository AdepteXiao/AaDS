from math import log2


def my_sort(array: list, reverse: bool = False, key=None, cmp=None) -> list:
    """
    Алгоритм сортировки
    :param array: сортируемый список
    :param reverse: флаг определяющий вариант сортировки, True по убыванию, False по возрастанию
    :param key: функция, вычисляющая значение, на основе которого будет производится сортировка
    Должна принимать один аргумент и возвращать значение.
    :param cmp: функция сравнения, должна принимать два аргумента и возвращать значение
    :return: отсортированный список
    """
    ar_len = len(array)
    last_index = ar_len - 1

    key = key if key is not None else lambda x: x
    cmp = cmp if cmp is not None else lambda x, y: x < y

    def intro_sort(begin=0, end=None, depth=0):
        """
        Интроспективная сортировка
        :param begin: начальный элемент
        :param end: конечный элемент
        :param depth: глубина рекурсии
        :return: отсортированный список
        """
        def heap_sort(heap):
            """
            Сортировка кучами (пирамидальная сортировка)
            :param heap: Сортируемый список
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
                    first_larger += 1

            array[end], array[first_larger] = array[first_larger], array[end]
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
                array[begin:end + 1] = heap_sort(array[begin:end + 1])
        else:
            return array

    intro_sort()
    return array


if __name__ == '__main__':
    from random import shuffle

    a = list(range(1, 1000))
    shuffle(a)
    print(a)
    my_sort(a)
    print(a == sorted(a))
