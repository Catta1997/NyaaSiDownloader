'''Simple parsing  script to obtain magnet link of a torrent'''
from bs4 import BeautifulSoup
import json
import os
import signal
import subprocess
import sys
import re
import requests


class NyaaSiDownloader():
    '''Torrent magnet link'''
    # text format
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

    json_torrent = '''
    {
        "Torrent": [
            ]
    }
    '''

    @staticmethod
    def verify_magnet_link(magnet_link):
        '''verify a magnet link using regex'''
        result = re.fullmatch(
            "^magnet:\?xt=urn:btih:[0-9a-fA-F]{40,}.*$", magnet_link)
        if result is not None:
            return True
        else:
            return False

    @staticmethod
    def searchnyaasi(req):
        '''Parsing function'''
        # extracting data in json format
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
                        if len(k.string)>5:
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
                leech = (elem.text)
            # create a json with torrent info
            if len(title) > 1:
                temp = {
                    'name': title,
                    'size': float(size.split(" ")[0]),
                    'type': size.split(" ")[1],
                    'seed': seed,
                    'leech': leech,
                    'movie_type': type_torr,
                    'date': date_t,
                    'magnet': magnet
                }
                data = json.loads(NyaaSiDownloader.json_torrent)
                data['Torrent'].append(temp)
                NyaaSiDownloader.json_torrent = json.dumps(data, indent=4)
                sorted_obj = dict(data)
                sorted_obj['Torrent'] = sorted(
                    data['Torrent'], key=lambda pos: pos['size'], reverse=True)
                NyaaSiDownloader.json_torrent = json.dumps(
                    sorted_obj, indent=4)


    @staticmethod
    def print_elem_gui(elem, torrent):
        '''Print torrent element'''
        from PySide2.QtWidgets import QTableWidgetItem
        title_t = elem['name']
        min_pos = 0
        max_pos = 95
        NyaaSiDownloader.tabella.setItem(
            torrent, 0, QTableWidgetItem(title_t[min_pos:max_pos]))
        NyaaSiDownloader.tabella.setItem(
            torrent, 1, QTableWidgetItem(f"{str(elem['size'])} {elem['type']}"))
        NyaaSiDownloader.tabella.setItem(
            torrent, 2, QTableWidgetItem(f"{elem['seed']}"))
        NyaaSiDownloader.tabella.setItem(
            torrent, 3, QTableWidgetItem(f"{elem['leech']}"))
        NyaaSiDownloader.tabella.setItem(
            torrent, 4, QTableWidgetItem(f"{elem['movie_type']}"))
        NyaaSiDownloader.tabella.setItem(
            torrent, 5, QTableWidgetItem(f"{elem['date']}"))
        NyaaSiDownloader.tabella.resizeColumnsToContents()

    @staticmethod
    def print_elem(elem):
        '''Print torrent element'''
        title_t = elem['name']
        min_pos = 0
        max_pos = 95
        print(
            f" {NyaaSiDownloader.cyan}TITLE: {title_t[min_pos:max_pos]}{NyaaSiDownloader.reset_clr}")
        while max_pos < len(title_t):
            min_pos += 95
            max_pos += 95
            print(
                f" {NyaaSiDownloader.cyan}       {title_t[min_pos:max_pos]}{NyaaSiDownloader.reset_clr}")
        print(
            f" {NyaaSiDownloader.red}DATE: {elem['date']}{NyaaSiDownloader.reset_clr}")
        print(
            f" {NyaaSiDownloader.green}DIM: {str(elem['size'])} {elem['type']} {NyaaSiDownloader.reset_clr}")
        print(
            f" {NyaaSiDownloader.yellow}SEED: {elem['seed']}{NyaaSiDownloader.reset_clr}")
        print(
            f" {NyaaSiDownloader.white}LEECH: {elem['leech']}{NyaaSiDownloader.reset_clr}")
        print(
            f" {NyaaSiDownloader.magenta}TYPE: {elem['movie_type']}{NyaaSiDownloader.reset_clr}")

    @staticmethod
    def searchnyaasi_request(name_s):
        '''Request to the torrent site'''
        # sending get request and saving the response as response object
        url = f"https://nyaa.si/?f=0&c={NyaaSiDownloader.search_type}&q=/{name_s}"
        req = requests.get(url=url, params={})
        NyaaSiDownloader.searchnyaasi(req)

    def avvia_ricerca(self):
        '''avvio ricerca GUI'''
        from PySide2.QtWidgets import QTableWidget, QPushButton, QApplication, QComboBox
        # reset to allow multiple search
        NyaaSiDownloader.json_torrent = '''
    {
        "Torrent": [
            ]
    }
    '''
        NyaaSiDownloader.category = NyaaSiDownloader.window.findChild(QComboBox, "category")
        NyaaSiDownloader.search_type = NyaaSiDownloader.categories[NyaaSiDownloader.category.currentIndex()]
        name_input = NyaaSiDownloader.titolo.text()
        NyaaSiDownloader.searchnyaasi_request(str(name_input))
        # populate tabel
        torrent = 1
        data = json.loads(NyaaSiDownloader.json_torrent)
        NyaaSiDownloader.tabella = NyaaSiDownloader.window.findChild(
            QTableWidget, "tableWidget")
        NyaaSiDownloader.seleziona = NyaaSiDownloader.window.findChild(
            QPushButton, "select")
        NyaaSiDownloader.seleziona.clicked.connect(
            lambda: NyaaSiDownloader.get_selected_element(self))
        NyaaSiDownloader.tabella.clearContents()
        NyaaSiDownloader.tabella.setRowCount(0)
        QApplication.processEvents()
        for elem in data['Torrent']:
            pos = torrent - 1
            NyaaSiDownloader.tabella.insertRow(pos)
            NyaaSiDownloader.print_elem_gui(elem, pos)
            torrent += 1

    def get_selected_element(self):
        # GUI (first time only)
        NyaaSiDownloader.autoadd = NyaaSiDownloader.add.isChecked()
        # get multiple selection
        items = NyaaSiDownloader.tabella.selectedItems()
        item_dict = json.loads(NyaaSiDownloader.json_torrent)['Torrent']
        for item in items:
            # only 1 item in a row
            if item.column() == 1:
                # start download with each selected row
                magnet = item_dict[item.row()]['magnet']
                NyaaSiDownloader.start(self, magnet)
                NyaaSiDownloader.get_magnet(self, item.row())
        return

    def choose(self):
        '''Select torrent'''
        # write _____________
        print(f'{NyaaSiDownloader.underscore}'+' ' *
              120+f'{NyaaSiDownloader.reset_clr}\n')
        found = 0
        while found == 0:
            item_dict = json.loads(NyaaSiDownloader.json_torrent)
            try:
                number = int(input('Choose torrent: '))
            except ValueError:
                print(
                    f"\n{NyaaSiDownloader.red}Not Valid!!{NyaaSiDownloader.reset_clr}\n")
                NyaaSiDownloader.choose(self)
            found = 1
            item_dict = json.loads(NyaaSiDownloader.json_torrent)[
                'Torrent'][number-1]
            NyaaSiDownloader.print_elem(item_dict)
            conf = ""
            while conf.lower() not in ['y', 'n']:
                conf = input("\ny to confirm, n to repeat: ")
            if conf.lower() == 'n':
                found = 0
            elif (conf.lower() == 'y'):
                number -= 1  # indice di un array
                # controllo che number sia una scelta valida:
                item_dict = json.loads(NyaaSiDownloader.json_torrent)
                if number < len(item_dict['Torrent']) and number >= 0:
                    magnet = item_dict['Torrent'][number]['magnet']
                    NyaaSiDownloader.start(self, magnet)
                else:
                    print(
                        f"{NyaaSiDownloader.red}Not Valid{NyaaSiDownloader.reset_clr}")

    def get_magnet(self, position):
        '''function to get magnet link'''
        item_dict = json.loads(NyaaSiDownloader.json_torrent)[
            'Torrent'][position]
        magnet_link = item_dict['magnet']
        NyaaSiDownloader.start(self, magnet_link)

    def start(self, magnet_link):
        '''start gui search'''
        # check magnet validity
        if (not NyaaSiDownloader.verify_magnet_link(magnet_link)):
            print(
                f"{NyaaSiDownloader.red}Not a valid Magnet{NyaaSiDownloader.reset_clr}")
            sys.exit(0)
        if (NyaaSiDownloader.autoadd):
            done = True
            # avvio il magnet
            if sys.platform.startswith('linux'):
                try:
                    subprocess.Popen(['xdg-open', magnet_link])
                except subprocess.CalledProcessError:
                    done = False
            elif sys.platform.startswith('win32'):
                done = os.startfile(magnet_link)  # check false
            elif sys.platform.startswith('cygwin'):
                done = os.startfile(magnet_link)  # check false
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
                    f'\n{NyaaSiDownloader.green}Success{NyaaSiDownloader.reset_clr}')
            else:  # ho incontrato un errore
                if (self.gui):
                    from PySide2.QtWidgets import QTextEdit
                    text = NyaaSiDownloader.magnet_window.findChild(
                        QTextEdit, "magnet_link")
                    text.insertPlainText(magnet_link)
                    NyaaSiDownloader.magnet_window.show()
                else:
                    print(
                        f"\nMagnet:{NyaaSiDownloader.red}{magnet_link}{NyaaSiDownloader.reset_clr}\n")
        else:
            if (self.gui):
                from PySide2.QtWidgets import QTextEdit
                text = NyaaSiDownloader.magnet_window.findChild(
                    QTextEdit, "magnet_link")
                text.insertPlainText(magnet_link)
                NyaaSiDownloader.magnet_window.show()
            else:
                print(
                    f"\nMagnet:{NyaaSiDownloader.red}{magnet_link}{NyaaSiDownloader.reset_clr}\n")

    def __init__(self, gui):
        self.gui = gui
        self_wrapp = self
        signal.signal(signal.SIGTERM, NyaaSiDownloader.sig_handler)
        signal.signal(signal.SIGINT, NyaaSiDownloader.sig_handler)
        if (self.gui):
            # GUI import
            from PySide2.QtWidgets import QCheckBox, QPushButton, QLineEdit
            from PySide2.QtCore import QObject

            class KeyPressEater(QObject):
                '''event filter '''

                def eventFilter(self, widget, event):
                    from PySide2.QtCore import QEvent, Qt
                    if (event.type() == QEvent.KeyPress):
                        key = event.key()
                        if key == Qt.Key_Return:
                            NyaaSiDownloader.avvia_ricerca(self_wrapp)
                    return False
            NyaaSiDownloader.filtro = KeyPressEater()
            NyaaSiDownloader.titolo = NyaaSiDownloader.window.findChild(
                QLineEdit, "titolo")
            NyaaSiDownloader.cerca = NyaaSiDownloader.window.findChild(
                QPushButton, "cerca")
            NyaaSiDownloader.add = NyaaSiDownloader.window.findChild(
                QCheckBox, "add")
            NyaaSiDownloader.cerca.clicked.connect(
                lambda: NyaaSiDownloader.avvia_ricerca(self_wrapp))
            NyaaSiDownloader.titolo.installEventFilter(
                NyaaSiDownloader.filtro)
        else:
            if len(sys.argv) == 1:
                name_input = input('Nome Film da cercare: ').strip()
            else:
                name_input = sys.argv[1]
                for elem in sys.argv[2:]:
                    name_input += '+' + elem
            NyaaSiDownloader.searchnyaasi_request(str(name_input))
            # print list
            torrent = 1
            data = json.loads(NyaaSiDownloader.json_torrent)
            for elem in data['Torrent']:
                # write _____________
                print(f'{NyaaSiDownloader.underscore}' + ' ' *
                      120 + f'{NyaaSiDownloader.reset_clr}\n')
                print(
                    f" {NyaaSiDownloader.bold_text}Torrent {torrent} :{NyaaSiDownloader.reset_clr}")
                NyaaSiDownloader.print_elem(elem)
                torrent += 1
            NyaaSiDownloader.choose(self)

    @classmethod
    def sig_handler(cls, _signo, _stack_frame):
        '''Catch ctr+c signal'''
        print("\n")
        sys.exit(0)
