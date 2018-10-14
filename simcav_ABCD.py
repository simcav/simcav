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

The returns of the functions are lists of 2 elements: tangential and sagital matrix.#


Tangential plane refers to the plane parallel to the optical table (horizontal).
Sagittal plane is perpendicular to the tangential plane (vertical).


The matrixes this file gives have been reviewed at 03/2016.
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
    
    q = (-(D-A) + csqrt((D-A)**2 + 4*B*C))/(2*np.abs(C))
    return q
    
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
def r_w(q,wl,n):
    R = 1/np.real(1/q)
    w = np.sqrt(-wl/(np.pi*n*np.imag(1/q)))
    return R, w