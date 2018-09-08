import numpy as np
import simcav_elementFeatures as EF
import simcav_ABCD as abcd

class cavity():
    def __init__(self):
        self.elementList = []
        self.refractiveIndex = 1.0
        self.numberOfElements = 0
        self.wl_mm = 675E-6
        
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
        return None
                
    def calcCavity(self):
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
        print('q0 OK')
            
        # Calculate propagation through cavity, both proyections
        proy = 0
        self.z_tan, self.wz_tan, self.z_limits_tan, self.z_names_tan = self.propagation(self.elementList, self.q0[proy], self.wl_mm, proy)
        proy = 1
        self.z_sag, self.wz_sag, self.z_limits_sag, self.z_names_sag = self.propagation(self.elementList, self.q0[proy], self.wl_mm, proy)
        print('data OK')
        
        return True
        
    #================= WORKING CONDITION FUNCTIONS =============================
    #%% -------------------- NonZero Lengths Condition --------------------
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

        if "Mirror" in (side1 and side2):
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
            
            # Calculate matrix and assign distance/radius, etc.
            element.update(EF.assign(element['Type'], entry1, entry2, self.refractiveIndex))
            # Update refractive index after interfaces
            if element['Type'] in ['Flat interface', 'Curved interface']:
                self.refractiveIndex = element['refr_index']
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
            #print("element Type, value :" + element['Type'] + "\n " + str(element['matrix']))
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
                aux_vector = np.linspace(0,element['distance'],element['distance']*100)
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
                
                # Distance
                aux_vector = np.linspace(0,element['distance'],element['distance']*100)
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
                
                if show_n:
                    print(element['Type'],refr_index_global)
                    
                # Add finish position.
                z_limits.append(zmax)
                z_names.append(element['Type'])
                
            # ------------------- Brewster Plate -------------------
            elif element['Type']=="Brewster plate":
                # Block divided in interface - distance - interface
                # First interface
                I = abcd.flat_interface_br(refr_index_global,element['refr_index'])
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                
                # Distance
                thi = np.arctan(element['refr_index']/refr_index_global)    
                thr = np.arcsin( refr_index_global*np.sin(thi) / element['refr_index'] )    
                d_temp = element['distance'] / np.cos(thr)
                
                aux_vector = np.linspace(0,d_temp,d_temp*100)
                z.append(aux_vector+zmax)
                zmax = zmax + max(aux_vector)
                q = q0 + aux_vector
                q0 = q[-1]
                w = np.sqrt(-wl/(np.pi*element['refr_index']*np.imag(1/q)))
                wz.append(w)
                
                # Second interface
                I = abcd.flat_interface_br(element['refr_index'], refr_index_global)
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                
                if show_n:
                    print(element['Type'],refr_index_global)
                    
                # Add finish position.
                z_limits.append(zmax)
                z_names.append(element['Type'])
            
            # ------------------- Brewster Crystal -------------------
            elif element['Type']=="Brewster crystal":
                # Block divided in interface - distance - interface
                # First interface
                I = abcd.flat_interface_br(refr_index_global,element['refr_index'])
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                
                # Distance
                aux_vector = np.linspace(0,element['distance'],element['distance']*100)
                z.append(aux_vector+zmax)
                zmax = zmax + max(aux_vector)
                q = q0 + aux_vector
                q0 = q[-1]
                w = np.sqrt(-wl/(np.pi*element['refr_index']*np.imag(1/q)))
                wz.append(w)
                
                # Second interface
                I = abcd.flat_interface_br(element['refr_index'], refr_index_global)
                q = abcd.q_propagation(I[proy],q0)
                q0 = q
                
                if show_n:
                    print(element['Type'],refr_index_global)
                    
                # Add finish position.
                z_limits.append(zmax)
                z_names.append(element['Type'])
                
            else:
                print(element['Type'])
                print('Element not available!')
        return z, wz, z_limits, z_names
