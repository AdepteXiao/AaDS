from tinytag import TinyTag
from back.utils import duration_from_seconds


class Composition:
    def __init__(self, path):
        """
        Конструктор класса
        :param path: путь до трека
        """
        self.__path = path
        self.tag = TinyTag.get(path, image=True)

    @property
    def duration(self):
        """
        геттер длины трека
        :return: длительность
        """
        return self.tag.duration

    @property
    def path(self):
        """
        геттер пути трека
        :return: путь
        """
        return self.__path

    @property
    def name(self):
        """
        геттер имени трека
        :return: название трека
        """
        return self.tag.title

    @property
    def author(self):
        """
        геттер автора трека
        :return: автор трека
        """
        return self.tag.artist

    @property
    def image(self):
        """
        геттер картинки трека
        :return: картинка трека
        """
        return self.tag.get_image()

    def __repr__(self):
        """
        представление в виде строки трека
        :return:мета трека
        """
        return f"{self.author} - {self.name}"

    def dur(self):
        """
        получение длительности трека в секундах
        :return: длина трека
        """
        return f'{duration_from_seconds(self.duration)}'


def get_comp(paths):
    """
    получение композиции по пути
    :param paths: пути композиций
    :return: композиции
    """
    return [Composition(t_path) for t_path in paths]
