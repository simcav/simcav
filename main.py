import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

import button_functions as BT
import load_icons as LI
import simcav_physics as SP

#===============================================================================
# Creating the GUI
qtCreatorFile = "gui.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        
        
        self.setupUi(self)
        self.initUI()
        
        self.element_list_setup()
        
        self.cavity = SP.cavity()
        self.elementFocus = None
        
        
        # BUTTON FUNCTIONS =====================================================
        # Cavity buttons
        self.button_moveUp.clicked.connect(self.handle_button_moveUp)
        self.button_moveDown.clicked.connect(self.handle_button_moveDown)
        self.button_delete.clicked.connect(self.handle_button_delete)
        
        # "Add element" functions
        self.button_flatMirror.clicked.connect(self.handle_button_addElement)
        self.button_curvedMirror.clicked.connect(self.handle_button_addElement)
        self.button_distance.clicked.connect(self.handle_button_addElement)
        self.button_block.clicked.connect(self.handle_button_addElement)
        self.button_brewsterPlate.clicked.connect(self.handle_button_addElement)
        self.button_brewsterCrystal.clicked.connect(self.handle_button_addElement)
        self.button_flatInterface.clicked.connect(self.handle_button_addElement)
        self.button_curvedInterface.clicked.connect(self.handle_button_addElement)
        self.button_thinLens.clicked.connect(self.handle_button_addElement)
        self.button_customElement.clicked.connect(self.handle_button_addElement)
        #=======================================================================
        
        self.numberOfElements = 0
    
    def initUI(self):
        pass
    
    def element_list_setup(self):
        # Layout for scroll area.
        # Widgets (cavity elements) have to be added to this layout
        self.elementListLayout = QtWidgets.QVBoxLayout(self.element_list_scroll)
        self.elementListLayout.setAlignment(QtCore.Qt.AlignTop)
        self.elementListLayout.setContentsMargins(0,0,0,0)
        self.elementListLayout.setSpacing(0)
        
    def updateElementList(self):
        for element in self.cavity.elementList:
            element['Widget'].setParent(None)
        for element in self.cavity.elementList:
            self.elementListLayout.addWidget(element['Widget'])
            
            
    ################################################    
    # Button functions Start
    
    # Move Up
    def handle_button_moveUp(self):
        if self.elementFocus != None:
            elementID = self.elementFocus
            element = window.cavity.findElement(elementID)
            element['Widget'].moveUp()
    def handle_button_moveDown(self):
        if self.elementFocus != None:
            elementID = self.elementFocus
            element = window.cavity.findElement(elementID)
            element['Widget'].moveDown()
    def handle_button_delete(self):
        if self.elementFocus != None:
            elementID = self.elementFocus
            element = window.cavity.findElement(elementID)
            element['Widget'].moveBottom()
            element['Widget'].deleteLater()
            window.cavity.elementList.pop()
            window.cavity.numberOfElements = window.cavity.numberOfElements - 1
            window.updateElementList()
        
    
    # Add element
    def handle_button_addElement(self):
        buttonName = self.sender().objectName()
        
        # Nice name for on screen print
        elementName = buttonName[7:].capitalize()
        for i in range(len(buttonName[7:])):
            if buttonName[7+i].isupper():
                elementName = buttonName[7:7+i].capitalize() + " " + buttonName[7+i:]
        
        newElement = ElementWidget(window.cavity.numberOfElements, elementName)
        # Add widget to element box
        self.elementListLayout.addWidget(newElement)
        # Add element to cavity-class
        self.cavity.addElement(newElement)
        
        window.cavity.numberOfElements = window.cavity.numberOfElements + 1
        
    # Button functions End 
    ################################################  
#===============================================================================


#===============================================================================
# Extra GUI elements
# Element label
class ElementWidget(QtWidgets.QWidget):
    def __init__(self, eOrder, etype, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        
        self.elementID = id(self)
        self.elementType = etype
        self.originalOrder = eOrder
        
        # Right click menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Set event Filter
        self.installEventFilter(self)

        # Appearance
        layout = QtWidgets.QHBoxLayout(self)


        self.columns = {
            'label_number': QtWidgets.QLabel(text=str(eOrder)),
            'label_name': QtWidgets.QLabel(text=etype),
            'entry1': QtWidgets.QLineEdit(placeholderText="mm"),
            'entry2': QtWidgets.QLineEdit()
        }

        # Config ---------------------------------------------------------------
        # Set minimum width so all labels are equal whatever the element name
        self.columns['label_name'].setMinimumWidth(110)
        # Config End -----------------------------------------------------------
        
        # Add the columns to the widget
        for i in self.columns:
            layout.addWidget(self.columns[i])

    # Mouse click events
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.setFocus()
            window.elementFocus = self.elementID
            for element in window.cavity.elementList:
                if element['ID'] == window.elementFocus:
                    element['Widget'].setAutoFillBackground(True)
                    element['Widget'].setBackgroundRole(QtGui.QPalette.AlternateBase)
                else:
                    element['Widget'].setAutoFillBackground(False)
                    element['Widget'].setBackgroundRole(QtGui.QPalette.Base)
                    
            #print("Left Button Clicked")
        elif QMouseEvent.button() == QtCore.Qt.RightButton:
            #do what you want here
            self.openMenu(QMouseEvent.pos())
            #print("Right Button Clicked")

    # Filter events
    # def eventFilter(self, object, event):
    #     if event.type() == QtCore.QEvent.FocusIn:
    #         self.setAutoFillBackground(True)
    #         self.setBackgroundRole(QtGui.QPalette.AlternateBase)
    #         #print("widget has gained keyboard focus")
    #     elif event.type() == QtCore.QEvent.FocusOut:
    #         self.setAutoFillBackground(False)
    #         self.setBackgroundRole(QtGui.QPalette.Base)
    #         #print("widget has lost keyboard focus")
    #     #else:
    #     #    print(event.name())
    #     return False

    # Right click menu
    def openMenu(self, position):
        menu = QtWidgets.QMenu()
        upAction = menu.addAction("Move up")
        downAction = menu.addAction("Move down")
        action = menu.exec_(self.mapToGlobal(position))
        if action == upAction:
            self.moveUp()
        elif action == downAction:
            self.moveDown()
    
    # Right click functions
    def moveUp(self):
        element = window.cavity.findElement(self.elementID)
        valueOld = element['Order']
        valueNew = element['Order'] - 1
        
        # Do nothing if it's first element
        if element['Order'] != 0:
            # Change the other elements
            for i in window.cavity.elementList:
                if i['Order'] < valueOld and i['Order'] >= valueNew:
                    window.cavity.updateValue(i['ID'], 'Order', i['Order'] + 1)
            # Change THE element
            window.cavity.updateValue(element['ID'], 'Order', valueNew)
            # Reorder the element list
            window.cavity.reorderList()
            # Update GUI
            window.updateElementList()
        
    def moveDown(self):
        element = window.cavity.findElement(self.elementID)
        valueOld = element['Order']
        valueNew = element['Order'] + 1
        
        # Do nothing if it's first element
        if element['Order'] < window.cavity.numberOfElements - 1:
            # Change the other elements
            for i in window.cavity.elementList:
                if i['Order'] > valueOld and i['Order'] <= valueNew:
                    window.cavity.updateValue(i['ID'], 'Order', i['Order'] - 1)
            # Change THE element
            window.cavity.updateValue(element['ID'], 'Order', valueNew)
            # Reorder the element list
            window.cavity.reorderList()
            # Update GUI
            window.updateElementList()
            
    def moveBottom(self):
        element = window.cavity.findElement(self.elementID)
        # Change the other elements
        for i in window.cavity.elementList:
            if i['Order'] > element['Order']:
                window.cavity.updateValue(i['ID'], 'Order', i['Order'] - 1)
        # Change THE element
        window.cavity.updateValue(element['ID'], 'Order', window.cavity.numberOfElements-1)
        # Reorder the element list
        window.cavity.reorderList()
        # Update GUI
        window.updateElementList()

#===============================================================================
# Launching the program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # # Load Icons
    # small_del = QtGui.QIcon()
    # small_del.addFile("Icons/small_del.png")
    # #tk.PhotoImage(file=resource_path("Icons/small_del.png"))
    window = MyApp()
    
    window.show()
    sys.exit(app.exec_())
#===============================================================================