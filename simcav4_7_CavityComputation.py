# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 09:55:00 2015

@author: mhb13219
"""

import simcav4_7_simulator as SIMU

def conditions(self):
    import simcav4_7_GUI as GUI
    
        #%% ------------------ w0 on a range --------------------------        
    def w0_size(self, w0, wmin, wmax):
        # Check that min is not an edge 
        if (min(w0) > wmin and min(w0) < wmax):
            return True
        else:
            return False
    
    #%% ------------------ Waist on a range --------------------------
    def waist(self, vector, wmin, wmax):
        # Check that min is not an edge 
        if (min(vector) < vector[0] and min(vector) < vector[-1]):
            if (min(vector) > wmin and min(vector) < wmax):
                return True
            else:
                return False
        else:
            return False

    def max_distance(self, cavity_elements):
        cav_distance = 0
        for element in cavity_elements:
            if element['type'] in ['Distance','Block','Brewster plate']:
                cav_distance = cav_distance + element['distance']
            else:
                pass
        return cav_distance