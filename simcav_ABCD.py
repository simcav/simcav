# -*- coding: utf-8 -*-
"""
@author: Julio Rodriguez

ABCD matrix for optical ray analysis.
This suit includes several functions such as:
 - ABCD matrixes for different optical elements
 - q complex parameter calculation for resonators or single pass given the ABCD
 - radious of curvature and beam waist (R(z) and w(z)) for a given q
 - Calculation of the cavity matrix for a given cavity in a particular position
 
**This program uses milimeter (mm) as the standart unit for input and output.

The returns of the functions are lists of 2 elements: tangential and sagital matrix.


Tangential plane refers to the plane parallel to the optical table (horizontal).
Sagittal plane is perpendicular to the tangential plane (vertical).
"""

#%%
# Basic modules used.
import numpy as np
from numpy.lib.scimath import sqrt as csqrt  # Complex numbers square root

#%% ----------------------------------------------------------------------------
# Distance
def distance(d, n):
    M = np.array([[1,d],[0,1]])
    return [M, M]
    
#%% ----------------------------------------------------------------------------
# Thin lense   
def thin_lens(f,th):
    M_tan = np.array([[1,0],[-1/(f*np.cos(th)),1]])
    M_sag = np.array([[1,0],[-1/(f/np.cos(th)),1]])
    return [M_tan, M_sag]
    
#%% ----------------------------------------------------------------------------
# Flat mirror  
def flat_mirror(e1, e2):
    M = np.array([[1,0],[0,1]])
    return [M, M]
    
#%% ----------------------------------------------------------------------------
# Curved mirror 
def curved_mirror(R):
    M = np.array([[1,0],[-2/R,1]])
    # R = radius of curvature, R > 0 for concave (centre of curvature before mirror surface)
    return [M, M]
    
#%% ----------------------------------------------------------------------------
# Flat interface
def flat_interface(n1, n2):
    M = np.array([[1,0],[0,n1/n2]])
    return [M, M]
    
#%% ----------------------------------------------------------------------------
# Tilted flat interface - NOT for external (simcav) reference
def tilted_flat_interface(n1, n2, thi):
    # thi is in radians already
    thr = np.arcsin( n1*np.sin(thi) /n2 )
    M = np.array([ [np.cos(thr)/np.cos(thi),0] , [0, (n1*np.cos(thi)) / (n2*np.cos(thr))] ])
    return M

#%% ----------------------------------------------------------------------------
# Brewster flat interface
def flat_interface_br(n1, n2):
    M_sag = np.array([ [1,0] , [0,n1/n2] ])
    
    thb = np.arctan(n2/n1)
    M_tan = tilted_flat_interface(n1,n2,thb)
    
    return [M_tan, M_sag]
    
#%% ----------------------------------------------------------------------------
# Curved interface
def curved_interface(R, n1, n2):
    M = np.array([[1,0],[-(n1-n2)/(n2*R),n1/n2]])
    # R = radius of curvature, R > 0 for concave (centre of curvature before interface)
    return [M, M]
    
#%% ----------------------------------------------------------------------------
# Thick Lense
def thick_lens(R1, R2, d, n1, n2):
    M1 = curved_interface(R2,n2,n1)
    M2 = distance(d,n2)
    M3 = curved_interface(R1,n1,n2)
    M = np.dot(M3,np.dot(M2,M1))    
    return [M, M]
    
#%% ----------------------------------------------------------------------------
# Curved mirror tilted on tangential plane   
def tilted_curved_mirror(R,th):
    M_tan = np.array([[1,0],[-2/(R*np.cos(th)),1]])
    M_sag = np.array([[1,0],[-2/(R/np.cos(th)),1]])  
    return [M_tan, M_sag]
    
#%% ----------------------------------------------------------------------------
# Thin lens tilted on tangential plane   
def tilted_thin_lens(f,th):
    n = 1.5
    C = 1/(1/n**2-(np.sin(th))**2) * (np.cos(th)-np.sqrt(n**2-(np.sin(th))**2))/(2*f*np.sqrt(n**2-(np.sin(th))**2))
    M_tan = np.array([[1,0],[C,1]])
    M_sag = np.array([[1,0],[-1/f,1]])
    return [M_tan, M_sag]
    
#%% ----------------------------------------------------------------------------
# Curved interface tilted on tangential plane
def tilted_curved_interface(R, n1, n2, th):
    nr = n2/n1
    A = np.sqrt(nr**2-(np.sin(th))**2) / (nr*np.cos(th))
    C_tan = (np.cos(th)-np.sqrt(nr**2-(np.sin(th))**2))/(R*np.cos(th)*np.sqrt(nr**2-(np.sin(th))**2))
    D = np.cos(th) / np.sqrt(nr**2-(np.sin(th))**2)
    M_tan = np.array([[A,0],[C_tan,D]])
    
    C_sag = (np.cos(th)-np.sqrt(nr**2-(np.sin(th))**2))/(R*nr)
    M_sag = np.array([[1,0],[C_sag,1/nr]])
    
    return [M_tan, M_sag] 
    
#%% ----------------------------------------------------------------------------
# BLock of refractive index n, air outside.
def block(d,n):
    M = np.array([[1,d/n],[0,1]])
    return [M, M]

#%% --------------------- BREWSTER ELEMENT --------------------------
# BLock of refractive index n, air outside at Brewstwer's angle.
def brewster_crystal(d,n):
    M_tan = np.array([[1,d/n**3],[0,1]])
    M_sag = np.array([[1,d/n],[0,1]])
    return [M_tan, M_sag]
    
#%% --------------------- BREWSTER PLATE --------------------------
# Thicknes of the plate d, refractive index n, air outside.
def brewster_plate(d,n):
    thi = np.arctan(n)    
    thr = np.arcsin( np.sin(thi)/n )    
    d = d / np.cos(thr)
    M_tan = np.array([[1,d/n**3],[0,1]])
    M_sag = np.array([[1,d/n],[0,1]])
    return [M_tan, M_sag]
        
#%% ----------------------------------------------------------------------------
# Calculate q for resonator
def q_resonator(M):
    A = M[0,0]
    B = M[0,1]
    C = M[1,0]
    D = M[1,1]
    
    q_inv = (D-A) / (2*B) - np.abs(1/B) * csqrt((A+D)**2 / 4 - 1)
    return 1 / q_inv
    
#%% ----------------------------------------------------------------------------
# Calculate q1 for propagation from q0
def q_propagation(M,q0):
    A = M[0,0]
    B = M[0,1]
    C = M[1,0]
    D = M[1,1]
    
    q1 = (A*q0+B) / (C*q0+D)
    return q1
    
#%% ----------------------------------------------------------------------------
# Calculate q at any dimensionless (z) element
def q_element(q0, elementX, elementList):
    # Propagation from q0 to elementX.
    # elementX is an element in element_list
    
    # If elementX is a length element, stop function, return False
    #   Makes no sense to calculate the beam size for an element with
    #   a z dimension (in this case).
    # if elementX['isVector']:
    #     return False
    # MOVE THIS CHECKING OUTSIDE THE FUNCTION
    
    qProp = []
    for proy in [0,1]:
        matrix = np.identity(2)
        for element in elementList[1:elementX['Order']]:
            matrix = np.dot(element['matrix'][proy],matrix)
        # Calculate q(x)
        q = q_propagation(matrix, q0[proy])
        qProp.append(q)
    return qProp

#%% ----------------------------------------------------------------------------
# Calculate R(q) and w(q) (in mm)
def r_w(q, wl, n):
    R = 1/np.real(1/q)
    w = np.sqrt(-wl/(np.pi*n*np.imag(1/q)))
    return R, w
    
#%% ----------------- Propagation calculation ------------------------------    
def propagation(E_list, q0, wl, proy, chivato=False):    
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
      
    for counter, element in enumerate(E_list):
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
            if counter == 0:
                q = q0
                # First list element must be ignored since SimCav calculates q0 just after the first element
            else:
                q = q_propagation(element['matrix'][proy],q0)
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
            aux_vector = np.linspace(0,element['distance'],num=1001)
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
            I = flat_interface(refr_index_global,element['refr_index'])
            q = q_propagation(I[proy],q0)
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
            I = flat_interface(element['refr_index'], refr_index_global)
            q = q_propagation(I[proy],q0)
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
            I = flat_interface_br(refr_index_global,element['refr_index'])
            q = q_propagation(I[proy],q0)
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
            I = flat_interface_br(element['refr_index'], refr_index_global)
            q = q_propagation(I[proy],q0)
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
            I = flat_interface_br(refr_index_global,element['refr_index'])
            q = q_propagation(I[proy],q0)
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
            I = flat_interface_br(element['refr_index'], refr_index_global)
            q = q_propagation(I[proy],q0)
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