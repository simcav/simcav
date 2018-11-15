from PyQt5 import QtCore, QtGui, QtWidgets

def init_statusBar(statusBar, wl_mm):
    wavelength = wl_mm*1E6  # Convert to nanometres
    wlLabel = QtWidgets.QLabel(text="λ = {} nm".format(wavelength))
    statusBar.addPermanentWidget(wlLabel)
    
    return wlLabel
    
def showWavelength(label, wavelength):
    label.setText("λ = {} nm".format(wavelength*1E6))
    #label.setStyleSheet("QLabel { background-color : red; color : blue;}");
    
def showUpdates(message, timer):
    statusBar.showMessage(message, timer)