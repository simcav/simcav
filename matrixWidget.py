from PyQt5 import QtCore, QtGui, QtWidgets, uic

#===============================================================================


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        #QtWidgets.QWidget.__init__(self)
        # Creating the GUI
        #qtCreatorFile = "widget.ui" # Enter file here.
        #Ui_childWidget, QtBaseClass = uic.loadUiType(qtCreatorFile)
        self.ui = uic.loadUi('matrixWidget.ui', self)
        self.ui.show()
        
        #Ui_childWidget.__init__(self)
        #self.setStyleSheet(open('style_main.css').read())
    
    def title(self, text):
        self.labelTitle.setText(text)
        
    def addFormContent(self, layout, labelText, fieldWidget):
        # Element Name
        label = QtWidgets.QLabel(labelText)
        label.setFixedHeight(100)
        label.setFixedWidth(80)
        label.setWordWrap(True)
        
        # layout should be 0 (tan) or 1 (sag)
        if layout == 0:
            self.formLayout_tan.addRow(label, fieldWidget)
        elif layout == 1:
            self.formLayout_sag.addRow(label, fieldWidget)
        
        
class MatrixWidget(QtWidgets.QWidget):
    # Widget featuring a matrix
    def __init__(self):
        super(MatrixWidget, self).__init__()
        
        # Needs grid layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        #self.setFixedWidth(140)
        
        # Line to limit matrix
        line1 = self.VLine()
        line2 = self.VLine()        
        self.layout().addWidget(line1, 0, 0, 2, 1)
        self.layout().addWidget(line2, 0, 3, 2, 1)
        
        # ABCD: for labels: 0-a, 1-b, 2-c, 3-d
        self.abcd = [QtWidgets.QLabel(), QtWidgets.QLabel(), QtWidgets.QLabel(), QtWidgets.QLabel()]
        self.layout().addWidget(self.abcd[0], 0, 1)
        self.layout().addWidget(self.abcd[1], 0, 2)
        self.layout().addWidget(self.abcd[2], 1, 1)
        self.layout().addWidget(self.abcd[3], 1, 2)
        
        # Formatting
        for i in self.abcd:
            i.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            #i.setFixedWidth(60)
        
    def setValues(self, valueList):
        for i, j in zip(self.abcd, valueList):
            value = str(round(j, 6))
            #value = str(j)
            i.setText(value)
        
    def setValueX(self, position, value):
        # position int [0 to 3]
        # value float
        valueX = str(round(value, 6))
        #valueX = str(value)
        self.abcd[position].setText(valueX)
        
    def VLine(self):
        # Line to limit matrix
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Plain)
        return line