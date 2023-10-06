from sys import argv, exit

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QSize, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from back.composition import Composition
from back.database_interaction import Relator
from back.playlist import Playlist, PlaylistItem, make_list_of_all, \
    make_empty_playlist
from back.utils import duration_from_seconds, duration_from_ms
from front.designer_maked.des_ui import Ui_MainWindow

from PyQt5.QtWidgets import (QScrollArea, QApplication, QWidget,
                             QMainWindow, QHBoxLayout, QVBoxLayout,
                             QLabel, QSpacerItem, QSizePolicy,
                             QPushButton, QSlider,
                             QGroupBox, QMenu, QInputDialog)

LOG_SLOTS = False


def make_pixmap(img: bytes, size_x: int, size_y: int) -> QPixmap:
    pix = QPixmap()
    pix.loadFromData(img)
    pix = pix.scaled(size_x, size_y, Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)
    return pix


class MainUI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My music Player")
        self.setupUi(self)

        self.relator = Relator()
        self.playlists = self.relator.load_playlists()

        self.playlistsLayout = QHBoxLayout(self)

        self.playLine = PlayLineGroupBox(make_list_of_all())

        self.all_playlists = AllPlaylistsGroupbox(self.playlists)
        self.all_playlists.to_be_cur.connect(self.cur)  # noqa
        self.all_playlists.add_new_list.connect(self.add)  # noqa
        self.all_playlists.rename_pllist.connect(self.rename)  # noqa
        self.all_playlists.delete_pllist.connect(self.delete)  # noqa

        self.playlistsLayout.addWidget(self.all_playlists)

        self.playlist_boxes = dict()
        self.cur_plist = None
        for plist in self.playlists:
            new_box = CurPlaylistGroupbox(plist, self)
            new_box.updated.connect(self.update_handler)  # noqa
            new_box.list_updated.connect(self.update_tr_in_pll)  # noqa
            if plist.name != "Все треки":
                new_box.hide()
            else:
                self.cur_plist = new_box
            self.playlistsLayout.addWidget(new_box)
            self.playlist_boxes[plist.name] = new_box

        self.verticalLayout.addLayout(self.playlistsLayout)
        self.verticalLayout.addWidget(self.playLine)

    def update_tr_in_pll(self):
        if LOG_SLOTS:
            print(
                f"\033[0;32m[ MAIN]\033[0;0m {self.sender().name} "
                f"обновил порядок треков")  # noqa
        for pl_box in self.all_playlists.playlist_boxes:
            if pl_box.playlist.name == self.sender().name:
                pl_box.update_meta(self.sender().playlist)
        if self.cur_plist.playlist.name == self.sender().playlist.name:
            if not len(
                    self.playlist_boxes[self.sender().playlist.name].playlist):
                self.cur("Все треки")
            else:
                self.cur(self.sender().playlist.name)  # noqa

    def update_handler(self):
        if LOG_SLOTS:
            print(
                f"\033[0;32m[ MAIN]\033[0;0m {self.sender().name} "
                f"делается текущим")  # noqa
        self.playLine.make_pll_cur(self.sender().playlist)  # noqa

    def cur(self, name):
        if LOG_SLOTS:
            print(f"\033[0;32m[ MAIN]\033[0;0m делает {name} текущим")
        if not len(self.playlist_boxes[name].playlist):
            return
        self.cur_plist.hide()
        self.cur_plist = self.playlist_boxes[name]
        self.cur_plist.show()
        self.playLine.make_pll_cur(self.cur_plist.playlist)

    def add(self):
        if LOG_SLOTS:
            print(f"\033[0;32m[ MAIN]\033[0;0m генерит новый плейлист")
        new_list = make_empty_playlist(len(self.playlist_boxes))

        new_box = CurPlaylistGroupbox(new_list, self)
        new_box.updated.connect(self.update_handler)  # noqa
        new_box.list_updated.connect(self.update_tr_in_pll)  # noqa
        new_box.hide()

        self.playlistsLayout.addWidget(new_box)
        self.playlist_boxes[new_list.name] = new_box

        self.all_playlists.add_playlist(new_list)

    def rename(self, names):
        old_name, new_name = names
        if LOG_SLOTS:
            print(
                f"\033[0;32m[ MAIN]\033[0;0m меняет имя {old_name} на {new_name}")
        old_name_val = self.playlist_boxes[old_name]
        del self.playlist_boxes[old_name]
        self.playlist_boxes[new_name] = old_name_val
        old_name_val.playlist.name = new_name
        old_name_val.upd()

    def delete(self, name):
        if LOG_SLOTS:
            print(f"\033[0;32m[ MAIN]\033[0;0m удаляет плейлист {name}")
        pllist_box = self.playlist_boxes[name]
        if pllist_box == self.cur_plist:
            self.cur("Все треки")
        del self.playlist_boxes[name]
        pllist_box.deleteLater()

    def closeEvent(self, event) -> None:
        self.relator.save([playlist_box.playlist for playlist_box in
                           self.playlist_boxes.values()])
        event.accept()


class AllPlaylistsGroupbox(QGroupBox):
    to_be_cur = pyqtSignal(str)
    add_new_list = pyqtSignal()
    rename_pllist = pyqtSignal(tuple)
    delete_pllist = pyqtSignal(str)

    def __init__(self, playlists: list):
        super().__init__()
        self.setTitle('Плейлисты')

        self.layout = QVBoxLayout(self)

        self.scrollArea = QScrollArea()
        self.scrollAreaWidget = QWidget()
        self.scrollAreaWidgetLayout = QVBoxLayout(self.scrollAreaWidget)
        self.scrollArea.setWidget(self.scrollAreaWidget)

        self.playlist_boxes = []
        for playlist in playlists:
            new_playlist = PlaylistGroupbox(playlist, self)
            new_playlist.want_to_be_cur.connect(self.pll_to_be_cur)  # noqa
            new_playlist.want_to_be_renamed.connect(
                self.pll_to_be_renamed)  # noqa
            new_playlist.want_to_be_deleted.connect(
                self.pll_to_be_deleted)  # noqa

            self.playlist_boxes.append(new_playlist)
            self.scrollAreaWidgetLayout.addWidget(new_playlist)
        self.addNewListBox = AddNewListGroupbox(self)
        self.addNewListBox.want_to_add_list.connect(
            self.pll_to_be_added)  # noqa

        self.scrollAreaWidgetLayout.addWidget(self.addNewListBox)

        self.scrollAreaWidgetLayout.addItem(
            QtWidgets.QSpacerItem(0, 40,
                                  QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding))
        self.layout.addWidget(self.scrollArea)

        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidget.setGeometry(QRect(0, 0, 350, 344))
        self.scrollArea.setMinimumSize(QSize(300, 0))

    def add_playlist(self, playlist: Playlist):
        new_playlist = PlaylistGroupbox(playlist, self)
        new_playlist.want_to_be_cur.connect(self.pll_to_be_cur)  # noqa
        new_playlist.want_to_be_renamed.connect(self.pll_to_be_renamed)  # noqa
        new_playlist.want_to_be_deleted.connect(self.pll_to_be_deleted)  # noqa

        self.playlist_boxes.append(new_playlist)
        widgets_count = self.scrollAreaWidgetLayout.count()
        self.scrollAreaWidgetLayout.insertWidget(widgets_count - 2,
                                                 new_playlist)

    def pll_to_be_cur(self, name):
        if LOG_SLOTS:
            print(
                f"\033[0;39m[ALLPL]\033[0;0m понял, "
                f"что {name} хочет стать текущим")
        self.to_be_cur.emit(name)  # noqa

    def pll_to_be_added(self):
        if LOG_SLOTS:
            print(f"\033[0;39m[ALLPL]\033[0;0m хочет добавить новый плейлист")
        self.add_new_list.emit()  # noqa

    def pll_to_be_renamed(self, new_name):
        if LOG_SLOTS:
            print(
                f"\033[0;39m[ALLPL]\033[0;0m понял, что {self.sender().name} "  # noqa
                f"хочет сменить имя на {new_name}")
        self.rename_pllist.emit((self.sender().name, new_name))  # noqa

    def pll_to_be_deleted(self):
        if LOG_SLOTS:
            print(f"\033[0;39m[ALLPL]\033[0;0m удаляет кнопку "
                  f"плейлиста под именем {self.sender().name}")  # noqa
        self.sender().deleteLater()

        self.delete_pllist.emit(self.sender().name)  # noqa


class PlaylistGroupbox(QGroupBox):
    want_to_be_cur = pyqtSignal(str)
    want_to_be_renamed = pyqtSignal(str)
    want_to_be_deleted = pyqtSignal()

    def __init__(self, playlist: Playlist, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.playlist = playlist
        self.name = playlist.name
        self.meta = QLabel(playlist.meta())
        self.layout.addWidget(self.meta)
        self.layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            if LOG_SLOTS:
                print(
                    f"\033[0;34m[PLLST]\033[0;0m {self.name} "
                    f"хочет стать текущим")
            self.want_to_be_cur.emit(self.name)  # noqa
        elif event.button() == Qt.RightButton:
            if LOG_SLOTS:
                print(
                    f"\033[0;34m[PLLST]\033[0;0m {self.name} "
                    f"хочет открыть попап меню")

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        if self.name != "Все треки":
            contextMenu = QMenu(self)
            renameAct = contextMenu.addAction("Переименовать плейлист")
            deleteAct = contextMenu.addAction("Удалить плейлист")

            action = contextMenu.exec_(self.mapToGlobal(event.pos()))
            if action == deleteAct:
                if LOG_SLOTS:
                    print(
                        f"\033[0;34m[PLLST]\033[0;0m {self.name} "
                        f"хочет удалиться")
                self.want_to_be_deleted.emit()  # noqa
            elif action == renameAct:
                if LOG_SLOTS:
                    print(
                        f"\033[0;34m[PLLST]\033[0;0m {self.name} "
                        f"хочет переименоваться")
                text, ok = QInputDialog(self).getText(self,
                                                      ' ',
                                                      'Введите новое '
                                                      'название плейлиста:',
                                                      text=self.name)
                if ok and text != self.name:
                    self.want_to_be_renamed.emit(text)  # noqa
                    self.name = text
                    self.playlist.name = text
                    self.meta.setText(self.playlist.meta())

    def update_meta(self, playlist):
        self.meta.setText(playlist.meta())


class AddNewListGroupbox(QGroupBox):
    want_to_add_list = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_new_box_layout = QHBoxLayout(self)
        self.label = QLabel("Добавить плейлист\n")
        self.add_new_box_layout.addWidget(self.label)
        # self.add_new_box_layout.addItem(
        #     QtWidgets.QSpacerItem(0, 40,
        #                           QtWidgets.QSizePolicy.Minimum,
        #                           QtWidgets.QSizePolicy.Expanding))

    def mousePressEvent(self, event) -> None:
        if LOG_SLOTS:
            print(f"\033[0;34m[ADDER]\033[0;0m хочет добавить плейлист")
        self.want_to_add_list.emit()  # noqa


class TrackGroupbox(QGroupBox):
    want_play = pyqtSignal()
    swap_dir = pyqtSignal(str)
    want_to_remove = pyqtSignal()

    def __init__(self, composition: Composition, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.upDownLayout = QHBoxLayout()
        self.up = QPushButton("↑")
        self.down = QPushButton("↓")
        self.up.setMaximumSize(QSize(15, 30))
        self.down.setMaximumSize(QSize(15, 30))
        self.up.clicked.connect(self.swap_direction)
        self.down.clicked.connect(self.swap_direction)

        self.layout = QHBoxLayout(self)
        self.pic = QLabel()
        self.pic.setPixmap(make_pixmap(composition.image, 32, 32))
        self.name = composition.name
        self.author = composition.author
        self.meta = QLabel(repr(composition))
        self.meta_dur = QLabel(composition.dur())
        self.composition = composition
        self.layout.addLayout(self.upDownLayout)
        self.upDownLayout.addWidget(self.up)
        self.upDownLayout.addWidget(self.down)
        self.layout.addWidget(self.pic)
        self.layout.addWidget(self.meta)
        spacerItem = QtWidgets.QSpacerItem(40, 0,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.layout.addItem(spacerItem)
        self.layout.addWidget(self.meta_dur)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            if LOG_SLOTS:
                print(f"\033[0;35m[TRACK]\033[0;0m {self.name} хочет играть")
            self.want_play.emit()  # noqa
        elif event.button() == Qt.RightButton:
            if LOG_SLOTS:
                print(
                    f"\033[0;35m[TRACK]\033[0;0m {self.name} "
                    f"хочет открыть попап меню")

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        contextMenu = QMenu(self)
        if self.parent.name != "Все треки":
            removeAct = contextMenu.addAction("Удалить из плейлиста")
        plist_dict = self.parent.parent.playlist_boxes
        actions_dict = {
            contextMenu.addAction(f"Добавить в плейлист: {pl_name}"):
                plist_dict[pl_name] for
            pl_name in plist_dict.keys() if
            pl_name not in ("Все треки", self.parent.playlist.name)}

        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        if self.parent.name != "Все треки" and action == removeAct:  # noqa
            if LOG_SLOTS:
                print(f"\033[0;35m[TRACK]\033[0;0m {self.name} "
                      f"хочет удалиться из плейлиста {self.parent.playlist.name}")
            self.want_to_remove.emit()  # noqa
        else:
            add_to_this = actions_dict.get(action, False)
            if add_to_this:
                track_names = [track.data.name for track in
                               add_to_this.playlist]  # noqa
                if self.composition.name not in track_names:
                    add_to_this.append_track(self.composition)  # noqa

    def swap_direction(self):
        direction = self.sender().text()  # noqa
        if LOG_SLOTS:
            print(
                f"\033[0;35m[TRACK]\033[0;0m {self.name} хочет меняться {direction}")
        self.swap_dir.emit(direction)  # noqa


class CurPlaylistGroupbox(QGroupBox):
    updated = pyqtSignal()
    list_updated = pyqtSignal(int)

    def __init__(self, playlist: Playlist, parent):
        super().__init__()

        self.parent = parent

        self.playlist = playlist
        self.setTitle(playlist.name)

        self.layout = QVBoxLayout(self)

        self.scrollArea = QScrollArea()
        self.scrollAreaWidget = QWidget()
        self.scrollAreaWidgetLayout = QVBoxLayout(self.scrollAreaWidget)
        self.scrollArea.setWidget(self.scrollAreaWidget)

        self.track_boxes = []
        for song in playlist:
            new_track = TrackGroupbox(song.data, self)
            new_track.want_play.connect(self.play_slot)  # noqa
            new_track.swap_dir.connect(self.swap_tracks)  # noqa
            new_track.want_to_remove.connect(self.remove_track)  # noqa
            self.track_boxes.append(new_track)
            self.scrollAreaWidgetLayout.addWidget(new_track)

        if self.track_boxes:
            self.cur_track = self.track_boxes[0]
        else:
            self.cur_track = None

        spacerItem = QtWidgets.QSpacerItem(0, 40,
                                           QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.scrollAreaWidgetLayout.addItem(spacerItem)

        self.playlist_meta = QLabel(repr(playlist))

        self.layout.addWidget(self.playlist_meta)
        self.layout.addWidget(self.scrollArea)

        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumSize(QSize(500, 0))
        self.scrollAreaWidget.setGeometry(QRect(0, 0, 350, 344))

    def swap_tracks(self, direction):
        if LOG_SLOTS:
            print(
                f"\033[0;36m[CURPL]\033[0;0m Плейлист {self.playlist.name} "
                f"понял что {self.sender().name} "
                f"хочет поменяться местами {direction}")
        track = self.sender().composition  # noqa
        self.playlist.swap(track, direction)
        self.upd()

    def upd(self, index=-1):
        if LOG_SLOTS:
            print(
                f"\033[0;36m[CURPL]\033[0;0m "
                f"Плейлист {self.playlist.name} обновился")
        is_filled = False
        if self.track_boxes:
            self.track_boxes.clear()
            is_filled = True
        count = self.scrollAreaWidgetLayout.count()
        for i in range(0, count):
            item = self.scrollAreaWidgetLayout.itemAt(i)
            if i == count - 1:
                self.scrollAreaWidgetLayout.removeItem(item)
            else:
                item.widget().deleteLater()

        self.setTitle(self.playlist.name)
        for song in self.playlist:
            track = TrackGroupbox(song.data, self)
            track.swap_dir.connect(self.swap_tracks)
            track.want_play.connect(self.play_slot)
            track.want_to_remove.connect(self.remove_track)
            self.scrollAreaWidgetLayout.addWidget(track)
            self.track_boxes.append(track)

        spacerItem = QtWidgets.QSpacerItem(0, 40,
                                           QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.scrollAreaWidgetLayout.addItem(spacerItem)

        if not is_filled and self.track_boxes:
            self.cur_track = self.track_boxes[0]
            self.playlist.current_track = self.playlist.head.data

        self.update_meta()
        self.list_updated.emit(index)  # noqa

    @property
    def name(self):
        return self.playlist.name

    def play_slot(self):
        if LOG_SLOTS:
            print(
                f"\033[0;36m[CURPL]\033[0;0m Плейлист {self.playlist.name} "
                f"понял что {self.sender().name} хочет играть")
        self.playlist.current_track = self.sender().composition  # noqa
        self.updated.emit()  # noqa

    def remove_track(self):
        if LOG_SLOTS:
            print(f"\033[0;36m[CURPL]\033[0;0m Плейлист {self.playlist.name} "
                  f"удаляет трек {self.sender().name}")
        self.playlist.remove(self.sender().composition)  # noqa

        if len(self.playlist) and \
                self.playlist.current_track == self.sender().composition:
            self.playlist.current_track = self.playlist.head.data
        self.upd()

    def append_track(self, track):
        if LOG_SLOTS:
            print(f"\033[0;36m[CURPL]\033[0;0m Плейлист {self.playlist.name} "
                  f"добавляет трек {track}")
        self.playlist.append(track)
        self.upd()

    def update_meta(self):
        self.playlist_meta.setText(str(self.playlist))


class PlayLineGroupBox(QGroupBox):
    def __init__(self, playlist: Playlist):
        super().__init__()
        self.cur_playlist = playlist

        self.player = QMediaPlayer()
        self.player.setMedia(
            QMediaContent(
                QUrl.fromLocalFile(self.cur_playlist.current_track.path)))

        self.player.positionChanged.connect(self.progress_tick)
        self.player.mediaStatusChanged.connect(self.media_status_handler)

        self.setTitle(self.cur_playlist.name)

        self.layout = QVBoxLayout(self)

        self.metaLayout = QHBoxLayout(self)
        self.pic = QLabel()
        self.pic.setPixmap(
            make_pixmap(self.cur_playlist.current_track.image, 64, 64))
        self.name = QLabel(repr(self.cur_playlist.current_track))

        self.metaLayout.addWidget(self.pic)
        self.metaLayout.addWidget(self.name)

        self.metaLayout.addItem(
            QtWidgets.QSpacerItem(1000, 0, QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Minimum))

        self.trackProgressLayout = QHBoxLayout(self)
        self.cur_dur = QLabel('00:00')
        self.dur = QLabel(self.cur_playlist.current_track.dur())

        self.bar = QSlider()
        self.bar.setOrientation(Qt.Horizontal)
        self.bar.setRange(
            0, int(self.cur_playlist.current_track.duration))
        self.bar.setValue(0)
        self.bar.sliderReleased.connect(self.upd_progress)

        self.trackProgressLayout.addWidget(self.cur_dur)
        self.trackProgressLayout.addWidget(self.bar)
        self.trackProgressLayout.addWidget(self.dur)

        self.controlsLayout = QHBoxLayout(self)
        self.prev = QPushButton("<-")
        self.pause = QPushButton("||")
        self.play = QPushButton("|>")
        self.next = QPushButton("->")

        self.pause.clicked.connect(self.pause_f)
        self.play.clicked.connect(self.play_f)
        self.prev.clicked.connect(self.prev_f)
        self.next.clicked.connect(self.next_f)

        self.controlsLayout.addWidget(self.prev)
        self.controlsLayout.addWidget(self.pause)
        self.controlsLayout.addWidget(self.play)
        self.controlsLayout.addWidget(self.next)

        self.pause.hide()

        self.layout.addLayout(self.metaLayout)
        self.layout.addLayout(self.trackProgressLayout)
        self.layout.addLayout(self.controlsLayout)

    def progress_tick(self):
        self.cur_dur.setText(duration_from_ms(self.player.position()))
        self.bar.setValue(self.bar.value() + 1)

    def upd_progress(self):
        self.player.setPosition(self.bar.value() * 1000)

    def media_status_handler(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_f()
            self.play_f()
        if status == 2:
            self.play_f()

    def play_f(self):
        self.play.hide()
        self.pause.show()
        self.player.play()

    def pause_f(self):
        self.pause.hide()
        self.play.show()
        self.player.pause()

    def prev_f(self):
        self.cur_playlist.previous_track()
        self.update_playline()
        self.play_f()

    def next_f(self):
        self.cur_playlist.next_track()
        self.update_playline()
        self.play_f()

    def make_pll_cur(self, playlist: Playlist):
        if LOG_SLOTS:
            print(f"\033[0;36m[PLINE]\033[0;0m Текущий плейлист обновился")
        self.cur_playlist = playlist
        self.setTitle(self.cur_playlist.name)
        self.update_playline()

    def update_playline(self):
        if LOG_SLOTS:
            print(f"\033[0;36m[PLINE]\033[0;0m Плэйлайн обновился")
        self.player.setMedia(QMediaContent(
            QUrl.fromLocalFile(self.cur_playlist.current_track.path)))
        self.pic.setPixmap(
            make_pixmap(self.cur_playlist.current_track.image, 64, 64))
        self.name.setText(repr(self.cur_playlist.current_track))
        self.dur.setText(
            duration_from_seconds(self.cur_playlist.current_track.duration))
        self.bar.setRange(
            0, int(self.cur_playlist.current_track.duration))
        self.bar.setValue(0)
        self.play_f()


if __name__ == '__main__':
    app = QApplication(argv)
    ex = MainUI()
    ex.show()
    app.exec_()
    exit()
