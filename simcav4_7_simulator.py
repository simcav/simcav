# -*- coding: utf-8 -*-
"""
Created on Tue May  5 15:07:43 2015

@author: Julio Rodriguez
"""
    
#%% --------------- Importing modules ------------------
import numpy as np
#import matplotlib.pyplot as plt
import simcav4_7_abcd as abcd

import imp
imp.reload(abcd)

n_air = 1.000

#%% ----------------- Cavity Matrix Calculation -----------------
def matrix(E_list, proy):
    # Takes the list of elements, as a list of dictionaries,
    # with an entry called "matrix"
    # "proy" states for the proyection, either 0 for tangential or 1 for sagital.
    M_cav = np.identity(2)
    
    #print(E_list,"\n\n")

    # Tangential or saggital proyection     
    for element in E_list[1:]:
        #print("element type, value :" + element['type'] + "\n " + str(element['matrix']))
        M_cav = np.dot(element['matrix'][proy],M_cav)
        
    for element in E_list[len(E_list)-2::-1]:
        M_cav = np.dot(element['matrix'][proy],M_cav)
    
    return M_cav

 #%% ------------------- Starting point size calculation -----------------------    
def q0(M_cav):
    # Beam complex paramenter
    q0 = abcd.q_resonator(M_cav)
    return q0

#%% ------------- Calculate q at any dimensionless (z) element ----------------- 
def qx(q0, elementX, E_list, proy):
    # Propagation from q0 to elementX.
    # elementX is the itemnumber of the element in element_list
    
    # If elementX is a length element, stop function, return False
    #   Makes no sense to calculate the beam size for an element with
    #   a z dimension (in this case).
    if E_list[elementX]['isvector']:
        return False
    
    M_cav = np.identity(2)
    for element in E_list[1:elementX]:
        #print("element type, value :" + element['type'] + "\n " + str(element['matrix']))
        M_cav = np.dot(element['matrix'][proy],M_cav)
    # Calculate q(x)
    q = abcd.q_propagation(M_cav,q0)
    return q    
    
#%% -------------------- Stability Condition --------------------
# Calculates stability and prints out if stable or not.    
def stability(M_cav, v=False):
    if abs((M_cav[0,0] + M_cav[1,1]) / 2) < 1:
        if v:
            print("Stability condition: -1 < " + str( (M_cav[0,0] + M_cav[1,1]) / 2) + ' < 1')
            print("Stable!")
        return True
    else:
        if v:
            print("Stability condition:" + str( (M_cav[0,0] + M_cav[1,1]) / 2) )
            print("NOT Stable!")
        return False

#%% -------------------- Stability Condition --------------------
# Calculates stability and returns value.    
def stabilitycalc(M_cav):
    stab = (M_cav[0,0] + M_cav[1,1]) / 2
    if stab < 1 and stab > -1:
        stabnorm = 1 - stab**2
    else:
        stabnorm = 0
    return stabnorm


#%% ----------------- Propagation calculation ------------------------------    
def propagation(E_list, q0, wl, proy, chivato):    
    # Propagation
    zmax = 0
    z = []
    wz = []
    #z.append(0)

    # Debugging ----------------------------------------
    show_n = False   
    if chivato:
        print('Im in SIMU.propagation. For loop through elements:')
    if show_n:
        print(' ')
        print('Refractive index')
    #---------------------------------------------------
    
    refr_index_global = 1.0 
      
    for element in E_list:
        # Some debugging
        if chivato:
            print(element['type'])
        
        # ------------------- Mirror -------------------
        if (
            (element['type']=="Flat mirror") or 
            (element['type']=="Curved mirror") or 
            (element['type']=="Thin lens") or
            (element['type']=="Flat interface") or
            (element['type']=="Curved interface") or
            (element['type']=="Custom element") ):
            
            # Calculate complex beam parameter (q)
            q = abcd.q_propagation(element['matrix'][proy],q0)
            q0 = q
            
            # Modify refractive index of the medium
            if 'refr_index' in element.keys():
                refr_index_global = element['refr_index']
            if show_n:
                print(element['type'],refr_index_global)
                        
            # Some debugging
            if chivato:
                print('Imag(q)',np.imag(q))
            
            #if z:
            #    plt.vlines(z[-1][-1],0,1)
        
        # ------------------- Distance -------------------            
        elif element['type']=="Distance":
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
                print(element['type'],refr_index_global)
        
        # ------------------- Block -------------------
        elif element['type']=="Block":
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
                print(element['type'],refr_index_global)
                    
        # ------------------- Brewster Plate -------------------
        elif element['type']=="Brewster plate":
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
                print(element['type'],refr_index_global)
        
        # ------------------- Brewster Crystal -------------------
        elif element['type']=="Brewster crystal":
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
                print(element['type'],refr_index_global)
            
        else:
            print(element['type'])
            print('Element not available!')
    return z, wz