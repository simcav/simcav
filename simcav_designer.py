from PyQt5 import QtWidgets, QtGui, QtCore

class SolutionsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setStyleSheet(open('style_designerSolutions.css').read())
        self.row = 1
        
        layout = QtWidgets.QGridLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        self.layout = layout
        
################################################################################        
        
    def addHeaders(self, iterElements, conditionList):
        layout = self.layout
        numElements = len(iterElements)
        # Table title: Items, Stability and Conditions
        #font = QtGui.QFont()
        #font.setWeight(QtGui.QFont.Bold)
        self.title = {
            'item': LabelTitle(self, text='Varying elements'),
            'stability': LabelTitle(self, text='Stability'),
            'conditions': LabelTitle(self, text='Conditions')
        }
        
        layout.addWidget(self.title['item'], 0, 0, 1, numElements)
        #layout.addWidget(QVLine(), 0, numElements, 1, 1)
        layout.addWidget(self.title['stability'], 0, numElements, 1, 2)
        #layout.addWidget(QVLine(), 0, numElements + 3, 1, 1)
        layout.addWidget(self.title['conditions'], 0, numElements + 2, 1, -1)
        
        # Subtitle: 
        # Elements:
        self.iterElementsNumbers = []
        for column, element in enumerate(iterElements):
            label = LabelSubtitle(self, text=element)
            layout.addWidget(label, 1, column)
            self.iterElementsNumbers.append(element[0])
        # Separator
        #layout.addWidget(QVLine(), 1, numElements, 1, 1)
        # Stability
        label = LabelSubtitle(self, text='Tangential')
        layout.addWidget(label, 1, numElements)
        label = LabelSubtitle(self, text='Sagittal')
        layout.addWidget(label, 1, numElements + 1)
        # Separator
        #layout.addWidget(QVLine(), 1, numElements + 3)
        # Conditions
        self.stabilityNum = 0
        for i, element in enumerate(conditionList):
            name = element['Widget'].columns['condition'].currentText()
            if name == "Stability":
                self.stabilityNum = self.stabilityNum + 2
            else:
                label = LabelSubtitle(self, text=name)
                layout.addWidget(label, 1, numElements + 2 + 2*i - self.stabilityNum, 1, 2)
            
        # Separators
        #layout.addWidget(QVLine(), 0, numElements, -1, 1)
        #layout.addWidget(QVLine(), 0, numElements + 3, -1, 1)
            
    def addRow(self, combination, stability, results, conditionList):
        row = self.row
        numberItems = len(self.iterElementsNumbers)
        # Add combination of elements
        column = 0
        for j, i in enumerate(combination):
            try:
                int(self.iterElementsNumbers[0])
                # Only present those elements that change
                if str(j) in self.iterElementsNumbers:
                    label = LabelCell(round(i,2), row)
                    self.layout.addWidget(label, 1+row, column, 1, 1)
                    column = column + 1
            except:
                label = LabelCell(round(i,2), row)
                self.layout.addWidget(label, 1+row, column, 1, 1)
                column = column + 1
        # Add stability
        for column, i in enumerate(stability):
            label = LabelCell(round(i,2), row, group='stab')
            self.layout.addWidget(label, 1+row, numberItems+column, 1, 1)
        # Add condition value
        stabilityNum = 0
        for column, result  in enumerate(results):
            startColumn = numberItems + 2
            element = conditionList[column]
            conditionName = element['Widget'].columns['condition'].currentText()
            if conditionName == "Cav. length":
                label = LabelCell(round(result,2), row, group='solution')
                self.layout.addWidget(label, 1+row, startColumn+2*column-stabilityNum, 1, 2)
            elif conditionName == "Stability":
                stabilityNum = stabilityNum + 2
            else:
                label = LabelCell(round(result[0],2), row, group='solution')
                self.layout.addWidget(label, 1+row, startColumn+2*column-stabilityNum, 1, 1)
                label = LabelCell(round(result[1],2), row, group='solution')
                self.layout.addWidget(label, 1+row, startColumn+2*column+1-stabilityNum, 1, 1)
        self.row = row + 1
        
    def addCombination(self, combination):
        pass
        
    def addStability(self, stability):
        pass
        
    def addResults(self, results):
        pass
            
class LabelTitle(QtWidgets.QLabel):
    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, parent, *args, **kwargs)
        self.setAlignment(QtCore.Qt.AlignCenter)
        
        font = QtGui.QFont()
        font.setWeight(QtGui.QFont.Bold)
        font.setStyleHint(QtGui.QFont.Serif)
        self.setFont(font)
        
class LabelSubtitle(QtWidgets.QLabel):
    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, parent, *args, **kwargs)
        self.setAlignment(QtCore.Qt.AlignCenter)

class LabelCell(QtWidgets.QLabel):
    def __init__(self, value, row, group=False, parent=None, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, parent, *args, **kwargs)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setText(str(value))
        if row%2:
            self.setProperty('impar', False)
        else:
            self.setProperty('impar', True)
        if group:
            self.setProperty('grupo', group)
        
class QVLine(QtWidgets.QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)