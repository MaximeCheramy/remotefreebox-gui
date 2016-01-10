import sys
import signal
from PyQt4 import uic
from PyQt4.QtGui import QWidget, QMainWindow, QApplication, QPixmap, QFontMetrics, QIcon
from PyQt4.QtCore import QUrl, QByteArray, Qt, pyqtSignal, QThread
from PyQt4.QtNetwork import QNetworkRequest, QNetworkAccessManager
from remotefreebox import FreeboxController
import urllib.request
import json
import time


def get(url):
    response = urllib.request.urlopen(url)
    html = response.read().decode("utf-8")
    return json.loads(html)


def setElidedText(label, text):
    metrics = QFontMetrics(label.font())
    elidedText = metrics.elidedText(text, Qt.ElideRight, label.width())
    label.setText(elidedText)


class LabelDownloader(QNetworkAccessManager):
    def __init__(self, url, label=None, btn=None):
        QNetworkAccessManager.__init__(self)
        self.messageBuffer = QByteArray()
        self.label = label
        self.btn = btn
        self.frmt = "PNG" if url.rsplit('.', 1)[1] == 'png' else "JPG"
        request = QNetworkRequest(QUrl(url))
        self.reply = self.get(request)
        self.reply.finished.connect(self.slotFinished)
        self.reply.readyRead.connect(self.slotReadData)

    def slotReadData(self):
        self.messageBuffer += self.reply.readAll()

    def slotFinished(self):
        pixmap = QPixmap()
        pixmap.loadFromData(self.messageBuffer, self.frmt)
        if self.label:
            self.label.setPixmap(pixmap)
        if self.btn:
            self.btn.setIcon(QIcon(pixmap))


class Program(QWidget):
    def __init__(self, uuid, name, chan, fbx, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi('program.ui', self)
        self.fbx = fbx
        self.uuid = uuid
        self.chan = chan
        setElidedText(self.channelName, name)
        self._l1 = LabelDownloader("http://mafreebox.freebox.fr/api/v3/tv/img/channels/logos68x60/"
                                   + uuid + ".png", btn=self.channelImg)
        try:
            self.retrieveProgram()
        except:
            pass

    def retrieveProgram(self):
        url = "http://mafreebox.freebox.fr/api/v3/tv/epg/highlights/{}/{}/".format(self.uuid, int(time.time()))
        obj = get(url)
        res = None
        i = 0
        while i < len(obj["result"]) and obj["result"][i]["date"] <= time.time():
            res = obj["result"][i]
            i += 1

        start = res["date"]
        duration = res["duration"]
        spent = int(time.time()) - start

        self.progressBar.setMaximum(duration)
        self.progressBar.setValue(spent)

        self.title.setText(res["title"])
        self.description.setText(res.get("sub_title", ""))
        picture = res.get("picture", None)
        if picture:
            self._l2 = LabelDownloader("http://mafreebox.freebox.fr" + picture, self.previewImg)

        self.channelImg.clicked.connect(self.switch)

    def switch(self, event):
        print(str(self.chan))
        for i in str(self.chan):
            self.fbx.press(i)


class FreeboxThread(QThread):
    connected = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.is_connected = False
        self.fbx = None
        self.q = []

    def press(self, cmd):
        self.q.append(cmd)
        if self.is_connected:
            while self.q:
                self.fbx.press(self.q.pop())

    def run(self):
        self.fbx = FreeboxController(self.connected_cb)

    def connected_cb(self, el):
        self.is_connected = True
        self.connected.emit()


class ProgramLoader(QThread):
    channelReceived = pyqtSignal(tuple)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        channels = get("http://mafreebox.freebox.fr/api/v3/tv/channels")["result"]

        obj = get("http://mafreebox.freebox.fr/api/v3/tv/bouquets/49/channels")
        if obj["success"]:
            for r in sorted(obj["result"], key=lambda x: x['number']):
                if r["available"]:
                    uuid = r["uuid"]
                    self.channelReceived.emit((uuid, channels[uuid]["name"], r["number"]))


class Freebox(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('freebox.ui', self)

        self.fbx = FreeboxThread()
        self.fbx.start()

        self.powerButton.clicked.connect(self.buttonCallback("Power"))
        self.avButton.clicked.connect(self.buttonCallback("AV"))
        self.zeroButton.clicked.connect(self.buttonCallback("0"))
        self.oneButton.clicked.connect(self.buttonCallback("1"))
        self.twoButton.clicked.connect(self.buttonCallback("2"))
        self.threeButton.clicked.connect(self.buttonCallback("3"))
        self.fourButton.clicked.connect(self.buttonCallback("4"))
        self.fiveButton.clicked.connect(self.buttonCallback("5"))
        self.sixButton.clicked.connect(self.buttonCallback("6"))
        self.sevenButton.clicked.connect(self.buttonCallback("7"))
        self.eightButton.clicked.connect(self.buttonCallback("8"))
        self.nineButton.clicked.connect(self.buttonCallback("9"))
        self.upButton.clicked.connect(self.buttonCallback("Up"))
        self.downButton.clicked.connect(self.buttonCallback("Down"))
        self.leftButton.clicked.connect(self.buttonCallback("Left"))
        self.rightButton.clicked.connect(self.buttonCallback("Right"))
        self.enterButton.clicked.connect(self.buttonCallback("Enter"))
        self.backButton.clicked.connect(self.buttonCallback("Back"))
        self.searchButton.clicked.connect(self.buttonCallback("Search"))
        self.menuButton.clicked.connect(self.buttonCallback("Menu"))
        self.infoButton.clicked.connect(self.buttonCallback("Info"))
        self.freeButton.clicked.connect(self.buttonCallback("Free"))
        self.incVolumeButton.clicked.connect(self.buttonCallback("Vol+"))
        self.decVolumeButton.clicked.connect(self.buttonCallback("Vol-"))
        self.muteButton.clicked.connect(self.buttonCallback("Mute"))
        self.recordButton.clicked.connect(self.buttonCallback("Record"))
        self.prevChanButton.clicked.connect(self.buttonCallback("Chan-"))
        self.nextChanButton.clicked.connect(self.buttonCallback("Chan+"))
        self.rewindButton.clicked.connect(self.buttonCallback("Rewind"))
        self.playPauseButton.clicked.connect(self.buttonCallback("Play/Pause"))
        self.forwardButton.clicked.connect(self.buttonCallback("Fast Forward"))

        self.programLoader = ProgramLoader()
        self.programLoader.channelReceived.connect(self.addProgram)
        self.programLoader.start()

    def addProgram(self, event):
        uuid, name, number = event
        p = Program(uuid, name, number, self.fbx)
        self.listofPrograms.layout().addWidget(p)

    def buttonCallback(self, action):
        return lambda: self.fbx.press(action)


app = QApplication(sys.argv)
freebox = Freebox()
freebox.show()
signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.exit(app.exec_())
