from typing import Union, Optional

from back.linked_list import LinkedListItem, LinkedList
from back.composition import Composition
from back.utils import duration_from_seconds

import os

path = r"C:\Education\algo2\tracks\songs"
list_of_all = [f"{path}\\{track}" for track in os.listdir(path)]


class PlaylistItem(LinkedListItem):
    def __init__(self, composition: Composition) -> None:
        """
        Конструктор класса
        :param composition:
        """
        super().__init__(composition)


class Playlist(LinkedList):
    def __init__(self, head: Optional[PlaylistItem], name: Optional[str]) -> None:
        """
        Конструктор класса
        :param head: первая нода списка
        :param name: название
        """
        super().__init__(head)
        if name is None:
            self.name = 'Неизвестный'
        else:
            self.name = name

        if head is None:
            self.duration = '0:0'
        else:
            self.duration = duration_from_seconds(sum(map(lambda x: x.data.duration, self)))

        self.__current_track = head

    @property
    def current_track(self) -> Composition:
        """
        геттер значения текущего трека
        :return: значение текущего трека
        """
        return self.__current_track.data

    @current_track.setter
    def current_track(self, value: Composition) -> None:
        """
        сеттер значения текущего трека
        :param value: возможная нода списка
        """
        self.__current_track = self.find_node(value)

    def next_track(self) -> None:
        """
        получение следующего трека
        """
        self.__current_track = self.__current_track.next_item

    def previous_track(self) -> None:
        """
        получение предыдущего трека
        """
        self.__current_track = self.__current_track.previous_item

    def __str__(self) -> str:
        """
        строковое представление плейлиста
        :return: мету плейлиста
        """
        return f'{self.name} - {self.size} треков, длительностью {self.duration}'

    def __repr__(self) -> str:
        """
        строковое представление плейлиста
        :return: мету плейлиста
        """
        return f'{self.name} - {self.size} треков, длительностью {self.duration}'

    def meta(self) -> str:
        """
        получение меты плейлиста
        :return: выведенная мета
        """
        return f'{self.name} - {self.size} треков'

    def get_dict(self) -> dict:
        """
        получение словаря треков
        :return: словарь
        """
        res = {
            'name': self.name,
            'tracks': []
        }
        for node in self:
            res['tracks'].append(node.data.path)
        return res

    def swap(self, item, direction) -> None:
        """
        перемена местами двух треков в плейлисте
        :param item: нода выбранная для изменения местами
        :param direction: направление
        """
        first_item = self.find_node(item)
        second_item = first_item.previous_item
        if direction == "↓":
            second_item = first_item.next_item
        super().swap(first_item, second_item)

    def append(self, item: Composition) -> None:
        """
        добавление в плейлист
        :param item: трек для добавления
        """
        super().append(item)
        self.duration = duration_from_seconds(sum(map(lambda x: x.data.duration, self)))


def create_node_sequence(data: list) -> Optional[LinkedListItem]:
    """
    Функция создания последовательности нод
    :param data: список нод
    :return: первая нода
    """
    if not data:
        return None
    head = LinkedListItem(data[0])
    ptr = head
    for val in data[1:]:
        new_node = LinkedListItem(val)
        ptr.next_item = new_node
        new_node.previous_item = ptr
        ptr = ptr.next_item

    head.previous_item = ptr
    ptr.next_item = head

    return head


def make_list_of_all() -> Playlist:
    """
    Функция создания плэйлиста из всех треков
    :return:
    """
    return Playlist(create_node_sequence([Composition(paths) for paths in list_of_all]), "Все треки")


def make_empty_playlist(num: int) -> Playlist:
    """
    Функция создания пустого плэйлиста
    :param num: номер плэйлиста
    :return: экземпляр класса плейлист
    """
    return Playlist(head=None, name=f"Unnamed playlist No{num}")


def make_playlist(data: list[Composition], name: str) -> Playlist:
    """
    Функция для создания плейлиста
    :param data: список композиций
    :param name: название плейлиста
    :return: экземпляр класса плейлист
    """
    seq = create_node_sequence(data)
    return Playlist(seq, name=name)

