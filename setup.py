# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 16:36:31 2016

@author: mhb13219
"""

from distutils.core import setup
import py2exe

#setup(windows=['simcav4_1_GUI.py'])

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True,"includes":["tkinter"]}},
    windows = [{'script': "simcav4_1_GUI.py"}],
    zipfile = None,
    #data_files = DATA,
)