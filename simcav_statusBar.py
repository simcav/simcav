from PyQt5 import QtCore, QtGui, QtWidgets


class StatusBar():
    def __init__(self, statusBar):
        self.statusBar = statusBar

        self.statusBar.messageChanged.connect(self.statusChanged)

    def init_statusBar(self, wl_mm):
        wavelength = wl_mm*1E6  # Convert to nanometres
        wlLabel = QtWidgets.QLabel(text="λ = {} nm".format(wavelength), autoFillBackground=False)
        wlLabel.setStyleSheet("QLabel{background-color: transparent; color: white}");
        self.statusBar.addPermanentWidget(wlLabel)

        return wlLabel

    def showWavelength(self, label, wavelength):
        label.setText("λ = {} nm".format(wavelength*1E6))
        #label.setStyleSheet("QLabel { background-color : transparent; color : blue;}");

    def showMessage(self, message, timer=10E3, messageType='info'):
        if messageType == 'error':
            self.statusBar.setStyleSheet("QStatusBar{background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        elif messageType == 'warning':
            self.statusBar.setStyleSheet("QStatusBar{background:rgba(255,175,0,255);color:black;font-weight:bold;}")
        elif messageType == 'info':
            self.statusBar.setStyleSheet("QStatusBar{background:black;color:white;font-weight:normal;}")
        self.statusBar.showMessage(message, int(timer))

    def statusChanged(self, args=None):
        # This is handle by QT connection!!! (ie. needs args).
        # If there are no arguments (the message is being removed)
        # change the background back to black / text back to white
        if not args:
            self.statusBar.setStyleSheet("QStatusBar{background: black; color: white;}")
