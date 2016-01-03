import sys
from PyQt4 import QtGui, uic
from remotefreebox import FreeboxController


class Freebox(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        uic.loadUi('freebox.ui', self)
        self.fbx = FreeboxController()

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

    def buttonCallback(self, action):
        return lambda: self.fbx.press(action)

app = QtGui.QApplication(sys.argv)
freebox = Freebox()
freebox.show()
app.exec_()
