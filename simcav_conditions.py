import numpy as np
import simcav_physics as SP
import simcav_ABCD as abcd

allConditions = ["Stability", "w(0)", "w(element)", "Waist", "Cav. length"]

def evalConditions(cavityMatrix, elementList, stability, conditionName, conditionAt, conditionAtNumber, condStart, condEnd, wavelength):
    if conditionName == "w(0)":
        w0 = cond_w0_size(cavityMatrix, condStart, condEnd, wavelength)
        return w0
    elif conditionName == "w(element)":
        wX = cond_w_element(cavityMatrix, elementList, conditionAt, condStart, condEnd, wavelength)
        return wX
    elif conditionName == "Waist":
        wz = cond_waist(cavityMatrix, elementList, conditionAtNumber, condStart, condEnd, wavelength)
        return wz
    elif conditionName == "Cav. length":
        length = cond_cavDistance(elementList, condStart, condEnd)
        return length
    elif conditionName == "Stability":
        stability = cond_stability(cavityMatrix, condStart, condEnd)  
        return stability      
    

# ------------------- CONDITIONS ---------------------
def cond_stability(cavityMatrix, condStart, condEnd):
    stability = []
    for matrix in cavityMatrix:
        stab = (matrix[0,0] + matrix[1,1]) / 2
        stab = 1 - stab**2
        if (stab >= condStart and stab <= condEnd):
            stability.append(stab)
        else:
            return False
    return stability
def cond_w0_size(cavityMatrix, condStart, condEnd, wl):
    w0 = []
    for matrix in cavityMatrix:
        q0 = abcd.q_resonator(matrix)
        r0, w0_pre = abcd.r_w(q0, wl, 1)
        w0_pre = w0_pre*1000    # Convert to µm

        if (w0_pre >= condStart and  w0_pre <= condEnd):
            w0.append(w0_pre)
    return w0
    
def cond_w_element(cavityMatrix, elementList, conditionAt, condStart, condEnd, wl):
    elementX = elementList[conditionAt]
    try:
        refractiveIndex = elementX['refr_index']
    except:
        refractiveIndex = 1
    
    q0 = []    
    for matrix in cavityMatrix:
        q0.append(abcd.q_resonator(matrix))
        
    q = abcd.q_element(q0, elementX, elementList)
    
    r, w_tan = abcd.r_w(q[0], wl, refractiveIndex)
    r, w_sag = abcd.r_w(q[1], wl, refractiveIndex)
    w_tan = w_tan*1000    # Convert to µm
    w_sag = w_sag*1000    # Convert to µm
    
    if ((w_tan >= condStart and  w_tan <= condEnd) and 
        (w_sag >= condStart and  w_sag <= condEnd)):
        w = [w_tan, w_sag]
        return w
    else:
        return False

def cond_waist(cavityMatrix, elementList, conditionAtnumber, condStart, condEnd, wl):
    q0 = []
    for matrix in cavityMatrix:
        q0.append(abcd.q_resonator(matrix))
            
    proy = 0
    z_tan, wz_tan, z_limits_tan, z_names_tan = abcd.propagation(elementList, q0[proy], wl, proy)
    proy = 1
    z_sag, wz_sag, z_limits_sag, z_names_sag = abcd.propagation(elementList, q0[proy], wl, proy)
    # Join and convert to µm
    wz_both = [np.array(wz_tan)*1000, np.array(wz_sag)*1000]
        
    wz_min = []
    for wz in wz_both:
        # I WAS FORCING THE SOLUTION NOT TO BE AN EDGE OF THE DISTANCE, BUT THAT IS ACTUALLY A VALID SOLUTION
        if (
            min(wz[conditionAtnumber]) >= condStart
            and
            min(wz[conditionAtnumber]) <= condEnd
            ):
            wz_min.append(min(wz[conditionAtnumber]))
        else:
            return False
    return wz_min

def cond_cavDistance(elementList, condStart, condEnd):
    total_distance = 0
    for element in elementList:
        if element['Type'] in ['Distance','Block','Brewster Plate','Brewster Crystal']:
            total_distance = total_distance + element['distance']
        else:
            pass
    if (
        total_distance >= condStart
        and
        total_distance <= condEnd
        ):
        return total_distance
    else:
        return False
# ----------------------------------------------------