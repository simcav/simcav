import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# Matplotlib stuff
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

# Other modules
import numpy as np

import load_icons as LI
import simcav_physics as SP

#===============================================================================
# Creating the GUI
qtCreatorFile = "gui.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

#===============================================================================
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        
        
        self.setupUi(self)
        self.initUI()
        
        self.element_list_setup()
        self.cavity_icons_setup()
        
        self.cavity = SP.cavity()
        self.elementFocus = None
        
        
        # BUTTON FUNCTIONS =====================================================
        # Cavity buttons
        self.button_moveUp.clicked.connect(self.handle_button_moveUp)
        self.button_moveDown.clicked.connect(self.handle_button_moveDown)
        self.button_delete.clicked.connect(self.handle_button_delete)
        self.button_calcCavity.clicked.connect(self.handle_button_calcCavity)
        
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
        self.cavityPlot = PlotCanvas()
        self.tab_cavity.layout = QtWidgets.QVBoxLayout()
        self.tab_cavity.layout.addWidget(self.cavityPlot)
        self.tab_cavity.setLayout(self.tab_cavity.layout)
    
    def cavity_icons_setup(self):
        # Layout for scroll area.
        # Widgets (cavity elements) have to be added to this layout
        self.cavityIconsLayout = QtWidgets.QHBoxLayout(self.scroll_cavityIconsArea)
        self.cavityIconsLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.cavityIconsLayout.setContentsMargins(0,0,0,0)
        self.cavityIconsLayout.setSpacing(0)
        
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
            element['Icon'].setParent(None)
        for element in self.cavity.elementList:
            self.elementListLayout.addWidget(element['Widget'])
            self.cavityIconsLayout.addWidget(element['Icon'])
            
            
    ################################################    
    # Button functions Start
    
    # Move Up
    def handle_button_moveUp(self):
        if self.elementFocus != None:
            for elementID in self.elementFocus:
                element = window.cavity.findElement(elementID)
                element['Widget'].moveUp()
    def handle_button_moveDown(self):
        if self.elementFocus != None:
            for elementID in reversed(self.elementFocus):
                element = window.cavity.findElement(elementID)
                element['Widget'].moveDown()
            
    def handle_button_delete(self):
        if self.elementFocus != None:
            for elementID in reversed(self.elementFocus):
                element = window.cavity.findElement(elementID)
                element['Widget'].moveBottom()
                element['Widget'].deleteLater()
                element['Icon'].deleteLater()
                window.cavity.elementList.pop()
                window.cavity.numberOfElements = window.cavity.numberOfElements - 1
                window.updateElementList()
            
    def handle_button_calcCavity(self):
        # Calculate element matrixes
        calcCavity = self.cavity.calcCavity()
        # If not valid values, end calculations
        if not calcCavity:
            print('Error happened')
            return False
            
        # Plot cavity    
        self.cavityPlot.plot(self.cavity.z_tan, self.cavity.wz_tan, self.cavity.z_sag, self.cavity.wz_sag)
        
        # Plot vertical marks
        self.cavityPlot.plotVerticals(self.cavity.z_limits_tan, self.cavity.z_names_tan)
        
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
        # Add icon to cavity representation
        newIcon = IconWidget(elementName)
        self.cavityIconsLayout.addWidget(newIcon)
        
        # Add element to cavity-class
        self.cavity.addElement(newElement, newIcon)  
        
        window.cavity.numberOfElements = window.cavity.numberOfElements + 1
        
    # Button functions End 
    ################################################  
#===============================================================================

#===============================================================================
# Canvas plot
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
 
        #FigureCanvas.setSizePolicy(self,
        #        QSizePolicy.Expanding,
        #        QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot_init()
 

    def plot_init(self):
        data = [i**2 for i in range(25)]
        self.axes.plot(data, 'r-')
        self.axes.set_title('Plot init')
        self.draw()
    
    def plot(self, x1, y1, x2, y2):
        # Clear figure
        self.axes.clear()
        
        if len(x1) > 1:
            for zrow, wrow in zip(x1,y1):
                tan, = self.axes.plot(zrow,wrow*1000,'g',label='Tangential')
            for zrow, wrow in zip(x2,y2):
                sag, = self.axes.plot(zrow,wrow*1000,'b',label='Saggital')
        else:
            x1.append(0)
            y1.append(0)
            x2.append(0)
            y2.append(0)
            for zrow, wrow in zip(x1,y1):
                tan, = self.axes.plot(zrow,wrow*1000,'g',label='Tangential')
            for zrow, wrow in zip(x2,y2):
                sag, = self.axes.plot(zrow,wrow*1000,'b',label='Saggital')
                
        self.axes.set_xlabel('z (mm)')
        self.axes.set_ylabel('w (µm)')
        self.axes.set_ylim(ymin=0) # Adjust the vertical min
        self.axes.legend(handles=[tan,sag], loc='upper left')
        self.axes.grid(linestyle='dashed')
        #self.canvas.show()
        self.draw()
        #toolbar = self.figure.canvas.toolbar
        #toolbar.update()       
        #toolbar.push_current()
        
    def plotVerticals(self, xpoints, xnames):
        y0, y1 = self.axes.get_ylim()
        for xi, element in zip(xpoints,xnames):
            print(element)
            self.axes.axvline(x=xi, color='orange', alpha=0.7, linewidth=0.7)
            if 'Mirror' in element:
                self.axes.text(xi,y0+5, element, rotation=90, horizontalalignment='right', verticalalignment='bottom')
            elif 'Lens' in element:
                self.axes.text(xi, y0+5, element, rotation=90, horizontalalignment='right', verticalalignment='bottom')
            elif 'Block' in element:
                self.axes.text((xi+xold)/2, y1-5, element,rotation=0, horizontalalignment='center', verticalalignment='top', color='w', bbox=dict(facecolor='k', edgecolor='k', boxstyle='round', linewidth=0, alpha=0.65))
            else:
                self.axes.text((xi+xold)/2,y1-5,element,rotation=90, horizontalalignment='center', verticalalignment='top', backgroundcolor='w', bbox=dict(facecolor='w', edgecolor='k', boxstyle='round',linewidth=0.5, alpha=0.65))
            xold = xi
        #self.canvas.show()
        self.draw()
#===============================================================================

#===============================================================================
# Extra GUI elements
class IconWidget(QtWidgets.QWidget):
    def __init__(self, eType, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        
        self.elementType = eType
        self.icon = QtWidgets.QPushButton()
        self.icon.setIcon(LI.elementIcon(eType))
        self.icon.setMinimumWidth(40)
        self.icon.setMinimumHeight(40)
        self.icon.setFlat(True)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.icon)
        
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

        # CONFIG ---------------------------------------------------------------
        # Set minimum width so all labels are equal whatever the element name
        self.columns['label_name'].setMinimumWidth(110)
        
        # Validate entry boxes values
        self.validator = QtGui.QDoubleValidator()
        self.validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.columns['entry1'].setValidator(self.validator)
        self.columns['entry2'].setValidator(self.validator)
        
        # Default values
        self.assignDefaults(etype)
        
        # Disable entry boxes for Flat mirrors
        if etype == 'Flat Mirror':
            self.columns['entry1'].setDisabled(True)
            self.columns['entry2'].setDisabled(True)
        # CONFIG End -----------------------------------------------------------
        
        # Add the columns to the widget
        for i in self.columns:
            layout.addWidget(self.columns[i])
            
    def assignDefaults(self, eType):
        # Default values for the entries
        if eType in ['Distance','Block','Brewster Plate','Brewster Crystal']:
            self.columns['entry2'].setText(str(1))
        elif eType in ['Curved Mirror','Thin lens']:
            self.columns['entry2'].setText(str(0))
        elif eType == 'Curved Interface':
            self.columns['entry2'].setText(str(1))
        elif eType == 'Flat Mirror':
            self.columns['entry1'].setText(str(0))
            self.columns['entry2'].setText(str(0))
            self.columns['entry1'].setDisabled(True)
            self.columns['entry2'].setDisabled(True)
        elif eType == 'Flat Interface':
            self.columns['entry2'].setText(str(0))
            self.columns['entry2'].setText(str(1))
            self.columns['entry1'].setDisabled(True)
        else:
            self.columns['entry2'].setText(str(0))
            
    # Read entries
    def readEntry(self, entry):
        state = self.validator.validate(self.columns[entry].text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            #color = '#c4df9b' # green
            color = ''
            try:
                value = float(self.columns[entry].text().replace(",", "."))
            except:
                # MAYBE PUT A MESSAGE HERE SAYING INVALID FLOAT
                # TO THE MESSAGE BAR
                self.columns[entry].setText("")
                value = False
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            value = False
        else:
            color = '#f6989d' # red
            value = False
        self.columns[entry].setStyleSheet('QLineEdit { background-color: %s }' % color)
        return value

    # Mouse click events
    def mousePressEvent(self, QMouseEvent):
        # If shift is pressed...
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.setFocus()
            # Save element as focused, add if mayus is pressed.
            if modifiers == QtCore.Qt.ShiftModifier and self.elementID is not None:
                window.elementFocus.append(self.elementID)
            elif modifiers == QtCore.Qt.ControlModifier:
                # Remove focus
                window.elementFocus.remove(self.elementID)
            else:
                window.elementFocus = self.elementID
                
            # Change focus into list if is an integer
            if type(window.elementFocus) == int:
                focusList = [window.elementFocus]
            else:
                focusList = window.elementFocus
                
            # Order list
            window.elementFocus = []
            for element in window.cavity.elementList:
                if element['ID'] in focusList:
                    window.elementFocus.append(element['ID'])
                    
            # Change background
            for element in window.cavity.elementList:
                if element['ID'] in window.elementFocus:
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