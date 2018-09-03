from PyQt5 import QtGui

def small_del():
    small_del = QtGui.QIcon()
    small_del.addFile("Icons/small_del.png")
    return small_del
    
def elementIcon(elementName):
    filename = "Icons/icon_" + elementName.lower().replace(" ", "_") + ".png"
    icon = QtGui.QIcon()
    icon.addFile(filename)
    return icon