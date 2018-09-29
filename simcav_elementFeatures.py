import simcav_ABCD as abcd
import tkinter.simpledialog as tkdiag
import numpy as np

def assign(elementType, entry1, entry2, refr_index=1.0):
    myDict = {}
    
    myDict['entry1'] = entry1
    myDict['entry2'] = entry2
    
    # Flat mirror
    if elementType == 'Flat Mirror':
        I = abcd.flat_mirror(entry1, entry2)
        myDict['matrix'] = I
    
    # Curved mirror
    elif elementType == 'Curved Mirror':
        entry2 = entry2 * np.pi / 180
        I = abcd.tilted_curved_mirror(entry1, entry2)
        myDict['matrix'] = I
    
    # Thin lens
    elif elementType == 'Thin Lens':
        entry2 = entry2 * np.pi / 180
        I = abcd.thin_lens(entry1, entry2)
        myDict['matrix'] = I
    # --------------------------------------------------------
                
    # Distance
    elif elementType == 'Distance':
        I = abcd.distance(entry1, entry2)
        myDict['matrix'] = I
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
        
    # Block
    elif elementType == 'Block':
        I = abcd.block(entry1, entry2)
        myDict['matrix'] = I
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
    # --------------------------------------------------------
    
    # --------------- BREWSTER PLATE -----------------------        
    # Brewster plate
    elif elementType == 'Brewster Plate':
        I = abcd.brewster_plate(entry1, entry2)
        myDict['matrix'] = I
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
    
    # --------------- BREWSTER CRYSTAL -----------------------        
    # Brewster crystal
    elif elementType == 'Brewster Crystal':
        I = abcd.brewster_crystal(entry1, entry2)
        myDict['matrix'] = I
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
    
    # --------------- CUSTOM ELEMENT -----------------------        
    # Custom element
    elif elementType == 'Custom Element':
        I = []
        for i,j in zip([1,2,3,4],['A','B','C','D']):
            I.append(tkdiag.askfloat('Custom ABCD element', ['Element',j] ))
        M = np.array([[I[0],I[1]],[I[2],I[3]]])
        myDict['matrix'] = [M,M]
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
        myDict['done'] = 1
    
    # --------------- INTERFACES -----------------------        
    # Flat interface
    elif elementType == 'Flat Interface':
        I = abcd.flat_interface(refr_index, entry2)
        myDict['matrix'] = I
        #myDict['n1'] = entry1
        myDict['refr_index'] = entry2
        
    # Curved interface
    elif elementType == 'Curved Interface':
        I = abcd.curved_interface(entry1, refr_index, entry2)
        myDict['matrix'] = I
        myDict['refr_index'] = entry2
        
        
    else:
        print(elementType)
        print('Error: Element does not exist.')
    
    return myDict