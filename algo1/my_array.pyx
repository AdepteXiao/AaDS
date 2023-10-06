# cython: language_level=3
# distutils: language = c

from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from cpython.float cimport PyFloat_AsDouble
from cpython.int cimport PyInt_AsLong

# Для проверки на тип в __eq__
import array as py_array

# Дескриптор, хранящий функции получения и записи значения в
# массив для нужных типов
cdef struct arraydescr:
    char * typecode
    int itemsize
    object (*getitem)(Array, size_t)
    int (*setitem)(Array, size_t, object)

cdef object double_getitem(Array a, size_t index):
    """
    Функция получения значения типа double из массива по индексу
    :param a: массив из которого получаем
    :param index: индекс искомого элемента
    :return: искомый элемент
    """
    return (<double *> a.data)[index]

cdef int double_setitem(Array a, size_t index, object obj):
    """
    Функция записи числа типа double в массив по индексу
    :param a: массив, в который записываем
    :param index: индекс, куда записываем
    :param obj: элемент, который записываем
    :return: код выполнения (0 - успех, -1 - ошибка)
    """
    if not isinstance(obj, int) and not isinstance(obj, float):
        return -1

    cdef double value = PyFloat_AsDouble(obj)

    if index >= 0:
        (<double *> a.data)[index] = value
    return 0

cdef object int_getitem(Array a, size_t index):
    """
    Функция получения значения типа long из массива по индексу
    :param a: массив из которого получаем
    :param index: индекс искомого элемента
    :return: искомый элемент
    """
    return (<int *> a.data)[index]

cdef int int_setitem(Array a, size_t index, object obj):
    """
    Функция записи числа типа long в массив по индексу
    :param a: массив, в который записываем
    :param index: индекс, куда записываем
    :param obj: элемент, который записываем
    :return: код выполнения (0 - успех, -1 - ошибка)
    """
    if not isinstance(obj, int):
        return -1

    cdef long value = PyInt_AsLong(obj)

    if index >= 0:
        (<long *> a.data)[index] = value
    return 0

# Массив дескрипторов для типов long и double
cdef arraydescr[2] descriptors = [
    arraydescr("d", sizeof(double), double_getitem, double_setitem),
    arraydescr("i", sizeof(long), int_getitem, int_setitem),
]

# Поддержка произвольных типов, значения - индексы дескрипторов в массиве
cdef enum TypeCode:
    DOUBLE = 0
    LONG = 1


cdef enum TypesRefactor:
    NO_TYPE = 0
    INT_TO_INT = 1
    INT_TO_DOUBLE = 2
    DOUBLE_TO_INT = 3
    DOUBLE_TO_DOUBLE = 4


cdef int char_typecode_to_int(str typecode):
    """
    Преобразование строкового кода в число
    :param typecode: строковое представление
    :return: число, соответствующее строковому представлению
    """
    if typecode == "d":
        return TypeCode.DOUBLE
    if typecode == "i":
        return TypeCode.LONG
    return -1

cdef long check_ind(long index, long length):
    """
    Преобразования индекса (для поддержки обращения с отрицательным индексом)
    :param index: индекс
    :param length: длина массива
    :return: корректный индекс
    """
    if length == 0 and index < 0:
        return 0
    if index < 0:
        return length + index
    return index

cdef class Array:
    """`
    Класс динамического массива, реализующий основные методы list в python,
    с поддержкой значений типа int и float
    """
    cdef public size_t length,  size
    cdef char * data
    cdef arraydescr * descr
    cdef int type


    def __init__(self, str typecode, orig_array=None) -> None:
        """
        Конструктор экземпляра массива
        :param typecode: "i" если массив с значениями типа "int", "d" если float (double)
        :param orig_array: Iterable объект для инициализации исходных значений массива
        """
        if orig_array is None:
            orig_array = []
        self.size = len(orig_array)
        self.length = len(orig_array)

        cdef int mtypecode = char_typecode_to_int(typecode)
        self.type = mtypecode
        self.descr = &descriptors[mtypecode]

        # Выделяем память для массива
        self.data = <char *> PyMem_Malloc(self.length * self.descr.itemsize)
        if not self.data:
            raise MemoryError()

        for i in range(self.length):
            check_res = self.check_type(orig_array[i])
            if check_res == TypesRefactor.NO_TYPE and check_res != TypesRefactor.INT_TO_DOUBLE:
                raise TypeError("Incorrect type of value")
            self[i] = self.check_val(orig_array[i])

    def check_type(self, obj: object) -> int:
        """
        Распознавание типа значения исходя из типа массива:
        :param obj: значение
        :return: тип значения
        """

        if abs(obj) > 2147483647:
            raise ValueError('value is too big')

        if isinstance(obj, int):
            if TypeCode.LONG == self.type:
                return TypesRefactor.INT_TO_INT
            if TypeCode.LONG != self.type:
                return TypesRefactor.INT_TO_DOUBLE
        elif isinstance(obj, float):
            if obj.is_integer():
                return TypesRefactor.DOUBLE_TO_INT
            if TypeCode.DOUBLE == self.type:
                return TypesRefactor.DOUBLE_TO_DOUBLE
        return TypesRefactor.NO_TYPE

    def check_val(self, object val):
        """
        Преобразование значения в соответствии с типом массива
        :param val значение для преобразования
        :return: преобразованное значение
        """
        check_res = self.check_type(val)
        if check_res == TypesRefactor.INT_TO_INT:
            return int(val)
        if check_res == TypesRefactor.INT_TO_DOUBLE:
            return float(val)
        if check_res == TypesRefactor.DOUBLE_TO_INT:
            return int(val)
        if check_res == TypesRefactor.INT_TO_INT or check_res == TypesRefactor.DOUBLE_TO_DOUBLE:
            return val
        raise TypeError("Incorrect type of values")

    def append(self, elem: object) -> None:
        """
        Добавление элемента в конец массива:
        :param elem: добавляемый элемент
        """
        val = self.check_val(elem)

        if self.length == self.size:
            self.extend_array()
        self.descr.setitem(self, self.length, val)
        self.length += 1


    def insert(self, index: int, item: object) -> None:
        """
        Вставка элемента по индексу:
        :param index: индекс на который вставляем элемент
        :param item: вставляемый элемент
        """
        if not isinstance(index, int) and not index.is_integer():
            raise IndexError("incorrect type of index")
        val_item = self.check_val(item)
        if index > self.length and index > 0:
            index = self.length

        if abs(index) > self.length and index < 0:
            index = 0
        if self.length == self.size:
            self.extend_array()
        index = check_ind(index, self.length)
        self.length += 1
        for i in range(self.length - 1, index, -1):
            self[i] = self[i - 1]
        self[index] = val_item

    def remove(self, object item) -> None:
        """
        Удаление первого вхождения значения в массив:
        :param item: значение элемента
        """
        cdef int is_find = False
        cdef long i
        for i in range(self.length):
            if self[i] == item:
                is_find = True
            if is_find and i < self.length - 1:
                self[i] = self[i + 1]
        if not is_find:
            raise ValueError(f"array.remove(item): item not in array")
        self.length -= 1
        if self.length <= self.size // 2:
            self.shorten_array()

    def pop(self, index: int | None = None) -> object:
        """
        Метод удаления элемента по индексу с последующим его возвращением
        array.pop() - удалит последний элемент массива
        :param index: индекс удаляемого элемента
        :return: удаляемый элемент
        """

        if not isinstance(index, (int, type(None))) and not index.is_integer():
            raise IndexError("incorrect type of index")
        if self.length == 0:
            raise IndexError(f"pop from empty list")
        if index is None:
            pop_val = self[self.length - 1]
            if self.length <= self.size // 2:
                self.shorten_array()
            self.length -= 1
            return pop_val
        if -index != self.length and abs(index) >= self.length:
            raise IndexError(f"pop index out of range")
        index = check_ind(index, self.length)
        pop_val = self[index]
        for i in range(index, self.length - 1):
            self[i] = self[i + 1]
        self.length -= 1
        if self.length <= self.size // 2:
            self.shorten_array()
        return pop_val


    def extend_array(self) -> None:
        """
        Увеличение выделяемой для массива памяти
        """
        if self.length != 0:
            self.size *= 2
        else:
            self.size = 1
        self.data = <char *> PyMem_Realloc(self.data, self.size * self.descr.itemsize)


    def shorten_array(self) -> None:
        """
        Уменьшение кол-ва выделяемой для массива памяти вдвое
        """
        self.size = self.size // 2
        self.data = <char *> PyMem_Realloc(self.data, self.size * self.descr.itemsize)

    def __dealloc__(self) -> None:
        PyMem_Free(self.data)


    # Добавим возможность получать элементы по индексу.
    def __getitem__(self, index: int) -> object:
        """
        Метод получения значения по индексу
        :param index: индекс получаемого значения
        :return: значение
        """
        if not isinstance(index, int):
            raise TypeError(f"incorrect type of index")
        index = check_ind(index, self.length)
        if 0 <= index < self.length:
            return self.descr.getitem(self, index)
        raise IndexError("list index out of range")

    # Запись элементов по индексу.
    def __setitem__(self, index: int, value: object) -> None:
        """
        Метод установки значения по индексу
        :param index: индекс
        :param value: значение
        """
        if not isinstance(index, int):
            raise TypeError(f"incorrect type of index")
        index = check_ind(index, self.length)
        value = self.check_val(value)
        if 0 <= index < self.length:
            self.descr.setitem(self, index, value)
        else:
            raise IndexError("list index out of range")

    def __len__(self) -> size_t:
        """
        Метод поиска длины массива
        :return: Кол-во элементов массива
        """
        return self.length

    def __eq__(self, array_to_eq : list | py_array | Array) -> bool:
        """
        Метод сравнения массива с другим Iterable объектом
        :param array_to_eq: Объект с которым сравниваем
        :return: булевый результат проверки на равенство
        """
        if not isinstance(array_to_eq, (list, py_array.array, Array)):
            return False
        if len(self) != len(array_to_eq):
            return False
        for i in range(self.length):
            if self[i] != array_to_eq[i]:
                return False
        return True

    def __repr__(self) -> str:
        """
        Возвращает текстовое представление массива
        :return: Строка в виде [x1, x2, x3], содержащая все эл-ты массива
        """
        typecode = 'i' if self.type == 1 else 'd'
        return f"{self.__class__.__name__}('{typecode}', [{', '.join(str(i) for i in self)}])"

    def __sizeof__(self) -> size_t:
        """
        Возвращает занимаемую массивом память
        :return: Количество занимаемой памяти
        """
        return self.size * self.descr.itemsize