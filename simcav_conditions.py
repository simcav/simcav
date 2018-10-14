import simcav_physics as SP
import simcav_ABCD as abcd

allConditions = ["w(0)", "w(element)", "Waist", "Cav. length", "Stability"]

def evalConditions(cavityMatrix, elementList, stability, conditionName, conditionAt, condStart, condEnd, wavelength):
    if conditionName == "w(0)":
        w0 = cond_w0_size(cavityMatrix, condStart, condEnd, wavelength)
        return w0
    elif conditionName == "w(element)":
        wz = cond_waist(cavityMatrix, elementList, conditionAt, wl, condStart, condEnd)
        return wz
    elif conditionName == "Waist":
        pass
    elif conditionName == "Cav. length":
        pass
    elif conditionName == "Stability":
        pass        
    

# ------------------- CONDITIONS ---------------------
def cond_w0_size(cavityMatrix, condStart, condEnd, wl):
    w0 = []
    for matrix in cavityMatrix:
        q0 = abcd.q_resonator(matrix)
        r0, w0_pre = abcd.r_w(q0, wl, 1)
        w0_pre = w0_pre*1000    # Convert to µm

        if (w0_pre > condStart and  w0_pre < condEnd):
            w0.append(w0_pre)
    return w0

def cond_waist(cavityMatrix, elementList, conditionAt, wl, condStart, condEnd):
    q0 = []
    for matrix in cavityMatrix:
        q0.append(abcd.q_resonator(matrix))
    
    #q = abcd.q_element(q0, conditionAt-1, elementList)
            
    proy = 0
    z_tan, wz_tan, z_limits_tan, z_names_tan = SP.propagation(elementList, q0[proy], wl, proy)
    proy = 1
    z_sag, wz_sag, z_limits_sag, z_names_sag = SP.propagation(elementList, q0[proy], wl, proy)
    # Join and convert to µm
    wz_both = [wz_tan*1000, wz_sag*1000]

    if master.toolbar.chivato:
        print('In waist condition')
        print('I(1/q)=',np.imag(1/q0))
        
    wz_min = []
    for wz in wz_both:
        # Check that min is not an edge
        if (
            min(wz[conditionAt]) < wz[conditionAt][0]
            and
            min(wz[conditionAt]) < wz[conditionAt][-1]
            ):

            if (
                min(wz[conditionAt]) > condStart
                and
                min(wz[conditionAt]) < condEnd
                ):
                wz_min.append(min(wz[conditionAt]))
    return wz_min

def cav_distance(self, condition):
    total_distance = 0
    for element in self.computation_elements:
        if element['type'] in ['Distance','Block','Brewster plate']:
            total_distance = total_distance + element['distance']
        else:
            pass
    if (
        total_distance >= float(condition['entry1'].get())
        and
        total_distance <= float(condition['entry2'].get())
        ):
        return total_distance*1E-3
    else:
        return False
# ----------------------------------------------------