import nyaa
import sys
from random import SystemRandom
# GUI import
try:
    from PySide2.QtCore import QFile, QCoreApplication, Qt
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtWidgets import QApplication, QLabel
    from PySide2.QtGui import QIcon, QPixmap
except ModuleNotFoundError:
    bold_text = "\033[1m"
    red = "\x1b[31m"
    reset_clr = "\x1b[0m"
    print(f"{bold_text}{red}Install requirments_gui.txt{reset_clr}")
    sys.exit(0)

QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
app = QApplication(sys.argv)

rand = SystemRandom()
icon = rand.randrange(1,15)
app.setWindowIcon(QIcon(f"Resources/icon_{icon}.png"))
install_ui = 'Resources/install.ui'
magnet_ui = 'Resources/show.ui'
ui_file = QFile(install_ui)
ui_magnet = QFile(magnet_ui)
loader = QUiLoader()
nyaa.NyaaSiDownloader.window = loader.load(ui_file)
nyaa.NyaaSiDownloader.magnet_window = loader.load(magnet_ui)
nyaa.NyaaSiDownloader.logo = nyaa.NyaaSiDownloader.window.findChild(QLabel, 'logo')
nyaa.NyaaSiDownloader.window.setWindowTitle('NyaaSiDownloader')
pixmap = QPixmap('Resources/nyaa_logo.png')
nyaa.NyaaSiDownloader.logo.setPixmap(pixmap)
ui_file.close()
ui_magnet.close()
x = nyaa.NyaaSiDownloader(True)
nyaa.NyaaSiDownloader.window.show()
sys.exit(app.exec_())
