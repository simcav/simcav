from PyQt5 import QtCore, QtGui, QtWidgets
import load_icons as LI

class element_list_setup():
    def __init__(self, main_window):
        # Layout for scroll area.
        # Widgets (cavity elements) have to be added to this layout
        self.elementListLayout = QtWidgets.QVBoxLayout(main_window.element_list_scroll)
        self.elementListLayout.setAlignment(QtCore.Qt.AlignTop)
        print('im here')
        main_window.button_flatMirror.clicked.connect(self.handle_button_flatMirror)
    
    ################################################    
    # Button functions Start
    def handle_button_flatMirror(self):
        print('add')
        newElement = ElementWidget(0, "Flat mirror")
        self.elementListLayout.addWidget(newElement)
        
    def handle_button_curvedMirror(self):
        newElement = ElementWidget(0, "Flat mirror")
        self.elementListLayout.addWidget(newElement)
    # Button functions End 
    ################################################  


# Element label
class ElementWidget(QtWidgets.QWidget):
    def __init__(self, inumber, etype, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.itemNumber = inumber
        self.elementType = etype
        
        # Right click menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        # Set event Filter
        self.installEventFilter(self)
        
        # Appearance
        
        
        
        layout = QtWidgets.QHBoxLayout(self)
        
        
        self.columns = {
            'label_number' : QtWidgets.QLabel(text=str(inumber)),
            'label_name' : QtWidgets.QLabel(text='Flat mirror'),
            'entry1' : QtWidgets.QLineEdit(placeholderText="mm"),
            'entry2' : QtWidgets.QLineEdit(),
            'delete' : QtWidgets.QPushButton()
        }
        
        # Config
        self.columns['delete'].setIcon(LI.small_del())
        
        for i in self.columns:
            layout.addWidget(self.columns[i])


    # Mouse click events
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.setFocus()
            #print("Left Button Clicked")
        elif QMouseEvent.button() == QtCore.Qt.RightButton:
            #do what you want here
            self.openMenu(QMouseEvent.pos())
            #print("Right Button Clicked")
    
    # Filter events
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.FocusIn:
            self.setAutoFillBackground(True)
            self.setBackgroundRole(QtGui.QPalette.AlternateBase)
            #print("widget has gained keyboard focus")
        elif event.type() == QtCore.QEvent.FocusOut:
            self.setAutoFillBackground(False)
            self.setBackgroundRole(QtGui.QPalette.Base)
            #print("widget has lost keyboard focus")
        #else:
        #    print(event.name())
        return False
        
        
    # Right click menu
    def openMenu(self, position):
        menu = QtWidgets.QMenu()
        topAction = menu.addAction("Move top")
        upAction = menu.addAction("Move up")
        downAction = menu.addAction("Move down")
        bottomAction = menu.addAction("Move bottom")
        action = menu.exec_(self.mapToGlobal(position))
        if action == topAction:
            self.moveTop()
        elif action == upAction:
            self.moveUp()
        elif action == downAction:
            self.moveDown()
        elif action == bottomAction:
            self.moveBottom()
    
    def moveTop(self):
        self.itemNumber = 0
    def moveUp(self):
        index = window.elementListLayout.count()
        i = 0
        while(i < index):
            if window.elementListLayout.itemAt(i) is None:
                pass
            else:
                print(window.elementListLayout.itemAt(i).widget().itemNumber)
            # try:
            #     print(window.elementListLayout.itemAt(index).widget())
            # except:
            #     pass
            #myWidget = window.elementListLayout.itemAt(index).widget()
            #print(myWidget.itemNumber)
            i = i + 1
        self.itemNumber = self.itemNumber - 1
        #for i in window.elementListLayout.children():
        #    i.printDummy()
        #    print(i.itemNumber)
    def moveDown(self):
        self.itemNumber = self.itemNumber + 1
    def moveBottom(self):
        # Need numberTotalItems in parent
        pass
    
    def printDummy(self):
        print("I'm dumb!")