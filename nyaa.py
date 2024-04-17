"""Simple parsing  script to obtain magnet link of a torrent"""
from bs4 import BeautifulSoup
import os
import signal
import subprocess
import sys
import re
import requests
from animeElem import AnimeElem


class NyaaSiDownloader:
    """Torrent magnet link"""
    # text format
    window = None
    tabella = None
    magnet_window = None
    workflow: bool
    bold_text = "\033[1m"
    underscore = "\x1b[4m"
    reset_clr = "\x1b[0m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    magenta = "\x1b[35m"
    cyan = "\x1b[36m"
    white = "\x1b[37m"
    categories = ["0_0", "1_0", "1_1", "1_2", "1_3", "1_4", "2_0", "2_1", "2_2", "3_0", "3_1",
                  "3_2", "3_3", "4_0", "4_1", "4_2", "4_3", "4_4", "5_0", "5_1", "5_2", "6_0", "6_1", "6_2"]
    search_type = categories[0]
    # config
    autoadd = False
    # end config
    animeElements: list = []

    @staticmethod
    def verify_magnet_link(magnet_link: str) -> bool:
        """verify a magnet link using regex"""
        result = re.fullmatch(
            "^magnet:\?xt=urn:btih:[0-9a-fA-F]{40,}.*$", magnet_link)
        if result is not None:
            return True
        else:
            return False

    def searchnyaasi(self, req: requests.models.Response) -> None:
        """Parsing function"""
        for parsed in BeautifulSoup(req.text, "html.parser").findAll('tr'):
            size = ""
            seed = ""
            leech = ""
            date_t = ""
            title = ""
            magnet = ""
            type_torr = ""
            x = 0
            for elem in parsed.findAll('img', alt=True):
                type_torr = elem['alt']
            for elem in parsed.findAll('td', attrs={'colspan': '2'}):
                for k in elem:
                    if k.string is not None:
                        if len(k.string) > 5:
                            title = k.string
            for elem in parsed.findAll('td', attrs={'class': 'text-center'}):
                for k in elem:
                    if x == 3:
                        # sometimes there is no download link
                        try:
                            magnet = k.get('href')
                        except AttributeError:
                            title = ""
                    if x == 5:
                        size = k.string
                    if x == 6:
                        date_t = k.string
                    if x == 7:
                        seed = k.string
                    if x == 8:
                        leech = k.string
                    x += 1
                leech = elem.text
            if len(title) > 1:
                temp: AnimeElem = AnimeElem(name=title, size=float(size.split(" ")[0]),
                                            type_t=size.split(" ")[1], seed=seed,
                                            leech=leech, movie_type=type_torr, date=date_t, magnet=magnet)
                self.animeElements.append(temp)
            self.animeElements.sort(key=lambda x: x.size, reverse=True)

    @staticmethod
    def print_elem_gui(elem: AnimeElem, torrent: int) -> None:
        """Print torrent element"""
        from PySide6.QtWidgets import QTableWidgetItem
        title_t = elem.name
        min_pos = 0
        max_pos = 95
        NyaaSiDownloader.tabella.setItem(
            torrent, 0, QTableWidgetItem(title_t[min_pos:max_pos]))
        NyaaSiDownloader.tabella.setItem(
            torrent, 1, QTableWidgetItem(f"{str(elem.size)} {elem.type_t}"))
        NyaaSiDownloader.tabella.setItem(
            torrent, 2, QTableWidgetItem(f"{elem.seed}"))
        NyaaSiDownloader.tabella.setItem(
            torrent, 3, QTableWidgetItem(f"{elem.leech}"))
        NyaaSiDownloader.tabella.setItem(
            torrent, 4, QTableWidgetItem(f"{elem.movie_type}"))
        NyaaSiDownloader.tabella.setItem(
            torrent, 5, QTableWidgetItem(f"{elem.date}"))
        NyaaSiDownloader.tabella.resizeColumnsToContents()

    def print_elem(self, elem: AnimeElem) -> None:
        """Print torrent element"""
        title_t = AnimeElem.name
        min_pos = 0
        max_pos = 95
        print(
            f" {self.cyan}TITLE: {title_t[min_pos:max_pos]}{self.reset_clr}")
        while max_pos < len(title_t):
            min_pos += 95
            max_pos += 95
            print(
                f" {self.cyan}       {title_t[min_pos:max_pos]}{self.reset_clr}")
        print(
            f" {self.red}DATE: {elem.date}{self.reset_clr}")
        print(
            f" {self.green}DIM: {str(elem.size)} {elem.type_t} {self.reset_clr}")
        print(
            f" {self.yellow}SEED: {elem.seed}{self.reset_clr}")
        print(
            f" {self.white}LEECH: {elem.leech}{self.reset_clr}")
        print(
            f" {self.magenta}TYPE: {elem.movie_type}{self.reset_clr}")

    def searchnyaasi_request(self, name_s: str) -> None:
        """Request to the torrent site"""
        # sending get request and saving the response as response object
        url = f"https://nyaa.si/?f=0&c={self.search_type}&q=/{name_s}"
        req = requests.get(url=url, params={}, allow_redirects=False)
        self.searchnyaasi(req)

    def avvia_ricerca(self) -> None:
        """avvio ricerca GUI"""
        from PySide6.QtWidgets import QTableWidget, QPushButton, QApplication, QComboBox
        # reset to allow multiple search
        self.animeElements = []
        self.category = self.window.findChild(
            QComboBox, "category")
        self.search_type = self.categories[self.category.currentIndex(
        )]
        name_input = self.titolo.text()
        self.searchnyaasi_request(str(name_input))
        # populate tabel
        torrent = 1
        NyaaSiDownloader.tabella = NyaaSiDownloader.window.findChild(
            QTableWidget, "tableWidget")
        NyaaSiDownloader.seleziona = NyaaSiDownloader.window.findChild(
            QPushButton, "select")
        NyaaSiDownloader.seleziona.clicked.connect(self.get_selected_element)
        NyaaSiDownloader.tabella.clearContents()
        NyaaSiDownloader.tabella.setRowCount(0)
        QApplication.processEvents()
        for elem in self.animeElements:
            pos = torrent - 1
            NyaaSiDownloader.tabella.insertRow(pos)
            self.print_elem_gui(elem, pos)
            torrent += 1

    def get_selected_element(self) -> None:
        # GUI (first time only)
        self.autoadd = self.add.isChecked()
        # get multiple selection
        items = self.tabella.selectedItems()
        for item in items:
            # only 1 item in a row
            if item.column() == 1:
                # start download with each selected row
                magnet = (self.animeElements[item.row()]).magnet
                self.start(magnet)
        return

    def choose(self) -> None:
        """Select torrent"""
        # write _____________
        number: int = 0
        print(f'{self.underscore}' + ' ' *
              120 + f'{self.reset_clr}\n')
        found = 0
        while found == 0:
            if self.animeElements is []:
                print(
                    f"{self.red}No Torrent Found{self.reset_clr}")
                sys.exit(0)
            if self.workflow:
                number = 1
            else:
                try:
                    number = int(input('Choose torrent: '))
                except ValueError:
                    print(
                        f"\n{self.red}Not Valid!!{self.reset_clr}\n")
                    self.choose()
            found = 1
            item_dict = self.animeElements[number - 1]
            self.print_elem(item_dict)
            conf = ""
            if self.workflow:
                conf = 'y'
            while conf.lower() not in ['y', 'n']:
                conf = input("\ny to confirm, n to repeat: ")
            if conf.lower() == 'n':
                found = 0
            elif conf.lower() == 'y':
                number -= 1  # indice di un array
                # controllo che number sia una scelta valida:
                if len(self.animeElements) > number >= 0:
                    magnet = self.animeElements[number].magnet
                    self.start(magnet)
                else:
                    print(
                        f"{self.red}Not Valid{self.reset_clr}")

    def get_magnet(self, position: int) -> None:
        """function to get magnet link"""
        magnet_link = self.animeElements[position].magnet
        self.start(magnet_link)

    def start(self, magnet_link: str) -> None:
        """start gui search"""
        # check magnet validity
        if not self.verify_magnet_link(magnet_link):
            print(
                f"{self.red}Not a valid Magnet{self.reset_clr}")
            sys.exit(0)
        if self.autoadd:
            done = True
            # avvio il magnet
            if sys.platform.startswith('linux'):
                try:
                    subprocess.Popen(['xdg-open', magnet_link])
                except subprocess.CalledProcessError:
                    done = False
            elif sys.platform.startswith('win32'):
                os.startfile(magnet_link)
            elif sys.platform.startswith('cygwin'):
                os.startfile(magnet_link)
            elif sys.platform.startswith('darwin'):
                try:
                    subprocess.Popen(['open', magnet_link])
                except subprocess.CalledProcessError:
                    done = False
            else:
                try:
                    subprocess.Popen(['xdg-open', magnet_link])
                except subprocess.CalledProcessError:
                    done = False
            if done:
                print(
                    f'\n{self.green}Success{self.reset_clr}')
            else:  # ho incontrato un errore
                if self.gui:
                    from PySide6.QtWidgets import QTextEdit
                    text = NyaaSiDownloader.magnet_window.findChild(
                        QTextEdit, "magnet_link")
                    text.insertPlainText(magnet_link)
                    text.insertPlainText("\n")
                    text.insertPlainText("\n")
                    NyaaSiDownloader.magnet_window.show()
                else:
                    print(
                        f"\nMagnet:{self.red}{magnet_link}{self.reset_clr}\n")
        else:
            if self.gui:
                from PySide6.QtWidgets import QTextEdit
                text: QTextEdit = NyaaSiDownloader.magnet_window.findChild(
                    QTextEdit, "magnet_link")
                # text.clear()
                text.insertPlainText(magnet_link)
                text.insertPlainText("\n")
                text.insertPlainText("\n")
                NyaaSiDownloader.magnet_window.show()
            else:
                print(
                    f"\nMagnet:{self.red}{magnet_link}{self.reset_clr}\n")

    def __init__(self, gui: bool, wf: bool = False) -> None:
        self.category = None
        self.workflow = wf
        self.gui = gui
        self_wrapp = self
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        if self.gui:
            # GUI import
            from PySide6.QtWidgets import QCheckBox, QPushButton, QLineEdit
            from PySide6.QtCore import QObject
            from PySide6.QtGui import QKeyEvent

            class KeyPressEater(QObject):
                """event filter """

                def eventFilter(self, widget, event: QKeyEvent):
                    from PySide6.QtCore import QEvent, Qt
                    if event.type() == QEvent.KeyPress:
                        key = event.key()
                        if key == Qt.Key_Return:
                            self_wrapp.avvia_ricerca()
                    return False

            self.filtro = KeyPressEater()
            self.titolo = NyaaSiDownloader.window.findChild(
                QLineEdit, "titolo")
            self.cerca = NyaaSiDownloader.window.findChild(
                QPushButton, "cerca")
            self.add = NyaaSiDownloader.window.findChild(
                QCheckBox, "add")
            self.cerca.clicked.connect(self.avvia_ricerca)
            self.titolo.installEventFilter(
                self.filtro)
        else:
            if len(sys.argv) == 1:
                name_input = input('Nome Film da cercare: ').strip()
            else:
                name_input = sys.argv[1]
                for elem in sys.argv[2:]:
                    name_input += '+' + elem
            self.searchnyaasi_request(str(name_input))
            # print list
            torrent = 1
            for elem in self.animeElements:
                # write _____________
                print(f'{self.underscore}' + ' ' *
                      120 + f'{self.reset_clr}\n')
                print(
                    f" {self.bold_text}Torrent {torrent} :{self.reset_clr}")
                self.print_elem(elem)
                torrent += 1
            self.choose()

    @classmethod
    def sig_handler(cls, _signo, _stack_frame):
        """Catch ctr+c signal"""
        print("\n")
        sys.exit(0)
