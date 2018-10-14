import numpy as np
import itertools
import simcav_elementFeatures as EF
import simcav_ABCD as abcd
import simcav_conditions as SC

class cavity():
    def __init__(self):
        self.elementList = []
        self.conditionList = []
        self.numberOfElements = 0
        self.wl_mm = 0.001   # Default 1µm
        
    def addCondition(self, widget):
        conditionDict = {
            'ID': widget.conditionID,
            'Widget': widget
        }
        self.conditionList.append(conditionDict)
        
    def delCondition(self, id):
        # id should be a list of IDs
        for condition in self.conditionList:
            if condition['ID'] == id:
                condition['Widget'].deleteLater()
                self.conditionList.remove(condition)
            
    def calcSolutions(self, elementList, conditionList):
        print('Calculating solutions')
        for element in elementList:
            myDict = {}
            a = element['Widget'].readEntry('entry1')
            b = element['Widget'].readEntry('entry2')
            c = element['Widget'].readEntry('entry3')
            myDict['vector'] = np.linspace(a, b, c)
            element.update(myDict)
            print(element)
            
        # Where the real magic starts
        refr_index = 1.0
        print('COMBINING')
        combination_final = []
        stablility_final = []
        results_final = []
        for combination in itertools.product(*[i['vector'] for i in elementList]):
            for element, entry in zip(elementList, combination):
                print(entry)
                # Create matrix for each element
                kind = element['Type']
                e1 = entry
                e2 = element['oldEntry2']
                if kind == 'Custom element':
                    pass
                else:
                    element.update(EF.assign(kind, e1, e2, refr_index))
                    try:
                        refr_index = element['refr_index']
                    except:
                        pass
                        
            # Calculate cavity matrix, for both saggital and tangential
            cavityMatrix = []
            cavityMatrix.append(self.calcCavityMatrix(elementList,0))
            cavityMatrix.append(self.calcCavityMatrix(elementList,1))
            # stable1 = SIMU.stabilitycalc(self.cav_matrix_tan)
            # stable2 = SIMU.stabilitycalc(self.cav_matrix_sag)
            # Before anything check stability
            stability = self.stabilityValue(cavityMatrix)
                
            if stability[0] and stability[1]:
                results = []
                for condition in conditionsList:
                    answer = SC.evalConditions(cavityMatrix, elementList, stability, conditionName, conditionAt, condStart, condEnd, self.wl_mm)
                    #self.conditions_call[condition['condition_var'].get()](condition)
                    if True:
                        print('answer',answer)
                    if not answer:
                        pass
                    else:
                        results.append(answer)
                if results:
                    combination_final.append(combination)
                    stablility_final.append(stability)
                    results_final.append(results)
            # Since this repeats for each different configuration, if it isnt stable nothing is done, y listo!
        return combination_final, stablility_final, results_final
        
    def addElement(self, widget, icon, vector):
        elementDict = {
            'ID': widget.elementID,
            'Type': widget.elementType,
            'Order': widget.originalOrder,
            'Widget': widget,
            'Icon': icon,
            'isVector': vector
        }
        
        self.elementList.append(elementDict)
        self.optionMenuLists()
        
    def updateValue(self, elementID, fieldToUpdate, Value):
        for element in self.elementList:
            if element['ID'] == elementID:
                element[fieldToUpdate] = Value
                
                # Update also widget number if applicable
                if fieldToUpdate == 'Order':
                    element['Widget'].columns['label_number'].setText(str(Value))
        # Update option menus
        self.optionMenuLists()
        
    def updateOtherList(self, elementID, myList, fieldToUpdate, Value):
        for element in myList:
            if element['ID'] == elementID:
                element[fieldToUpdate] = Value
                try:
                    refr_index = element['refr_index']
                except:
                    refr_index = 1.0
                newdict = EF.assign(element['Type'], element['entry1'], element['entry2'], refr_index)
                myList[element['Order']].update(newdict)
        return myList
                
    def reorderList(self):
        oldList = self.elementList
        newList = sorted(oldList, key=lambda k: k['Order'])
        self.elementList = newList
    
    def findElement(self, elementID):
        for element in self.elementList:
            if element['ID'] == elementID:
                return element
        return None
        
    def findElement_byNumber(self, elementOrder):
        for element in self.elementList:
            if element['Order'] == elementOrder:
                return element
        return None
        
    def optionMenuLists(self):
        elementList = []
        vectorList = []
        notVectorList = []
        
        for element in self.elementList:
            entry = str(element['Order']) + ' ' + element['Type']
            elementList.append(entry)
            if element['isVector']:
                vectorList.append(entry)
            else:
                notVectorList.append(entry)
        return elementList, vectorList, notVectorList
        
    ############################################################################
    # Function to initiate cavity calculations
    def basicSetup(self):
        if not self.minimumElements():
            print('Error, not enough elements')
            return False
        
        # Assign matrix to elements
        if not self.calcElementData():
            print('Error happened with calcElementData')
            return False
            
        # Ensure working conditions
        # Check no 0-length distance elements
        if not self.elementLengths():
            print('Error happened with elementLengths')
            return False
        else:
            print('Lengths OK')
        # And also check that it is a closed cavity
        if not self.closedCavity():
            print('Error happened with closedCavity')
            return False
        else:
            print('Closed OK')
        return True
    
    ############################################################################
    # Function to calculate the optical cavity
    def calcCavity(self):
        if not self.basicSetup():
            return False
            
        # Calculate cavity matrix, for both saggital and tangential
        cavityMatrix = []
        cavityMatrix.append(self.calcCavityMatrix(self.elementList,0))
        cavityMatrix.append(self.calcCavityMatrix(self.elementList,1))
        
        # Before anything check stability
        if not self.stabilityBool(cavityMatrix):
            print('Error happened with stabilityBool')
            return False
        else:
            print('Stability OK')
            
        # Calculate complex beam parameter
        # This is the starting point to calculate the propagation
        self.q0 = []
        for matrix in cavityMatrix:
            self.q0.append(abcd.q_resonator(matrix))
            
        # Calculate propagation through cavity, both proyections
        proy = 0
        self.z_tan, self.wz_tan, self.z_limits_tan, self.z_names_tan = self.propagation(self.elementList, self.q0[proy], self.wl_mm, proy)
        proy = 1
        self.z_sag, self.wz_sag, self.z_limits_sag, self.z_names_sag = self.propagation(self.elementList, self.q0[proy], self.wl_mm, proy)
        
        self.z_tan = np.array(self.z_tan)
        self.z_sag = np.array(self.z_sag)
        self.wz_tan = np.array(self.wz_tan)
        self.wz_sag = np.array(self.wz_sag)
        
        return True
        
    ############################################################################
    # Function to calculate the stability in function of a variation
    def calcStability(self, elementOrder, xstart, xend):
        if not self.basicSetup():
            print('Basics FAIL')
            return False, False, False, False
            
        # Define coordinate X   
        xvec = np.linspace(xstart, xend, num=100)
        # Create another list, to be modified
        stabilityList = list(self.elementList)
        # Element to be modified
        element = self.findElement_byNumber(elementOrder)
        
        # Calculate coordinate Y
        yvec_tan = []
        yvec_sag = []
        
        for number in xvec:
            stabilityList = self.updateOtherList(element['ID'], stabilityList, 'entry1', number)
                
            # Calculate cavity matrix, for both saggital and tangential
            stabilityMatrix = [self.calcCavityMatrix(stabilityList,0),
                               self.calcCavityMatrix(stabilityList,1)]
            stab_val = self.stabilityValue(stabilityMatrix)

            yvec_tan.append(stab_val[0])
            yvec_sag.append(stab_val[1])
            
        xlabel = 'Variation of element ' + str(element['Order']) + ' (mm)'
        return np.array(xvec), np.array(yvec_tan), np.array(yvec_sag), xlabel
        
    # Function to calculate beam size along a "distance" element
    def calcBeamsize(self, watchElementOrder, varElementOrder, xstart, xend):
        if not self.basicSetup():
            print('Basics FAIL')
            return False, False, False, False, False
            
        # Define coordinate X 
        xvec = np.linspace(xstart, xend, num=100)
        beamsizeList = list(self.elementList)
        # Relevant elements
        watchElement = self.findElement_byNumber(watchElementOrder)
        varElement = self.findElement_byNumber(varElementOrder)
        
        # Calculate coordinate Y
        yvec_tan = []
        yvec_sag = []
        
        # For every value of the X axis vector
        for number in xvec:
            beamsizeList = self.updateOtherList(varElement['ID'], beamsizeList, 'entry1', number)
            
            beamsizeMatrix = [self.calcCavityMatrix(beamsizeList,0),
                              self.calcCavityMatrix(beamsizeList,1)]
            q0 = []
            for matrix in beamsizeMatrix:
                q0.append(abcd.q_resonator(matrix))
            q = abcd.q_element(q0, watchElement, beamsizeList)
            
            # Refractive index
            if 'refr_index' in watchElement.keys():
                refr_index = watchElement['refr_index']
            else:
                refr_index = 1.0
                
            # Wavelength (micrometres)
            wl = self.wl_mm
            
            # Calculate beamsize
            R, w = abcd.r_w(q[0], wl, refr_index)
            yvec_tan.append(w*1E3)
            R, w = abcd.r_w(q[1], wl, refr_index)
            yvec_sag.append(w*1E3)
            
        xlabel = 'Variation of element ' + str(varElement['Order']) + ' (mm)'
        ylabel = 'Beam size at element ' + str(watchElement['Order']) + ' (µm)'    
        return np.array(xvec), np.array(yvec_tan), np.array(yvec_sag), xlabel, ylabel
        
    #================= WORKING CONDITION FUNCTIONS =============================
    #%% -------------------- NonZero Lengths Condition --------------------
    def minimumElements(self):
        if self.numberOfElements < 3:
            return False
        else:
            return True
        
    def elementLengths(self):
        for element in self.elementList:
            if element['Type'] in ['Distance','Block','Brewster plate','Brewster crystal']:
                if element['distance'] == 0:
                    self.zeroelement = element['Order']
                    return False
        return True
    #%% -------------------- Closed Cavity Condition --------------------
    def closedCavity(self):
        # Check that both sides of the cavity have mirrors
        # ie. check that is closed cavity, not open
        side1 = self.elementList[0]["Type"]
        side2 = self.elementList[-1]["Type"]

        if "Mirror" in side1 and "Mirror" in side2:
            return True
        else:
            return False
            
    #%% -------------------- Stability Condition --------------------        
    # Checks if stable cavity   
    def stabilityBool(self, M_cav, v=False):
        stable = []
        for matrix in M_cav:
            stabilityValue = (matrix[0,0] + matrix[1,1]) / 2
            if abs(stabilityValue) < 1:
                stable.append(True)
                if v:
                    print("Stability condition: -1 < " + str(stabilityValue) + ' < 1')
                    print("Stable!")
            else:
                stable.append(False)
                if v:
                    print("Stability condition: -1 < " + str(stabilityValue) + ' < 1')
                    print("NOT Stable!")
        if stable[0] and stable[1]:
            return True
        else:
            return False
            
    # Calculates stability and returns value.    
    def stabilityValue(self, M_cav):
        stabNorm = []
        for matrix in M_cav:
            stab = (matrix[0,0] + matrix[1,1]) / 2
            if stab < 1 and stab > -1:
                stabNorm.append(1 - stab**2)
            else:
                stabNorm.append(0)
        return stabNorm
    #=============== END WORKING CONDITION FUNCTIONS ===========================
        
    def calcElementData(self):
        # Go through every element
        for element in self.elementList:
            # Read entry boxes
            entry1 = element['Widget'].readEntry('entry1')
            entry2 = element['Widget'].readEntry('entry2')
            
            # If any entry isn't valid return False to end loop
            if entry1 is False or entry2 is False:
                return False
            try:
                refr_index = self.elementList[element['Order']-1]['refr_index']
            except:
                refr_index = 1.0
            # Calculate matrix and assign distance/radius, etc.
            element.update(EF.assign(element['Type'], entry1, entry2, refr_index))
            # Update refractive index after interfaces
            # if element['Type'] in ['Flat interface', 'Curved interface']:
            #     self.refractiveIndex = element['refr_index']
            # PROBABLY NOT NEEDED SINCE DEALING WITH REFR INDEX DIFFERENTLY
            
        return True
    
    #================= PHYSICAL CALCULATIONS =============================
    #%% -------------------- Cavity matrix --------------------
    def calcCavityMatrix(self, E_list, proy):
        # Takes the list of elements, as a list of dictionaries,
        # with an entry called "matrix"
        # "proy" states for the proyection, either 0 for tangential or 1 for sagital.
        M_cav = np.identity(2)
    
        # Tangential or saggital proyection     
        for element in E_list[1:]:
            M_cav = np.dot(element['matrix'][proy],M_cav)
            
        for element in E_list[len(E_list)-2::-1]:
            M_cav = np.dot(element['matrix'][proy],M_cav)
        return M_cav
        
    #%% ----------------- Propagation calculation ------------------------------    
    def propagation(self, E_list, q0, wl, proy, chivato=False):    
        # Propagation
        zmax = 0
        z = []
        wz = []
        
        # To draw limiting lines for each element
        z_limits = []
        z_names = []
        
        # Debugging ----------------------------------------
        show_n = False
        if chivato:
            print('Im in cavity.propagation. For loop through elements:')
        if show_n:
            print(' ')
            print('Refractive index')
        #---------------------------------------------------
        
        refr_index_global = 1.0 
          
        for element in E_list:
            # Some debugging
            if chivato:
                print(element['Type'])
            
            # ------------------- Mirror -------------------
            if (
                (element['Type']=="Flat Mirror") or 
                (element['Type']=="Curved Mirror") or 
                (element['Type']=="Thin Lens") or
                (element['Type']=="Flat Interface") or
                (element['Type']=="Curved Interface") or
                (element['Type']=="Custom Element") ):
                
                # Calculate complex beam parameter (q)
                q = abcd.q_propagation(element['matrix'][proy],q0)
                q0 = q
                
                # Modify refractive index of the medium
                if 'refr_index' in element.keys():
                    refr_index_global = element['refr_index']
                if show_n:
                    print(element['Type'],refr_index_global)
                            
                # Some debugging
                if chivato:
                    print('Imag(q)',np.imag(q))
                    
                # Add mirror position
                try:
                    z_limits.append(z_limits[-1])
                    z_names.append(element['Type'])
                except:
                    z_limits.append(0)
                    z_names.append(element['Type'])
                #if z:
                #    plt.vlines(z[-1][-1],0,1)
            
            # ------------------- Distance -------------------            
            elif element['Type']=="Distance":
                aux_vector = np.linspace(0,element['distance'],num=100)
                z.append(aux_vector+zmax)
                zmax = zmax + max(aux_vector)
                q = q0 + aux_vector
                q0 = q[-1]
                w = np.sqrt(-wl/(np.pi*element['refr_index']*np.imag(1/q)))
                wz.append(w)
                
                # Modify refractive index of the medium
                refr_index_global = element['refr_index']
                
                if show_n:
                    print(element['Type'],refr_index_global)
                    
                # Add finish position.
                z_limits.append(zmax)
                z_names.append('')
            
            # ------------------- Block -------------------
            elif element['Type']=="Block":
                # Block divided in interface - distance - interface
                # First interface
                I = abcd.flat_interface(refr_index_global,element['refr_index'])
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                # Some debugging
                if chivato:
                    print('Imag(q)',np.imag(q))
                
                # Distance
                aux_vector = np.linspace(0,element['distance'],num=100)
                z.append(aux_vector+zmax)
                zmax = zmax + max(aux_vector)
                q = q0 + aux_vector
                q0 = q[-1]
                w = np.sqrt(-wl/(np.pi*element['refr_index']*np.imag(1/q)))
                wz.append(w)
                
                # Second interface
                I = abcd.flat_interface(element['refr_index'], refr_index_global)
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                # Some debugging
                if chivato:
                    print('Imag(q)',np.imag(q))
                
                if show_n:
                    print(element['Type'],refr_index_global)
                    
                # Add finish position.
                z_limits.append(zmax)
                z_names.append(element['Type'])
                
            # ------------------- Brewster Plate -------------------
            elif element['Type']=="Brewster Plate":
                # Block divided in interface - distance - interface
                # First interface
                I = abcd.flat_interface_br(refr_index_global,element['refr_index'])
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                # Some debugging
                if chivato:
                    print('Imag(q)',np.imag(q))
                
                # Distance
                thi = np.arctan(element['refr_index']/refr_index_global)    
                thr = np.arcsin( refr_index_global*np.sin(thi) / element['refr_index'] )    
                d_temp = element['distance'] / np.cos(thr)
                
                aux_vector = np.linspace(0,d_temp,num=100)
                z.append(aux_vector+zmax)
                zmax = zmax + max(aux_vector)
                q = q0 + aux_vector
                q0 = q[-1]
                w = np.sqrt(-wl/(np.pi*element['refr_index']*np.imag(1/q)))
                if proy == 0:
                    w = w/element['refr_index']
                wz.append(w)
                
                # Second interface
                I = abcd.flat_interface_br(element['refr_index'], refr_index_global)
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                # Some debugging
                if chivato:
                    print('Imag(q)',np.imag(q))
                
                if show_n:
                    print(element['Type'],refr_index_global)
                    
                # Add finish position.
                z_limits.append(zmax)
                z_names.append(element['Type'])
            
            # ------------------- Brewster Crystal -------------------
            elif element['Type']=="Brewster Crystal":
                # Block divided in interface - distance - interface
                # First interface
                I = abcd.flat_interface_br(refr_index_global,element['refr_index'])
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                # Some debugging
                if chivato:
                    print('Imag(q)',np.imag(q))
                
                # Distance
                aux_vector = np.linspace(0,element['distance'],num=100)
                z.append(aux_vector+zmax)
                zmax = zmax + max(aux_vector)
                q = q0 + aux_vector
                q0 = q[-1]
                w = np.sqrt(-wl/(np.pi*element['refr_index']*np.imag(1/q)))
                if proy == 0:
                    w = w/element['refr_index']
                wz.append(w)
                
                # Second interface
                I = abcd.flat_interface_br(element['refr_index'], refr_index_global)
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                # Some debugging
                if chivato:
                    print('Imag(q)',np.imag(q))
                
                if show_n:
                    print(element['Type'],refr_index_global)
                    
                # Add finish position.
                z_limits.append(zmax)
                z_names.append(element['Type'])
                
            else:
                print('Element ' + element['Type'] + ' not available!')
        return z, wz, z_limits, z_names
