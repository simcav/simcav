# -*- coding: utf-8 -*-
"""
Created on Sat May 23 21:14:11 2015

@author: julio
"""

import simcav4_7_abcd as abcd
import tkinter.simpledialog as tkdiag
import imp
imp.reload(abcd)
import numpy as np

def assignment(element, entry1, entry2, refr_index):
    myDict = {}    
    
    # Flat mirror
    if element == 'Flat mirror':
        I = abcd.flat_mirror(entry1, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
    
    # Curved mirror
    elif element == 'Curved mirror':
        entry2 = entry2 * np.pi / 180
        I = abcd.tilted_curved_mirror(entry1, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
    
    # Thin lens
    elif element == 'Thin lens':
        entry2 = entry2 * np.pi / 180
        I = abcd.thin_lens(entry1, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
    # --------------------------------------------------------
                
    # Distance
    elif element == 'Distance':
        I = abcd.distance(entry1, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
        
    # Block
    elif element == 'Block':
        I = abcd.block(entry1, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
    # --------------------------------------------------------
    
    # --------------- BREWSTER PLATE -----------------------        
    # Brewster plate
    elif element == 'Brewster plate':
        I = abcd.brewster_plate(entry1, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
    
    # --------------- BREWSTER CRYSTAL -----------------------        
    # Brewster crystal
    elif element == 'Brewster crystal':
        I = abcd.brewster_crystal(entry1, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
    
    # --------------- CUSTOM ELEMENT -----------------------        
    # Custom element
    elif element == 'Custom element':
        I = []
        for i,j in zip([1,2,3,4],['A','B','C','D']):
            I.append(tkdiag.askfloat('Custom ABCD element', ['Element',j] ))
        M = np.array([[I[0],I[1]],[I[2],I[3]]])
        myDict['type'] = element
        myDict['matrix'] = [M,M]
        myDict['distance'] = entry1
        myDict['refr_index'] = entry2
        myDict['done'] = 1
    
    # --------------- ITERFACES -----------------------        
    # Flat interface
    elif element == 'Flat interface':
        I = abcd.flat_interface(refr_index, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
        #myDict['n1'] = entry1
        myDict['refr_index'] = entry2
        
    # Curved interface
    elif element == 'Curved interface':
        I = abcd.curved_interface(entry1, refr_index, entry2)
        myDict['type'] = element
        myDict['matrix'] = I
        myDict['refr_index'] = entry2
        
        
    else:
        print(element)
        print('Error')
    
    return myDict