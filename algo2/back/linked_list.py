from typing import Union, Iterator, Generator, Optional


class LinkedListItem:
    def __init__(self, item: Optional[object] = None) -> None:
        self.__next = None
        self.__prev = None
        self.data = item

    @property
    def next_item(self) -> object:
        return self.__next

    @next_item.setter
    def next_item(self, value: object) -> None:
        self.__next = value
        value.__prev = self  # pylint: disable=E0401

    @property
    def previous_item(self) -> object:
        return self.__prev

    @previous_item.setter
    def previous_item(self, value: object) -> None:
        self.__prev = value
        value.__next = self  # pylint: disable=W0238

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return f"   prev: {self.previous_item}\n" \
               f"   val: {self.data}\n" \
               f"   next: {self.next_item}"


class LinkedList:
    def __init__(self, head: Optional[LinkedListItem] = None) -> None:
        """
        Конструктор класса, присваивает первому и последнему элементу
        значение первой и последней ноды списка
        :param head: первая нода списка
        """
        self.__head = head

        if head is None:
            self.__tail = None
            self.size = 0
        else:
            self.size = 1
            ptr = head
            while ptr.next_item is not None and ptr.next_item != self.head:
                ptr = ptr.next_item
                self.size += 1
            self.tail = ptr

    @property
    def head(self) -> Optional[LinkedListItem]:
        """
        Свойство геттер значения первой ноды
        :return: значение первой ноды
        """
        return self.__head

    @property
    def tail(self) -> Optional[LinkedListItem]:
        """
        Свойство геттер значения последней ноды
        :return: значение последней нода
        """
        return self.__tail

    @tail.setter
    def tail(self, value: Optional[LinkedListItem]) -> None:
        """
        Свойство сеттер значения последней ноды
        :param value: нода
        """
        self.__tail = value

    @head.setter
    def head(self, value: Optional[LinkedListItem]) -> None:
        """
        Свойство сеттер значения первой ноды списка
        :param value: нода
        """
        self.__head = value

    def append_to_empty_list(self, item: object) -> None:
        """
        Метод вставки ноды в пустой список
        :param item: вставляемая нода
        """
        new_node = LinkedListItem(item)
        self.head = new_node
        self.tail = new_node
        new_node.previous_item = self.tail
        new_node.next_item = self.head
        self.size += 1

    def append_left(self, item: object) -> None:
        """
        Метод вставки ноды в начало списка
        :param item: вставляемая нода
        """
        if self.head is None:
            self.append_to_empty_list(item)
            return
        new_node = LinkedListItem(item)
        new_node.next_item = self.head
        self.head.previous_item = new_node
        self.head = new_node
        self.size += 1

    def append_right(self, item: object) -> None:
        """
        Метод вставки ноды в конец списка
        :param item: вставляемая нода
        """
        self.append(item)

    def append(self, item: object) -> None:
        """
        Метод вставки ноды в конец списка
        :param item: вставляемая нода
        """
        if self.head is None:
            self.append_to_empty_list(item)
            return
        new_node = LinkedListItem(item)
        self.tail.next_item = new_node
        self.tail = new_node
        self.tail.next_item = self.head
        self.head.previous_item = self.tail
        self.size += 1

    def insert(self, previous: Union[LinkedListItem, object],
               item: object) -> None:
        """
        Метод вставки ноды после выбранной
        :param previous: нода, после которой будет вставлена новая
        :param item: вставляемая нода
        """
        if not isinstance(previous, LinkedListItem):
            previous = self.find_node(previous)
        new_node = LinkedListItem(item)
        nxt = previous.next_item
        nxt.previous_item = new_node
        previous.next_item = new_node
        new_node.previous_item = previous
        new_node.next_item = nxt
        self.size += 1

    def remove(self, item) -> None:
        """
        Метод удаления ноды из списка
        :param item: значение для удаления
        """
        if not isinstance(item, LinkedListItem):
            item = self.find_node(item)

        if self.size == 1:
            self.head = None
            self.tail = None
            self.size = 0
            del item
            return

        if self.tail == item:
            self.tail = item.previous_item

        if self.head == item:
            self.head = item.next_item

        item.previous_item.next_item = item.next_item
        item.next_item.previous_item = item.previous_item
        del item
        self.size -= 1

    def find_node(self, data: object) -> LinkedListItem:
        """
        Метод поиска ноды в списке
        :param data: передаваемое значение ноды
        :return: ноду
        """
        for node in self:
            if node.data == data:
                return node
        raise ValueError("data not in list")

    def swap(self, first_item: LinkedListItem,
             second_item: LinkedListItem) -> None:
        """
        Метод обмена двух любых нод списка между собой
        :param first_item: первая нода
        :param second_item: вторая нода
        """

        if first_item == self.head:
            self.head = second_item
        elif second_item == self.head:
            self.head = first_item
        if first_item == self.tail:
            self.tail = second_item
        elif second_item == self.tail:
            self.tail = first_item

        temp = first_item.next_item
        first_item.next_item = second_item.next_item
        second_item.next_item = temp

        if first_item.next_item is not None:
            first_item.next_item.previous_item = first_item
        if second_item.next_item is not None:
            second_item.next_item.previous_item = second_item

        temp = first_item.previous_item
        first_item.previous_item = second_item.previous_item
        second_item.previous_item = temp

        if first_item.previous_item is not None:
            first_item.previous_item.next_item = first_item
        if second_item.previous_item is not None:
            second_item.previous_item.next_item = second_item

    def __len__(self) -> int:
        """

        :return:
        """
        return self.size

    def __iter__(self) -> Iterator:
        """

        """
        pointer = self.head
        for _ in range(self.size):
            yield pointer
            pointer = pointer.next_item

    def __contains__(self, item: object) -> bool:
        """

        :param item:
        :return:
        """
        for list_item in self:
            if item in (list_item, list_item.data):
                return True
        return False

    def __reversed__(self) -> Generator:
        """

        """
        node = self.tail
        for _ in range(self.size):
            yield node.data
            node = node.previous_item

    def __getitem__(self, index: int) -> object:
        """
        Метод получения элемента из списка по индексу
        :param index: индекс элемента
        :return:
        """
        if index >= self.size or abs(index) > self.size:
            raise IndexError("index out of range")
        if index >= 0:
            ptr = self.head
            for _ in range(index):
                ptr = ptr.next_item
        else:
            ptr = self.tail
            for _ in range(-1, index, -1):
                ptr = ptr.previous_item
        return ptr.data

    def __str__(self):
        """
        Метод представления списка в виде строки
        :return:
        """
        return f"{self.__class__.__name__}([{', '.join([str(i) for i in self])}])"
