import json
from back.playlist import Playlist, make_list_of_all, create_node_sequence
from back.composition import get_comp


class Relator:

    def __init__(self) -> None:
        """
        Конструктор класса, открывает и считывает json файл
        """
        self.json_file = r"C:\Education\algo2\tracks\main_playlist.json"
        with open(self.json_file, 'r', encoding="utf-8") as file:
            tmp = json.load(file)
            tmp[0] = make_list_of_all().get_dict()
        with open(self.json_file, 'w', encoding="utf-8") as file:
            json.dump(tmp, file, indent=4, ensure_ascii=False)

    def save(self, list_of_playlists: list[Playlist]) -> None:
        """
        сохранение
        :param list_of_playlists: список плейлистов
        """
        with open(self.json_file, 'w', encoding='utf-8') as file:
            res = []
            for pllst in list_of_playlists:
                res.append(pllst.get_dict())
            json.dump(res, file, indent=4, ensure_ascii=False)

    def load(self) -> list:
        """
        загрузка файла
        """
        with open(self.json_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def load_playlists(self) -> list:
        """
        загрузка плейлистов
        :return: список плейлистов
        """
        list_of_playlists = self.load()
        res = []
        for playlist_data in list_of_playlists:
            res.append(Playlist(name=playlist_data['name'],
                                head=create_node_sequence(
                                    get_comp(playlist_data['tracks']))))
        return res


if __name__ == '__main__':
    rel = Relator()
    for playlist in rel.load_playlists():
        print(playlist)
