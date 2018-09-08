import simcav_elementFeatures as EF

class cavity():
    def __init__(self):
        self.elementList = []
        self.refractiveIndex = 1.0
        self.numberOfElements = 0
        
    def addElement(self, widget, icon):
        elementDict = {
            'ID': widget.elementID,
            'Type': widget.elementType,
            'Order': widget.originalOrder,
            'Widget': widget,
            'Icon': icon
        }
        
        self.elementList.append(elementDict)
        
    def updateValue(self, elementID, fieldToUpdate, Value):
        for element in self.elementList:
            if element['ID'] == elementID:
                element[fieldToUpdate] = Value
                
                # Update also widget number if applicable
                if fieldToUpdate == 'Order':
                    element['Widget'].columns['label_number'].setText(str(Value))
                
    def reorderList(self):
        oldList = self.elementList
        newList = sorted(oldList, key=lambda k: k['Order'])
        self.elementList = newList
    
    def findElement(self, elementID):
        for element in self.elementList:
            if element['ID'] == elementID:
                return element
                
    def calcElementData(self):
        # Go through every element
        for element in self.elementList:
            # Read entry boxes
            entry1 = element['Widget'].readEntry('entry1')
            entry2 = element['Widget'].readEntry('entry2')
            
            # If any entry isn't valid return False to end loop
            if entry1 is False or entry2 is False:
                return False
            
            # Calculate matrix and assign distance/radius, etc.
            element.update(EF.assign(element['Type'], entry1, entry2, self.refractiveIndex))
            if element['Type'] in ['Flat interface', 'Curved interface']:
                self.refractiveIndex = element['refr_index']
            for i in element:
                print(i, element[i])
        return True