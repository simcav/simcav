# -*- coding: utf-8 -*-
"""
Created on Sat May 23 21:14:11 2015

@author: julio
"""
# Import for GUI
import sys
if sys.version_info < (3, 0):
    print('Please update your python version. This program only works with Python 3')
else:
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.filedialog
    import tkinter.messagebox

# Imports for functionality
import simcav4_7_ElementFeatures as EF
import simcav4_7_simulator as SIMU
import simcav4_7_abcd as ABCD
import itertools
import pickle
import numpy as np
import os

# Imports for plotting
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt

# import for scrolled window
import scrolledframe as scrollf
import tooltips as tt


# File path function for deployment in single file with PyInstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


#==============================================================================
#%% Toolbar
class Toolbar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Chivato
        self.chivato = False

        self.toolbar_buttons = {}

        # Loading icons
        self.img_new = tk.PhotoImage(file=resource_path("Icons/t_new.png"))
        self.img_add = tk.PhotoImage(file=resource_path("Icons/t_edit.png"))
        self.img_save = tk.PhotoImage(file=resource_path("Icons/t_save.png"))
        self.img_load = tk.PhotoImage(file=resource_path("Icons/t_load.png"))
        self.img_compute = tk.PhotoImage(file=resource_path("Icons/t_calcu.png"))
        self.img_quit = tk.PhotoImage(file=resource_path("Icons/t_quit.png"))
        self.img_quit2 = tk.PhotoImage(file=resource_path("Icons/t_quit2.png"))
        #self.img_test = tk.PhotoImage(file="test.gif")

        # Creating buttons
        self.toolbar_buttons['a0_separator'] = ttk.Separator(self, orient='vertical')
        self.toolbar_buttons['a_button_new'] = tk.Button(self, text='New',
                                               image=self.img_new, command=self.func_button_new,
                                               highlightthickness=0)
        self.toolbar_buttons['b_button_load'] = tk.Button(self, text='Load',
                                                image=self.img_load, command=self.func_button_load,
                                                highlightthickness=0)
        self.toolbar_buttons['c_button_save'] = tk.Button(self, text='Save',
                                                image=self.img_save, command=self.func_button_save,
                                                highlightthickness=0)
        self.toolbar_buttons['d0_separator'] = ttk.Separator(self, orient='vertical')
        self.toolbar_buttons['d_button_add'] = tk.Button(self, text='Add',
                                               image=self.img_add, command=self.func_button_add,
                                               highlightthickness=0)
        self.toolbar_buttons['e_button_computation'] = tk.Button(self, text='Computing',
                                                       image=self.img_compute,
                                                       command=self.func_button_computation,
                                                       highlightthickness=0)
        self.toolbar_buttons['f0_separator'] = ttk.Separator(self, orient='vertical')
        self.toolbar_buttons['z_button_quit'] = tk.Button(self, text='Quit',
                                                image=self.img_quit, command=self.func_button_quit,
                                                highlightthickness=0)
        #self.toolbar_buttons['f_test'] = tk.Button(self, text='TEST', image=self.img_test, command=self.func_button_test)

        # Setting some common configuration and packing the buttons
        for button in sorted(self.toolbar_buttons):
            # Adding features to all icons and packing them.
            if button == 'z_button_quit':
                # But quit icon goes apart
                self.toolbar_buttons[button].configure(width=35, height=35, bd=0, bg='white', activebackground='white')
                self.toolbar_buttons[button].pack(side='right')
                self.toolbar_buttons[button].bind("<Enter>", self.func_quit_enter)
                self.toolbar_buttons[button].bind("<Leave>", self.func_quit_leave)
            elif 'separator' in button:
                self.toolbar_buttons[button].pack(side='left', fill='y')
            else:
                self.toolbar_buttons[button].configure(width=35, height=35, bd=0, bg='white')
                self.toolbar_buttons[button].bind('<Enter>', self.func_color_enter)
                self.toolbar_buttons[button].bind('<Leave>', self.func_color_leave)
                self.toolbar_buttons[button].pack(side='left')

        # Tooltips
        self.testtip = tt.createToolTip(self.toolbar_buttons['a_button_new'], "New cavity")
        self.testtip = tt.createToolTip(self.toolbar_buttons['b_button_load'], "Load cavity")
        self.testtip = tt.createToolTip(self.toolbar_buttons['c_button_save'], "Save cavity")
        self.testtip = tt.createToolTip(self.toolbar_buttons['d_button_add'], "Modify cavity")
        self.testtip = tt.createToolTip(self.toolbar_buttons['e_button_computation'], "Design calculator")
        # Quit tooltip removed because it interferes with icon change.
        #self.testtip = tt.createToolTip(self.toolbar_buttons['z_button_quit'], "Quit")

        # Wavelength labels and entry.
        self.label_wl = tk.Label(self, text='Wavelength = ', padx=2, pady=4, bd=0, width=25, bg='white', anchor='e')
        self.label_wlunits = tk.Label(self, text=' nm', pady=1, bd=0, bg='white')
        self.entry_wl = tk.Entry(self, width=7, justify='right')
        # Automatic value, my usual working wavelength.
        self.entry_wl.insert(0, 675)
        # Sending the value to the program.
        self.entry_wl.bind("<Return>", self.eval_entry_wl)

        # Packing wavelength stuff.
        self.label_wl.pack(side='left')
        self.entry_wl.pack(side='left')
        self.label_wlunits.pack(side='left')

        #self.button_test = tk.Button(self, text='TEST', command=self.func_button_test, bd=0, bg='white')
        #self.button_test.pack(side='left')


    def func_button_test(self):
        # This button is for testing purposes
        pass

    def func_button_computation(self):
        # Opens computation tab.
        computation = master.frameright.show_cavitycomputation()
        if computation:
            master.frameright.cavitycomputation.build_interface()
            master.warningbar.warbar_message('Ready to calculate!', 'lawn green')
            return True
        else:
            self.func_button_add()
            master.warningbar.warbar_message('Not enough elements to compute. First build a cavity!', 'firebrick')
            return False

    def func_button_new(self):
        # Sets the program ready for a clean start.

        # Delete all elements
        for element in master.physics.element_list:
            element['checkbutton_var'].set(True)
        # Calling delete button
        master.elementbox.func_delete_button()
        # New fresh element list
        master.physics.element_list = []
        # Ready to add elements
        master.toolbar.func_button_add()
        master.warningbar.warbar_message('New cavity  --  Adding elements...', 'lawn green')

    def func_button_quit(self):
        # Close program
        killing_root()

    def func_button_add(self):
        # Shows tab for add/delete cavity elements
        master.frameright.show_cavityelements()
        master.warningbar.warbar_message('Modifying cavity...', 'lawn green')
        # This button allows cavity modifications

    def func_button_save(self):
        # Saves designed cavity
        saving = self.file_save()
        if saving:
            master.warningbar.warbar_message('Save successful...', 'lawn green')
        if not saving:
            master.warningbar.warbar_message('Error while saving!', 'firebrick')
        return saving

    def func_button_load(self):
        # Loads a previously saved cavity
        master.warningbar.warbar_message('Loading file...', 'lawn green')
        loading = self.file_load()
        if loading:
            master.warningbar.warbar_message('Load successful...', 'lawn green')
        if not loading:
            master.warningbar.warbar_message('Error while loading!', 'firebrick')
        return loading

    # Used when saving a file
    def file_save(self):
        # Open file in wb mode (byte writing)
        fout = tk.filedialog.asksaveasfile(mode='wb', defaultextension=".sc",
                                           filetypes=(("SimCav file", "*.sc"),("All Files", "*.*")),
                                           initialdir='Saves')
        if fout == None:
            return False

        saving_list = []
        for element in master.physics.element_list:
            my_dict = {}
            my_dict['type'] = element['type']
            my_dict['entry1_val'] = element['entry1'].get()
            my_dict['entry2_val'] = element['entry2'].get()
            my_dict['wavelength'] = master.physics.wl_mm
            saving_list.append(my_dict)

        pickle.dump(saving_list, fout)
        fout.close()
        return True

    # Used when loading a file
    def file_load(self):
        # Clear workspace
        self.func_button_new()
        """open a file to read"""
        # The filetype mask (default is sc files)
        mask = \
        [("SimCav files","*.sc"),("All Files", "*.*")]
        fin = tk.filedialog.askopenfile(filetypes=mask, mode='rb',
                                        initialdir='Saves')
        if fin == None:
            return False

        self.saved_list = pickle.load(fin)

        for element in self.saved_list:
            # adds the saved elements
            master.elementbox.add_element(element['type'])

        # Now add the values:
        for index, element in enumerate(self.saved_list):
            # Deletes default values
            master.physics.element_list[index]['entry1'].delete(0, tk.END)
            master.physics.element_list[index]['entry2'].delete(0, tk.END)
            self.entry_wl.delete(0, tk.END)
            # Sets loaded values
            master.physics.element_list[index]['entry1'].insert(0, element['entry1_val'])
            master.physics.element_list[index]['entry2'].insert(0, element['entry2_val'])
            master.physics.wl_mm = element['wavelength']
            self.entry_wl.insert(0, round(master.physics.wl_mm*1E8)/100)

        # Calculate and plot
        master.elementbox.func_button_calc()
        return True

    # Evaluates wavelength
    def eval_entry_wl(self, event):
        wl = self.entry_wl.get()
        try:
            wl = float(wl)
            master.physics.calc_wl(wl)
            master.warningbar.warbar_message('Wavelength changed to %.2f nm -- Please update the calculations' %wl, 'lawn green')
            return wl
        except ValueError:
            master.warningbar.warbar_message('Error: Wavelength NaN', 'firebrick')
            return False

    #--------------------------------------------
    # Probably unseful functions... Thsi is handled by the activebackground property of each widget
    def func_color_enter(self, event):
        event.widget.configure(bg='aquamarine')
    def func_color_leave(self, event):
        event.widget.configure(bg='white')

    def func_quit_enter(self, event):
        event.widget.configure(image=self.img_quit2)
    def func_quit_leave(self, event):
        event.widget.configure(image=self.img_quit)
    #--------------------------------------------

#==============================================================================


#==============================================================================
#%% Warningbar
class Warningbar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.label_warning = tk.Label(self, text=' ', pady=4)
        self.label_warning.pack(fill='x')
        self.warbar_nomessage()

    def warbar_message(self, newtext, newcolor):
        # Call this function to display a new message in the warningbar.
        self.label_warning.configure(text=newtext, bg=newcolor, font='bold')

    def warbar_nomessage(self):
        # Call this function to display "No messages" in the warning bar.
        self.warbar_message('No messages','grey')


#==============================================================================


#==============================================================================
#%% Physics
class Physics():
    # This class handles the calculations needed to plot a cavity.
    # Ussually uses other modules (eg. simulator)
    def __init__(self):
        self.wl_mm = 675E-6
        self.element_list = []
        self.refr_index = 1
    
    # element_list holds all the information of every element in the cavity:
    # checkbutton_var: PY_VAR6
    # checkbutton: .!mainapplication.!elementbox.!checkbutton2
    # label: .!mainapplication.!elementbox.!label10
    # entry1: .!mainapplication.!elementbox.!entry5
    # entry2: .!mainapplication.!elementbox.!entry6
    # type:         Type of element, as the element button names
    # matrix:       ABCD matrix
    # distance:     first column value
    # refr_index:   second column value
    # itemnumber:   position in the cavity.
    # itemnumber_label: .!mainapplication.!elementbox.!label11


    def calc_matrix(self, el_list, proy):
        matrix = SIMU.matrix(el_list, proy)
        return matrix

    def calc_wl(self, wl):
        self.wl_mm = wl*1E-6
        master.warningbar.warbar_message('Wavelength = %.2f nm' %wl, 'lawn green')
        return True

    def calc_stability(self, **kw):
        stable = SIMU.stability(self.matrix, **kw)
        return stable

    def closed_cavity(self, **kw):
        # Check that both sides of the cavity have mirrors
        # ie. check that is closed cavity, not open
        side1 = self.element_list[0]["type"]
        side2 = self.element_list[-1]["type"]

        if "mirror" in (side1 and side2):
            return True
        else:
            return False
        
    def element_lengths(self, **kw):
        for element in self.element_list:
            if element['type'] in ['Distance','Block','Brewster plate','Brewster crystal']:
                if element['distance'] == 0:
                    self.zeroelement = element['itemnumber']
                    return False
        return True
                

    def calc_cavity(self, proy):
        master.toolbar.eval_entry_wl("<Return>")
        self.matrix = self.calc_matrix(self.element_list, proy)
        
        # Check no 0-length distance elements
        self.nozeros = self.element_lengths()
        # And also check that it is a closed cavity
        self.closed = self.closed_cavity()
        # Before anything check stability
        self.stable = self.calc_stability()
        
        # The conditions here should also be added in "Cavityplot(tk.Frame)"
        #       inside the function "plot(self, x1, y1, x2, y2)"
        #       in the (first?) condition.
        if (self.stable and self.closed and self.nozeros):
            master.warningbar.warbar_message('Cavity stable!', 'lawn green')
            self.q0 = SIMU.q0(self.matrix)
            if proy == 0:
                self.z_tan, self.wz_tan = SIMU.propagation(self.element_list, self.q0, self.wl_mm, proy, master.toolbar.chivato)
            elif proy == 1:
                self.z_sag, self.wz_sag = SIMU.propagation(self.element_list, self.q0, self.wl_mm, proy, master.toolbar.chivato)
            return True
        # If any of the conditions aren't matched, stop calculation, throw error
        else:
            master.framecentral.cavityplot.plot(1, 1, 1, 1)
            master.framecentral.cavityplot.figureplot.clear()
            master.framecentral.cavityplot.canvas.show()
            if not self.closed:
                master.warningbar.warbar_message('Mirrors needed at the sides of the cavity!', 'firebrick')
            elif not self.nozeros:
                master.warningbar.warbar_message(['Element',self.zeroelement,'no distance defined'], 'firebrick')
            else:
                master.warningbar.warbar_message('Cavity not stable!', 'firebrick')
            return False

    def stability_plot(self, item, xstart, xend):
        self.xvec = np.linspace(xstart, xend, np.abs(xend-xstart)*100)
        stab_list = self.element_list

        self.yvec = []
        for proy in [0,1]:
            y = []
            for number in self.xvec:
                # Now modify ONLY the first entry of the chosen item, and the associated matrix:
                e1 = number
                e2 = float(stab_list[item]['entry2'].get())
                kind = stab_list[item]['type']
                if kind == 'Custom element':
                    pass
                else:
                    stab_list[item].update(EF.assignment(kind, e1, e2, master.physics.refr_index))

                stab_matrix = self.calc_matrix(stab_list, proy)
                stab_val = (-1)**proy * SIMU.stabilitycalc(stab_matrix)
                y.append(stab_val)

            self.yvec.append(y)
        
        xname = 'Element '+str(item)+' variation (mm)'
        yname = 'Saggital         Stability (norm.)       Tangential'
        master.framecentral.stabilityplot.plotframe.plot(self.xvec, np.array(self.yvec[0]), self.xvec, np.array(self.yvec[1]), xstart, xend, xname, yname, ymin=-1, ymax=1)
#==============================================================================


#==============================================================================
#%% Element box
class Elementbox(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.pack_propagate(0)
        self.icon_go = tk.PhotoImage(file=resource_path("Icons/final_go.gif"))
        self.img_del1 = tk.PhotoImage(file=resource_path("Icons/e_delete.png"))
        self.img_del2 = tk.PhotoImage(file=resource_path("Icons/e_delete2.png"))

        #self.img_calc = tk.PhotoImage(file="black_calc.gif")
        self.label_title = tk.Label(self, text='Cavity', width=30, fg='white', bg='sea green', font=('bold',13))
        self.button_calc = tk.Button(self, text='CALCULATE', image=self.icon_go,
                                     command=self.func_button_calc, bg='white', 
                                     bd=0, highlightthickness=0, width=38, height=38)
        self.button_delete = tk.Button(self, text = 'Delete', image=self.img_del1,
                                        command=lambda: master.elementbox.func_delete_button(),
                                        highlightthickness=0, width=120, height=30, bd=0, bg='white')
        self.button_delete.bind('<Enter>', self.button_delete_enter)
        self.button_delete.bind('<Leave>', self.button_delete_leave)
        self.label_column0 = tk.Label(self, text=' ', bg='white')
        self.label_column1 = tk.Label(self, text='#', bg='white', width=2)
        self.label_column2 = tk.Label(self, text='Element', bg='white', width=15)
        self.label_column3 = tk.Label(self, text='(mm)', bg='white')
        self.label_column4 = tk.Label(self, text='n or þ', bg='white')

        self.label_title.grid(row=0, columnspan=5, sticky='ew')
        self.label_column0.grid(row=1, column=0)
        self.label_column1.grid(row=1, column=1)
        self.label_column2.grid(row=1, column=2, sticky='ew')
        self.label_column3.grid(row=1, column=3)
        self.label_column4.grid(row=1, column=4)
        
    def button_delete_enter(self, event):
        event.widget.configure(image=self.img_del2)

    def button_delete_leave(self, event):
        event.widget.configure(image=self.img_del1)
#==============================================================
#       Adding ELEMENTS
#==============================================================
    def add_element(self, kind):
        master.warningbar.label_warning.configure(text='Added ' + kind)
        # Adds elements in the frame, with boxes for options
        myDict = {}
        myDict['checkbutton_var'] = tk.BooleanVar()
        myDict['checkbutton'] = tk.Checkbutton(self, offvalue=False, onvalue=True,
                                               variable = myDict['checkbutton_var'], bg='white', highlightthickness=0)
        myDict['label'] = tk.Label(self, text=kind, width=15, anchor='w', bg='white')
        myDict['entry1'] = tk.Entry(self, width=5, justify='right')
        myDict['entry2'] = tk.Entry(self, width=5, justify='right')

        # Return key binding for entries
        myDict['entry1'].bind("<Return>", self.pressed_enter)
        myDict['entry2'].bind("<Return>", self.pressed_enter)
        
        # Add var to differentiate lengths-elements or not.
        if kind in ['Distance','Block','Brewster plate','Brewster crystal']:
            myDict['isvector'] = True
        else:
            myDict['isvector'] = False             

        # Default values for the entries
        if kind in ['Distance','Block','Brewster plate','Brewster crystal']:
            myDict['entry1'].insert(0, 1)
            myDict['entry2'].insert(0, 1)
        elif kind in ['Curved mirror','Thin lens']:
            myDict['entry1'].insert(0, 100)
            myDict['entry2'].insert(0, 0)
        elif kind == 'Curved interface':
            myDict['entry1'].insert(0, 100)
            myDict['entry2'].insert(0, 1)
        elif kind == 'Flat mirror':
            myDict['entry1'].insert(0, 1)
            myDict['entry2'].insert(0, 1)
            myDict['entry1'].configure(state='disable')
            myDict['entry2'].configure(state='disable')
        elif kind == 'Flat interface':
            myDict['entry1'].insert(0, 1)
            myDict['entry2'].insert(0, 1)
            myDict['entry1'].configure(state='disable')
        else:
            myDict['entry1'].insert(0, 0)
            myDict['entry2'].insert(0, 1)

        e1 = float(myDict['entry1'].get())
        e2 = float(myDict['entry2'].get())

        myDict.update(EF.assignment(kind, e1, e2, master.physics.refr_index))

        # THIS IS FOR INSERTING ELEMENTS---------------------------------------
        # Look for the value of the checkbox of the elements in the element_list
        # If it founds one, the new element is inserted just before.
        index_found = False
        for index, element in enumerate(master.physics.element_list):
            if element['checkbutton_var'].get():
                index_val = index
                index_found = True
                break
        # If a checkbox was found True, inserts the element,
        # if not, it is added to the end.
        if index_found:
            myDict['itemnumber'] = index_val+1
            myDict['itemnumber_label'] = tk.Label(self, text=str(index_val), width=2, anchor='w', bg='white')
            master.physics.element_list.insert(index_val, myDict)
            self.show_elements()
        else:
            counter = len(master.physics.element_list)
            myDict['itemnumber'] = counter
            myDict['itemnumber_label'] = tk.Label(self, text=str(myDict['itemnumber']), width=2, anchor='w', bg='white')
            master.physics.element_list.append(myDict)
            self.show_last_element(myDict)

        try:
            master.framecentral.stabilityplot.update_menus()
        except:
            pass
        try:
            master.framecentral.beamsizeplot.update_menus()
        except:
            #print('i cant delete it')
            pass
        #----------------------------------------------------------------------

    def show_last_element(self,element):
        counter = element['itemnumber']
        element['checkbutton'].grid(column=0, row=counter+2)
        element['itemnumber_label'].grid(column=1, row=counter+2, padx=2)
        element['label'].grid(column=2, row=counter+2, sticky='w')
        element['entry1'].grid(column=3, row=counter+2, padx=1)
        element['entry2'].grid(column=4, row=counter+2)
        # If it is the first element, show "calculate" button
        if len(master.physics.element_list) == 1:
            self.button_calc.bind('<Enter>', master.toolbar.func_color_enter)
            self.button_calc.bind('<Leave>', master.toolbar.func_color_leave)
            self.button_calc.grid(row=50, column=4, pady=8)
            self.button_delete.grid(row=50, column=0, columnspan=3, pady=8, sticky='w')

    def func_recalculate_itemnumbers(self):
        # Recalculate the itemnumbers
        for counter,element in enumerate(master.physics.element_list):
            element['itemnumber'] = counter
            element['itemnumber_label']['text'] = str(element['itemnumber'])

    def show_elements(self):
        # Remove all the window elements to reposition them.
        for element in master.physics.element_list:
            self.func_remove_element(element)
        # Recalculate the itemnumbers
        self.func_recalculate_itemnumbers()
        # Replace all the elements in the window
        for counter, element in enumerate(master.physics.element_list):
            element['checkbutton'].grid(column=0, row=counter+2)
            element['itemnumber_label'].grid(column=1, row=counter+2, padx=2)
            element['label'].grid(column=2, row=counter+2, sticky='w')
            element['entry1'].grid(column=3, row=counter+2, padx=1)
            element['entry2'].grid(column=4, row=counter+2)

    def func_remove_element(self,element):
        element['itemnumber_label'].grid_forget()
        element['checkbutton'].grid_forget()
        element['label'].grid_forget()
        element['entry1'].grid_forget()
        element['entry2'].grid_forget()

    def func_delete_button(self):
        # Deletes element from list and program
        deleting = False
        # Stores indexes for removal
        to_remove = []
        for counter, element in enumerate(master.physics.element_list):
            # The "[:]" is needed so the iteration works over a COPY of the list!
            # if not done so, deleting an element alter the position of the remaining elements
            # and gives trouble (deleting skips elements)
            if element['checkbutton_var'].get():
                deleting = True
                # This deletes the visual widgets
                self.func_remove_element(element)
                # This removes the element from the list
                to_remove.append(counter)
                master.warningbar.warbar_message('Deleting element ' +
                                    '  --  Numer of items = ' + str(len(master.physics.element_list)), 'lawn green')
        # Now deletes the elements
        for i in reversed(to_remove):
            master.physics.element_list.pop(i)

        if not deleting:
            master.warningbar.warbar_message('No elements marked for deleting', 'firebrick')

        if len(master.physics.element_list) == 0:
            self.button_calc.grid_forget()
            self.button_delete.grid_forget()
        try:
            master.framecentral.stabilityplot.update_menus()
        except:
            pass
        try:
            master.framecentral.beamsizeplot.update_menus()
        except:
            #print('i cant delete it')
            pass

        self.show_elements()

    def func_button_calc(self):
        for i,element in enumerate(master.physics.element_list):
            kind = element['type']
            try:
                e1 = float(element['entry1'].get())
                if e1 < 0 and kind not in ['Curved mirror','Thin lens','Curved interface']:
                    print(kind)
                    master.warningbar.warbar_message('Negative value in cavity entry box %d-1' %i, 'firebrick')
                    return 1
            except:
                master.warningbar.warbar_message('Wrong value in cavity entry box %d-1' %i, 'firebrick')
                return 1
            try:
                e2 = float(element['entry2'].get())
            except:
                master.warningbar.warbar_message('Wrong value in cavity entry box %d-2' %i, 'firebrick')
                return 1

            if kind == 'Custom element':
                pass
            else:
                element.update(EF.assignment(kind, e1, e2, master.physics.refr_index))
                if kind not in ['Block','Brewster crystal','Brewster plate']:
                    try:
                        master.physics.refr_index = element['refr_index']
                    except:
                        pass

        for proy in [0,1]:
            calc_cav = master.physics.calc_cavity(proy)
            if not calc_cav:
                break

        if calc_cav:
            master.framecentral.cavityplot.plot(master.physics.z_tan, master.physics.wz_tan,
                                   master.physics.z_sag, master.physics.wz_sag)
        
        master.framecentral.disablebuttons('a_cav')
        master.framecentral.show_cavityplot()

    def pressed_enter(self, event):
        self.func_button_calc()
#==============================================================================

#==============================================================================
#%% Central Frame
class Framecentral(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #self.pack_propagate(1)

        self.framebutton = tk.Frame(self, bd=0, bg='white')
        self.framebutton.pack(side='top', fill='x', expand=False)

        # Buttons go inside its frame
        #       Change active background by adding 
        #       "activebackground=COLOR" to button options
        self.buttons = {}
        self.buttons['a_cav'] = tk.Button(self.framebutton, text='Cavity', width=1,
                                   command=self.show_cavityplot, bg='white',
                                   bd=0, highlightthickness=0, font=('bold',11))
        self.buttons['b_stab'] = tk.Button(self.framebutton, text='Stability', width=1,
                                   command=self.show_stabilityplot, bg='white',
                                   bd=0, highlightthickness=0, font=('bold',11))
        self.buttons['c_size'] = tk.Button(self.framebutton, text='Beam size', width=1,
                                   command=self.show_beamsizeplot, bg='white',
                                   bd=0, highlightthickness=0, font=('bold',11))

        # Pack the buttons
        for element in sorted(self.buttons):
            self.buttons[element].pack(side='left', fill='both', expand='yes')
            self.buttons[element].config(state='disable', bg='grey')
            # Binds for color change (I think they aren't needed in linux)
            self.buttons[element].bind('<Enter>', self.func_color_enter)
            self.buttons[element].bind('<Leave>', self.func_color_leave)
            
        # Disable cavity button (cause it is the one active at start)
        #self.buttons['a_cav'].config(state='disable', bg='lawngreen')
        
        self.cavityplot = Cavityplot(self, relief='flat', borderwidth=0, bg='white')
        self.cavityplot.pack(side='top', fill='both', expand=True)

        self.stabilityplot = Stabilityplot(self, relief='flat', borderwidth=0, bg='white')
        self.beamsizeplot = Beamsizeplot(self, relief='flat', borderwidth=0, bg='white')
        #self.frametest = tk.Frame(self, bd=0, bg='blue')
        #self.frametest.pack(fill='both', expand=True)
        
    #==================================================================
    # These two functions change the button (normal) color.
    # However when mouse enters, the button color is "activebackground"
    # So to modify, simply change that option when defining the button.
    # Maybe on windows it works differently tho!
    def func_color_enter(self, event):
        if event.widget.cget('state') == 'normal':
            event.widget.configure(bg='aquamarine')
    def func_color_leave(self, event):
        if event.widget.cget('state') != 'disabled':
            event.widget.configure(bg='grey')
    #==================================================================
    
    # Function for color control of tab buttons
    def disablebuttons(self, currentbutton):
        for element in self.buttons:
            self.buttons[element].config(state='normal', bg='grey')
        self.buttons[currentbutton].config(state='disable', bg='lawngreen')
        
    def show_cavityplot(self):
        self.colorbutton = 'lawngreen'
        try:
            #master.cavityplot.pack_forget()
            #master.stabilityplot.pack_forget()
            self.stabilityplot.pack_forget()
            self.beamsizeplot.plotframe.canvas.pack_forget() 
        except:
            pass
        try:
            self.beamsizeplot.pack_forget()
            self.beamsizeplot.plotframe.canvas.pack_forget() 
        except:
            pass
        self.cavityplot.pack(fill='both', expand='yes')
        self.disablebuttons('a_cav')
        #master.warningbar.warbar_message('Cavity plot','lawn green')
        return True

    def show_stabilityplot(self):
        self.colorbutton = 'lawngreen'
        # 1. Tries to close cavityelements frame and to destroy previous cavitycomputation frame.
        #       If fails nothing happens (cause means they don't exist).
        #       But if an error happens then what??
        # 2. If there are less than 3 elements it doesn't open (can't have a cavity with 2 elements) and EXIT.
        # 3. warningbar message, creates cavitycomputation frame and packs it.

        try:
            self.cavityplot.pack_forget()
            self.mycanvas.pack_forget() 
        except:
            pass
        try:
            self.beamsizeplot.pack_forget()
            self.beamsizeplot.plotframe.canvas.pack_forget() 
        except:
            pass
        # Update tab buttons status
        self.disablebuttons('b_stab')
        # Pack stability frame
        self.stabilityplot.pack(side='top', fill='both', expand=True)
        if not self.stabilityplot.controlexists:
            self.stabilityplot.createcontrol()
            
    def show_beamsizeplot(self):
        # Remove Cavity plot frame
        try:
            self.cavityplot.pack_forget()
            self.mycanvas.pack_forget() 
        except:
            pass
        # Remove Stability plot frame
        try:
            self.stabilityplot.pack_forget()
            self.beamsizeplot.plotframe.canvas.pack_forget()  
        except:
            pass
        # Update tab buttons status
        self.disablebuttons('c_size')
        # Pack beam size frame
        self.beamsizeplot.pack(side='top', fill='both', expand=True)
        if not self.beamsizeplot.controlexists:
            self.beamsizeplot.createcontrol()      

#==============================================================================

#==============================================================================
#%% centralplot object that should be used by central frames with plots
class Centralplot(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #self.label = tk.Label(self, text='Plotting...')
        self.figure = plt.figure(figsize=(1,1), facecolor='white', edgecolor=None,
                                 linewidth=0.0, frameon=None)  #figsize=(5,4), dpi=100
        self.figureplot = self.figure.add_subplot(111)
        self.create_canvas()

    def create_canvas(self):
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(side='bottom', fill='x', expand=1)
        self.canvas.get_tk_widget().configure(bg='white', bd=0, highlightthickness=0)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)
        self.figuretoolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.figuretoolbar.configure(bg='white')
        self.figuretoolbar.update()

    def plot(self, x0, y0, x1, y1, xmin, xmax, xaxis, yaxis, ymin=None, ymax=None):
        self.figureplot.clear()

        self.figureplot.plot(x0, y0)
        self.figureplot.set_prop_cycle(None)
        self.figureplot.plot(x1, y1)
        self.figureplot.grid(linestyle='dashed')
        
        # xmin and xmax should be an input to the plot function
        #xmin = float(master.elementbox.stability_entry1.get())
        #xmax = float(master.elementbox.stability_entry2.get())
        plt.xlim((xmin,xmax))
        if ymin and ymax:
            plt.ylim((ymin,ymax))

        self.figureplot.set_xlabel(xaxis)
        self.figureplot.set_ylabel(yaxis)
        self.canvas.show()
#==============================================================================

#==============================================================================
#%% Plotting Beam Size frame
class Beamsizeplot(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.controlframe = tk.Frame(self, bd=0, bg='white', padx=5, pady=5)
        self.separator = ttk.Separator(self, orient='horizontal')
        self.plotframe = Centralplot(self, bd=0, bg='white')
        
        self.controlframe.pack(side='top', fill='x', expand=False)
        self.separator.pack(side='top', fill='x')
        self.plotframe.pack(side='top', fill='both', expand=True)
        
        self.controlexists = False
        self.plotframe.plot(0, 0, 0, 0, 0, 1, 'Varying parameter (mm)', 'Beam size (µm)')
    
    def createcontrol(self):
        self.controlexists = True
        # List for size elements
        self.size_list = []
        self.param_list = []
        for element in master.physics.element_list:
            self.param_list.append(element['itemnumber'])
            if not element['isvector']:
                self.size_list.append(element['itemnumber'])
                
        # Var for size in element choice
        self.elemsize_var = tk.IntVar(self)
        # Var for parameter element
        self.elemparam_var = tk.IntVar(self)
        # Var containing visible elements
        self.controls = {}
        self.controls['a_labelsize'] = tk.Label(self.controlframe, text='Beam size at element: ', bg='white', bd=0, highlightthickness=0)
        self.controls['b_optionmenu'] = tk.OptionMenu(self.controlframe, self.elemsize_var, *self.size_list)
        self.controls['b_optionmenu'].configure(bg='white', activebackground='white', highlightbackground='white')
        self.controls['b_optionmenu']['menu'].configure(fg ='darkgreen', bg='white')
        self.controls['c_labelsize'] = tk.Label(self.controlframe, text='     Varying element: ', bg='white', bd=0, highlightthickness=0)
        self.controls['d_optionmenu'] = tk.OptionMenu(self.controlframe, self.elemparam_var, *self.param_list)
        self.controls['d_optionmenu'].configure(bg='white', activebackground='white', highlightbackground='white')
        self.controls['d_optionmenu']['menu'].configure(fg ='darkgreen', bg='white')
        self.controls['e_labelsize'] = tk.Label(self.controlframe, text='    Variation from... ', bg='white', bd=0, highlightthickness=0)
        self.controls['f_entry1'] = tk.Entry(self.controlframe, width=5, justify='right')
        self.controls['g_labelsize'] = tk.Label(self.controlframe, text='     to... ', bg='white', bd=0, highlightthickness=0)
        self.controls['h_entry2'] = tk.Entry(self.controlframe, width=5, justify='right')
        self.controls['i_labelsize'] = tk.Label(self.controlframe, text='             ', bg='white', bd=0, highlightthickness=0)
        self.controls['j_button'] = tk.Button(self.controlframe, text='CALCULATE', image=master.elementbox.icon_go, command=self.pressed_go, bg='white', bd=0, highlightthickness=2)
        
        # Adjust entry values
        self.controls['f_entry1'].insert(0, 0)
        self.controls['h_entry2'].insert(0, 100)
        self.controls['f_entry1'].bind("<Return>", self.pressed_enter)
        self.controls['h_entry2'].bind("<Return>", self.pressed_enter)
        
        # Place items
        for element in self.controls:
            self.controls[element].pack(side='left')
            
    def update_menus(self):
        for element in self.controls:
            self.controls[element].destroy()
        self.createcontrol()        
        
    def pressed_enter(self, event):
        self.pressed_go()
        
    def pressed_go(self):
        master.warningbar.warbar_message('Calculating beam size variation', 'lawngreen')
        # Optionmenus variables
        item1 = self.elemsize_var.get()
        item2 = self.elemparam_var.get()
        # Entry variables
        se1 = float(self.controls['f_entry1'].get())
        se2 = float(self.controls['h_entry2'].get())
        # Call calculation
        self.calculate_variation(item1, item2, se1, se2)
        
    def calculate_variation(self, item1, item2, xstart, xend):
        # X axis vector for plotting
        self.xvec = np.linspace(xstart, xend, np.abs(xend-xstart)*100)
        # Element list for this calculation
        beamsize_list = master.physics.element_list
        elementY = beamsize_list[item1]['itemnumber']
        print(elementY)
        
        # Creation of Y axis vector
        self.yvec = []
        # Done for tangential and sagital
        for proy in [0,1]:
            y = []
            # For every value of the X axis vector
            for number in self.xvec:
                # Now modify ONLY the first entry of the chosen item, and the associated matrix:
                e1 = number
                e2 = float(beamsize_list[item2]['entry2'].get())
                kind = beamsize_list[item2]['type']
                if kind == 'Custom element':
                    pass
                else:
                    beamsize_list[item2].update(EF.assignment(kind, e1, e2, master.physics.refr_index))
                beamsize_matrix = SIMU.matrix(beamsize_list, proy)
                q0 = SIMU.q0(beamsize_matrix)
                
                # Maybe need to check stability
                
                # Complex beam parameter at desired element (elementY)
                if elementY == 0:
                    q = q0
                else:
                    q = SIMU.qx(q0, elementY, beamsize_list, proy)
                
                # Refractive index
                if 'refr_index' in beamsize_list[item1].keys():
                    refr_index = beamsize_list[item1]['refr_index']
                else:
                    refr_index = 1.0
                # Wavelength (micrometres)
                wl = master.physics.wl_mm
                # Calculate beamsize
                R, w = ABCD.r_w(q, wl, refr_index)
                y.append(w*1E3)
            # Y vectors for each projection
            self.yvec.append(y)
            
        # Plot axis labels
        xname = 'Element '+str(beamsize_list[item2]['itemnumber'])+' variation (mm)'
        yname = 'Saggital         Beam size at element '+str(elementY)+' (µm)       Tangential'
        self.plotframe.plot(self.xvec, np.array(self.yvec[0]), self.xvec, np.array(self.yvec[1])*(-1), xstart, xend, xname, yname)
        
        master.warningbar.warbar_message('Calculation finished!', 'lawngreen')
        return 0
#==============================================================================


#==============================================================================
#%% Plotting stability frame
class Stabilityplot(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #self.label = tk.Label(self, text='Plotting...')
        #self.figure = plt.figure(2, figsize=(1,1), facecolor='white', edgecolor=None,
        #                         linewidth=0.0, frameon=None)  #figsize=(5,4), dpi=100
        #self.figureplot = self.figure.add_subplot(111)
        #self.create_canvas()
        
        self.controlframe = tk.Frame(self, bd=0, bg='white', padx=5, pady=5)
        self.separator = ttk.Separator(self, orient='horizontal')
        self.plotframe = Centralplot(self, bd=0, bg='white')
        
        self.controlframe.pack(side='top', fill='x', expand=False)
        self.separator.pack(side='top', fill='x')
        self.plotframe.pack(side='top', fill='both', expand=True)
        
        self.controlexists = False
        self.plotframe.plot(0, 0, 0, 0, 0, 1, 'Varying parameter (mm)', 'Stability (norm.)', ymin=-1, ymax=1)
        
    def createcontrol(self):
        self.controlexists = True
        # List for size elements
        #self.param_list = []
        #for element in master.physics.element_list:
        #    self.param_list.append(element['itemnumber'])
        
        # Var for size in element choice
        self.elemsize_var = tk.IntVar(self)
        # Var for parameter element
        self.elemparam_var = tk.IntVar(self)
        # Var containing visible elements
        self.controls = {}
        self.controls['c_labelsize'] = tk.Label(self.controlframe, text='Varying element:   ', bg='white', bd=0, highlightthickness=0)
        self.controls['d_optionmenu'] = tk.OptionMenu(self.controlframe, self.elemparam_var, *range(len(master.physics.element_list)))
        self.controls['d_optionmenu'].configure(bg='white', activebackground='white', highlightbackground='white')
        self.controls['d_optionmenu']['menu'].configure(fg ='darkgreen', bg='white')
        self.controls['e_labelsize'] = tk.Label(self.controlframe, text='    Variation from... ', bg='white', bd=0, highlightthickness=0)
        self.controls['f_entry1'] = tk.Entry(self.controlframe, width=5, justify='right')
        self.controls['g_labelsize'] = tk.Label(self.controlframe, text='     to... ', bg='white', bd=0, highlightthickness=0)
        self.controls['h_entry2'] = tk.Entry(self.controlframe, width=5, justify='right')
        self.controls['i_labelsize'] = tk.Label(self.controlframe, text='             ', bg='white', bd=0, highlightthickness=0)
        self.controls['j_button'] = tk.Button(self.controlframe, text='CALCULATE', image=master.elementbox.icon_go, command=self.pressed_go, bg='white', bd=0, highlightthickness=2)
        
        # Adjust entry values
        self.controls['f_entry1'].insert(0, 0)
        self.controls['h_entry2'].insert(0, 100)
        self.controls['f_entry1'].bind("<Return>", self.pressed_enter)
        self.controls['h_entry2'].bind("<Return>", self.pressed_enter)
        
        # Place items
        for element in self.controls:
            self.controls[element].pack(side='left')
        
    def update_menus(self):
        for element in self.controls:
            self.controls[element].destroy()
        self.createcontrol()
        
    def pressed_enter(self, event):
        self.pressed_go()
        
    def pressed_go(self):
        # Optionmenus variables
        item1 = self.elemparam_var.get()
        # Entry variables
        se1 = float(self.controls['f_entry1'].get())
        se2 = float(self.controls['h_entry2'].get())
        # Call calculation
        master.physics.stability_plot(item1, se1, se2)

        master.warningbar.warbar_message('Calculation finished!', 'lawngreen')
        return 0
#==============================================================================


#==============================================================================
#%% Plotting cavity frame
class Cavityplot(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.figure = plt.figure(1, figsize=(1,1), facecolor='white', edgecolor=None,
                                 linewidth=0.0, frameon=None)  #figsize=(5,4), dpi=100
        self.figureplot = self.figure.add_subplot(111)
        self.create_canvas()

    def create_canvas(self):
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(side='bottom', fill='x', expand=1)
        self.canvas.get_tk_widget().configure(bg='white', bd=0, highlightthickness=0)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)
        self.figuretoolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.figuretoolbar.configure(bg='white')
        self.figuretoolbar.update()

    def plot(self, x1, y1, x2, y2):
        # Clear figure in case next won't not stable
        self.figureplot.clear()

        if (master.physics.stable and master.physics.closed and master.physics.nozeros):
            if len(x1) > 1:
                for zrow, wrow in zip(x1,y1):
                    self.figureplot.plot(zrow,wrow*1000)

                #self.figureplot.set_color_cycle(None)   # Deprecated
                self.figureplot.set_prop_cycle(None)

                for zrow, wrow in zip(x2,y2):
                    self.figureplot.plot(zrow,-wrow*1000)

            else:
                x1.append(0)
                y1.append(0)
                x2.append(0)
                y2.append(0)
                for zrow, wrow in zip(x1,y1):
                    self.figureplot.plot(zrow,wrow)

                #self.figureplot.set_color_cycle(None)   # Deprecated
                self.figureplot.set_prop_cycle(None)

                for zrow, wrow in zip(x2,y2):
                    self.figureplot.plot(zrow,-wrow)

            self.figureplot.set_xlabel('z (mm)')
            self.figureplot.set_ylabel('Saggital            w (µm)            Tangential')
            self.figureplot.grid(linestyle='dashed')
            self.canvas.show()

#==============================================================================


#==============================================================================
#%% Add optical elements frame
class Cavityelements(tk.Frame):
    # Simply buttons that call the add_element function with the element type as variable.
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.img_del1 = tk.PhotoImage(file=resource_path("Icons/e_delete.png"))
        self.img_del2 = tk.PhotoImage(file=resource_path("Icons/e_delete2.png"))
        # ELEMENTS
        self.img_flatmirror = tk.PhotoImage(file=resource_path("Icons/e_flat_mirror.png"))
        self.img_curvedmirror = tk.PhotoImage(file=resource_path("Icons/e_curved_mirror.png"))
        self.img_distance = tk.PhotoImage(file=resource_path("Icons/e_distance.png"))
        self.img_block = tk.PhotoImage(file=resource_path("Icons/e_block.png"))
        self.img_brwplate = tk.PhotoImage(file=resource_path("Icons/e_brewster_plate.png"))
        self.img_brwcrystal = tk.PhotoImage(file=resource_path("Icons/e_brewster_crystal.png"))
        self.img_thinlens = tk.PhotoImage(file=resource_path("Icons/e_thin_lens.png"))
        self.img_flatinter = tk.PhotoImage(file=resource_path("Icons/e_flat_interface.png"))
        self.img_curvedinter = tk.PhotoImage(file=resource_path("Icons/e_curved_interface.png"))
        self.img_custom = tk.PhotoImage(file=resource_path("Icons/e_custom_element.png"))

        self.label_title = tk.Label(self, text='Modify Cavity', fg='white', bg='sea green', font=('bold',13))

        #self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)

#==============================================================================
#         To add a new element you need to:
#             - Add a button here.
#             - Add the corresponding matrix in the abcd module.
#             - Add the corresponding calculation proceeding in the simulator module.
#             - Add the corresponding matrix asignment in element_features module.
#==============================================================================

        self.item_button = {}

        self.item_button['a_flat_mirror'] = tk.Button(self, text = 'Flat Mirror',
                                         image=self.img_flatmirror, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Flat mirror'),
                                         highlightthickness=0)
        self.item_button['b_curved_mirror'] = tk.Button(self, text = 'Curved Mirror',
                                         image=self.img_curvedmirror, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Curved mirror'), highlightthickness=0)
        self.item_button['c_distance'] = tk.Button(self, text = 'Distance', 
                                         image=self.img_distance, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Distance'),
                                         highlightthickness=0)
        self.item_button['d_block'] = tk.Button(self, text = 'Block', 
                                         image=self.img_block, width=120, 
                                         height=30,
                                         command=lambda: master.elementbox.add_element('Block'),
                                         highlightthickness=0)
        self.item_button['e_brewster_plate'] = tk.Button(self, text = 'Brewster plate', 
                                         image=self.img_brwplate, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Brewster plate'),
                                         highlightthickness=0)
        self.item_button['f_brewster_crystal'] = tk.Button(self, text = 'Brewster crystal', 
                                         image=self.img_brwcrystal, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Brewster crystal'),
                                         highlightthickness=0)
        self.item_button['g_thin_lens'] = tk.Button(self, text = 'Thin lens',
                                         image=self.img_thinlens, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Thin lens'),
                                         highlightthickness=0)
        self.item_button['h_custom_element'] = tk.Button(self, text = 
                                         'Custom element', 
                                         image=self.img_custom, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Custom element'),
                                         highlightthickness=0)
        self.item_button['i_flat_interface'] = tk.Button(self, text = 'Flat interface', 
                                         image=self.img_flatinter, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Flat interface'),
                                         highlightthickness=0)
        self.item_button['j_curved_interface'] = tk.Button(self, text = 'Curved interface', 
                                         image=self.img_curvedinter, width=120, 
                                         height=30, command=lambda: master.elementbox.add_element('Curved interface'),
                                         highlightthickness=0)

        self.button_delete = tk.Button(self, text = 'Delete', image=self.img_del1,
                                        command=lambda: master.elementbox.func_delete_button(),
                                        highlightthickness=0)
                                        
        # Delete button config
        self.button_delete.config(width=120, height=30, bd=0, bg='white')
        self.button_delete.bind('<Enter>', self.button_delete_enter)
        self.button_delete.bind('<Leave>', self.button_delete_leave)

        self.label_title.grid(row=0, column=0, columnspan=2, sticky='ew')

        # DELETE BUTTON MOVED TO ELEMENTBOX - for the moment just won't place it here.
        #self.button_delete.grid(row=100, column=0, columnspan=2, pady=10)

        for i,button in enumerate(sorted(self.item_button)):
            self.item_button[button].config(bd=0, bg='white')
            # THIS BINDS ARE TOTALLY NEEDED: they don't do the same as activebackground!
            self.item_button[button].bind('<Enter>', self.func_color_enter)
            self.item_button[button].bind('<Leave>', self.func_color_leave)
            self.item_button[button].grid(row=3+i-i%2, column=i%2, pady=7 )
        
        #============ ATENTION =================
        # CUSTOM ELEMENT DISABLED UNTIL IT WORKS
        self.item_button['h_custom_element'].config(state=tk.DISABLED)
        self.customtip = tt.createToolTip(self.item_button['h_custom_element'], "Work in progress")

    def button_delete_enter(self, event):
        event.widget.configure(image=self.img_del2)

    def button_delete_leave(self, event):
        event.widget.configure(image=self.img_del1)

    def func_color_enter(self, event):
        event.widget.configure(bg='aquamarine')

    def func_color_leave(self, event):
        event.widget.configure(bg='white')


#==============================================================================


#==============================================================================
#%% Add cavity computation frame
class Cavitycomputation(tk.Frame):
    # Simply buttons that call the add_element function with the element type as variable.
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Icons
        self.icon_go = tk.PhotoImage(file=resource_path("Icons/final_go.gif"))
        self.icon_add_cond = tk.PhotoImage(file=resource_path("Icons/final_add_cond.gif"))
        self.icon_del_cond = tk.PhotoImage(file=resource_path("Icons/final_del_cond.gif"))

        # Stores conditions
        self.condition_number = 0
        self.conditions_list = []
        self.conditions_available = ['w(0) size', 'Waist','Cav. distance']

        self.conditions_call = {
                                'w(0) size' : self.cond_w0_size,
                                'Waist' : self.cond_waist,
                                'Cav. distance' : self.cav_distance,
                                }

    def build_interface(self):
        self.button_computation = tk.Button(self, text='COMPUTE!', image=self.icon_go,
                                            command=self.func_computation_gui, bg='white', bd=0, highlightthickness=0, width=38, height=38)
        self.button_computation.grid(column=4, row=99, columnspan=2, sticky='e', padx=5)
        self.button_computation.bind('<Enter>', master.toolbar.func_color_enter)
        self.button_computation.bind('<Leave>', master.toolbar.func_color_leave)

        # Titles row
        self.label_title = tk.Label(self, text='Design Calculator', fg='white', bg='sea green', font=('bold',13))
        self.label_title.grid(row=0, column=0, columnspan=5, sticky='ew')
        # Stores the title labels
        self.label_subtitle = []
        self.label_subtitle.append(tk.Label(self, text='#', bg='white'))
        self.label_subtitle.append(tk.Label(self, text='Element', bg='white'))
        self.label_subtitle.append(tk.Label(self, text='Start', bg='white'))
        self.label_subtitle.append(tk.Label(self, text='Stop', bg='white'))
        self.label_subtitle.append(tk.Label(self, text='# points', bg='white'))

        for i,j in enumerate(self.label_subtitle):
            j.grid(column=i, row=3, pady=5)

        # Stores the labels and entries of the elements
        self.computation_elements = []
        z = 0
        # Element entries
        # Create the elements for computation copying the elements of the cavity.
        for number, element in enumerate(master.physics.element_list):
            myDict = {}
            i = number + 4
            myDict['type'] = element['type']
            myDict['entry2'] = element['entry2']
            myDict['label_number'] = tk.Label(self, text=i-4, bg='white', width=7)
            myDict['label_number'].grid(column=0, row=i)
            myDict['label_element'] = tk.Label(self, text=element['type'], anchor='w', width=15, bg='white')
            myDict['label_element'].grid(column=1, row=i)
            myDict['entry_rangestart'] = tk.Entry(self, width=10, justify='right')
            myDict['entry_rangestart'].grid(column=2, padx=2, row=i)
            myDict['entry_rangestop'] = tk.Entry(self, width=10, justify='right')
            myDict['entry_rangestop'].grid(column=3, padx=2, row=i)
            myDict['entry_points'] = tk.Entry(self, width=10, justify='right')
            myDict['entry_points'].grid(column=4, padx=2, row=i)

            # Initial values
            myDict['entry_rangestart'].insert(0, element['entry1'].get())
            myDict['entry_rangestop'].insert(0, element['entry1'].get())
            myDict['entry_points'].insert(0, 1)
            if myDict['type'] in ['Distance','Block','Brewster plate','Brewster crystal']:
                myDict['z'] = z
                z += 1
            else:
                myDict['z'] = 'NA'
                z += 1
            self.computation_elements.append(myDict)

            # rownumber keeps track of the number of rown in use, so things dont overlap.
            self.rownumber = i
            # Number for elements such as distances, blocks and brewster plates
            self.vectorial_elements = []
            for element in self.computation_elements:
                if not element['z'] == 'NA':
                    self.vectorial_elements.append(element['z'])

        # Things to make it pretty.
        self.label_separator = tk.Label(self, text=' ', bg='white')
        self.label_separator.grid(column=0, row=self.rownumber+1)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.separator.grid(column=0, row=self.rownumber+2, columnspan=5, sticky='ew')
        # Stores the conditions title labels
        self.conditions_title = []
        # Condition titles row
        self.conditions_title.append(tk.Label(self, text='Condition', bg='white', height=2))
        self.conditions_title.append(tk.Label(self, text='Element', bg='white'))
        self.conditions_title.append(tk.Label(self, text='Min', bg='white'))
        self.conditions_title.append(tk.Label(self, text='Max', bg='white'))
        self.conditions_title[0].grid(column=1, row=self.rownumber+3)
        self.conditions_title[1].grid(column=2, row=self.rownumber+3)
        self.conditions_title[2].grid(column=3, row=self.rownumber+3)
        self.conditions_title[3].grid(column=4, row=self.rownumber+3)

        self.rownumber += 5

        self.func_add_condition()
        # First condition musn't be deleted, and its always w0_size.
        self.conditions_list[0]['delete_button'].grid_forget()
        self.conditions_list[0]['condition_var'].set('w(0) size')
        self.check_condition(0, self.conditions_list[0])

#==============================================================================
#         self.conditions_list[0]['condition_var'].set('w(0) size')
#         self.conditions_list[0]['element_menu'].config(state='disable')
#==============================================================================

        # Add condition Button
        self.button_add_condition = tk.Button(self, text='+', image=self.icon_add_cond,
                                              bd=0, width=20, height=20, command=self.func_add_condition,
                                              highlightthickness=0, bg='white')
        self.button_add_condition.grid(column=0, row = 98, pady=5)
        self.button_add_condition.bind('<Enter>', master.toolbar.func_color_enter)
        self.button_add_condition.bind('<Leave>', master.toolbar.func_color_leave)


    def pressed_enter(self, event):
        self.func_computation_gui()

    def func_add_condition(self):
        myDict = {}
        myDict['number'] = self.condition_number
        myDict['delete_button'] = self.button_del_condition = tk.Button(self, text='-',
                                        image=self.icon_del_cond, bd=0, width=20, height=21, bg='white', command=lambda:self.func_del_condition(myDict), highlightthickness=0)
        myDict['delete_button'].bind('<Enter>', master.toolbar.func_color_enter)
        myDict['delete_button'].bind('<Leave>', master.toolbar.func_color_leave)

        myDict['element_var'] = tk.IntVar(self)
        myDict['element_menu'] = tk.OptionMenu(self, myDict['element_var'], *self.vectorial_elements)
        myDict['entry1'] = tk.Entry(self, width=10, justify='right')
        myDict['entry2'] = tk.Entry(self, width=10, justify='right')
        # Return key binding for entries
        myDict['entry1'].bind("<Return>", self.pressed_enter)
        myDict['entry2'].bind("<Return>", self.pressed_enter)

        myDict['condition_var'] = tk.StringVar(self)
        myDict['condition_menu'] = tk.OptionMenu(self, myDict['condition_var'], *self.conditions_available,
                                                    command=lambda var:self.check_condition(var,myDict))

        # Posiotioning in the GRID
        myDict['delete_button'].grid(column=0, row = self.rownumber)
        myDict['condition_menu'].grid(column=1, row=self.rownumber, sticky="ew")
        myDict['condition_menu'].configure(bg='white', activebackground='white', highlightbackground='white', width=12)
        myDict['condition_menu']['menu'].configure(fg ='darkgreen', bg='white')
        myDict['element_menu'].grid(column=2, row=self.rownumber, sticky="ew")
        myDict['element_menu'].configure(bg='white', activebackground='white', highlightbackground='white')
        myDict['element_menu']['menu'].configure(fg ='darkgreen', bg='white')
        myDict['entry1'].grid(column=3, row=self.rownumber)
        myDict['entry2'].grid(column=4, row=self.rownumber)

        myDict['condition_var'].set('Waist')
        myDict['element_var'].set(self.vectorial_elements[0])

        self.check_condition(0, myDict) # 0 means nothing, the function needs 2 inputs as stated below.
        self.conditions_list.append(myDict)
        self.rownumber += 1
        self.condition_number += 1

        master.warningbar.warbar_message('Condition added', 'lawn green')

    def func_del_condition(self, myDict):
        myDict['delete_button'].destroy()
        myDict['condition_menu'].destroy()
        myDict['element_menu'].destroy()
        myDict['entry1'].destroy()
        myDict['entry2'].destroy()
        self.conditions_list.remove(myDict)
        master.warningbar.warbar_message('Condition deleted', 'lawn green')

    # ------------ Disable element menu for w0_waist condition
    def check_condition(self, notuseful, var):
        # I need "notuseful" because the tkinter optionmenu automatically passes a variable
        # to the command called, but it is not the variable that i need, so with a lambda
        # function i pass a second variable, and receive and ignore the first variable.
        var['entry1'].bind("<FocusIn>", self.delete_units)
        var['entry2'].bind("<FocusIn>", self.delete_units)

        if var['condition_var'].get() == 'w(0) size':
            var['element_menu'].config(state='disable')
            # Shows apropiate units
            self.show_micro(var)

        elif var['condition_var'].get() == 'Waist':
            var['element_menu'].config(state='normal')
            var['element_menu']
            # Shows apropiate units
            self.show_micro(var)

        elif var['condition_var'].get() == 'Cav. distance':
            var['element_menu'].config(state='disable')
            # Shows apropiate units
            self.show_mili(var)

        else:
            var['element_menu'].config(state='normal')

    def show_mili(self, element):
        # Shows apropiate units
        element['entry1'].delete(0, tk.END)
        element['entry1'].insert(0, '(mm)')
        element['entry2'].delete(0, tk.END)
        element['entry2'].insert(0, '(mm)')
    def show_micro(self, element):
        # Shows apropiate units
        element['entry1'].delete(0, tk.END)
        element['entry1'].insert(0, '(µm)')
        element['entry2'].delete(0, tk.END)
        element['entry2'].insert(0, '(µm)')

    # ------------------- CONDITIONS ---------------------
    def cond_w0_size(self, condition):
        q0 = SIMU.q0(SIMU.matrix(self.computation_elements, 0))
        r0, w0 = ABCD.r_w(q0, master.physics.wl_mm, 1)

        if master.toolbar.chivato:
            print('In w0 size condition')
            print('I(1/q)=',np.imag(1/q0))
            print('R =',r0,' --- w =',w0)

        if (w0 > float(condition['entry1'].get())*1E-3 and  w0 < float(condition['entry2'].get())*1E-3):
            if master.toolbar.chivato:
                print('And solution found:',w0)
            return w0
        else:
            if master.toolbar.chivato:
                print('And no solution found')
            return False

    def cond_waist(self, condition):
        q0 = SIMU.q0(SIMU.matrix(self.computation_elements, 0))
        z, wz = SIMU.propagation(self.computation_elements, q0, master.physics.wl_mm, 0,master.toolbar.chivato)
        array_number = self.vectorial_elements.index(condition['element_var'].get())

        if master.toolbar.chivato:
            print('In waist condition')
            print('I(1/q)=',np.imag(1/q0))

        # Check that min is not an edge
        if (
            min(wz[array_number]) < wz[array_number][0]
            and
            min(wz[array_number]) < wz[array_number][-1]
            ):

            if (
                min(wz[array_number]) > float(condition['entry1'].get())*1E-3
                and
                min(wz[array_number]) < float(condition['entry2'].get())*1E-3
                ):
                return min(wz[array_number])
            else:
                return False
        else:
            return False
        pass

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


    def func_computation_gui(self):
        if master.toolbar.chivato:
            print('Started computation ----------')
        # Eval user entries
        if not self.cond_error('entry_eval'):
            return False

        # Make button take focus (so condition entries dont)
        self.button_computation.focus_set()

        self.solutions_found = False
        self.combination_final = []
        self.results_final = []
        self.stable_final = []

        master.toolbar.eval_entry_wl("<Return>")
        master.warningbar.warbar_message('Unbelievable complex calculations in progress...', 'lawn green')

        # Create results window, disabling main window
        self.resultswindow = ResultsWindow(master)
        self.resultswindow.grab_set()
        
        root.update_idletasks()
        
        for element in self.computation_elements:
            myDict = {}
            a = float(element['entry_rangestart'].get())
            b = float(element['entry_rangestop'].get())
            c = float(element['entry_points'].get())
            myDict['vector'] = np.linspace(a, b, c)
            element.update(myDict)

        master.physics.refr_index = 1
        for combination in itertools.product(*[i['vector'] for i in self.computation_elements]):
            for element, entry in zip(self.computation_elements,combination):
                # Create matrix for each element
                kind = element['type']
                e1 = float(entry)
                e2 = float(element['entry2'].get())
                if kind == 'Custom element':
                    pass
                else:
                    element.update(EF.assignment(kind, e1, e2, master.physics.refr_index))
                    try:
                        master.physics.refr_index = element['refr_index']
                    except:
                        pass

            # Calculate total cavity matrix
            self.cav_matrix_tan = SIMU.matrix(self.computation_elements, 0)
            self.cav_matrix_sag = SIMU.matrix(self.computation_elements, 1)
            stable1 = SIMU.stabilitycalc(self.cav_matrix_tan)
            stable2 = SIMU.stabilitycalc(self.cav_matrix_sag)
            
            if master.toolbar.chivato:
                print('Physics matrix, physics elements')
                print(master.physics.calc_matrix(master.physics.element_list, 0))
                print('Physics matrix, comp. elements')
                print(master.physics.calc_matrix(self.computation_elements, 0))
                print('Physics matrix, comp. elements')
                print(self.cav_matrix_tan)
                print(self.cav_matrix_sag)

                print('Checking stability')
                print(stable1, stable2)

            # Element to element comparison
            if False:
                print('Im gonna compare every element')
                #print(master.physics.element_list)
                #print(self.computation_elements)
                for i, j in zip(master.physics.element_list, self.computation_elements):
                    #print(i.keys())
                    #print(j.keys())
                    print(i['type'], j['type'])
                    #print(float(i['entry1'].get()), float(j['entry1'].get()) )
                    print(i['entry2'].get(), j['entry2'].get())
                    
            if stable1 and stable2:
                if master.toolbar.chivato:
                    print('It is stable')
                results = []
                for condition in self.conditions_list:
                    answer = self.conditions_call[condition['condition_var'].get()](condition)
                    if master.toolbar.chivato:
                        print('answer',answer)
                    if not answer:
                        results = []
                        break
                    else:
                        results.append(round(answer*1E3,4))
                if results:
                    self.combination_final.append(combination)
                    self.results_final.append(results)
                    self.stable_final.append([stable1,stable2])
                    #self.resultswindow.inner_frame.create_results()
                    self.solutions_found = True
            # Since this repeats for each different configuration, if it isnt stable nothing is done, y listo!
            
        if self.solutions_found:
            master.warningbar.warbar_message('Finished... Solutions found', 'lawn green')

            # Limited by grid positioning
            if len(self.combination_final) > 1000:
                self.combination_final = self.combination_final[0:1000]
                self.results_final = self.results_final[0:1000]
                master.warningbar.warbar_message('Too many solutions. Capped at 1000', 'goldenrod')

            self.resultswindow.inner_frame.create_results()
            #self.resultswindow2.inner_frame.create_results()
            #master.framebottom.show_computationtable()
            # Release focus
            self.resultswindow.grab_release()
        else:
            self.resultswindow.results_window_close()
            master.warningbar.warbar_message('Finished... Solutions not found', 'firebrick')
        return True

    def delete_units(self, event):
        event.widget.delete(0, tk.END)

    # Error handling
    def cond_error(self, case):
        def entry_eval():
            # Evaluate user entries
            for condition in self.conditions_list:
                try:
                    float(condition['entry1'].get())
                    float(condition['entry2'].get())
                    return 1
                except ValueError:
                    return 2

        cond_dict = {
                    'entry_eval' : entry_eval
                    }

        # Evaluate codes
        if cond_dict[case]() == 1:
            return True

        elif cond_dict[case]() == 2:
            master.warningbar.warbar_message('Error in condition entry', 'firebrick')
            return False

#==============================================================================
#%% Results window (parent - scroll container)
class ResultsWindow(scrollf.VerticalScrolledFrame):
    def __init__(self, parent, *args, **kwargs):
        scrollf.VerticalScrolledFrame.__init__(self, parent, *args, **kwargs)
        self.title("Results window")
        self.config(background='white')
        self.inner_frame = ResultsWindow2(self.interior)
        self.inner_frame.grid(column=0, row=0)

        # Protocol for window close
        self.protocol("WM_DELETE_WINDOW", self.results_window_close)

    def results_window_close(self):
        self.destroy()
        master.warningbar.warbar_message('No messages','grey')

#==============================================================================

#==============================================================================
#%% Results window (inner frame - scrollable)
class ResultsWindow2(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.config(background='white')

        self.number_items = len(master.frameright.cavitycomputation.computation_elements)
        self.number_conditions = len(master.frameright.cavitycomputation.conditions_list)
        self.create_titles()
        self.combination = []
        self.results = []
        self.row_counter = 4

    def create_titles(self):
        # Table title: Items and Conditions
        self.item_title = tk.Label(self, text='Items', fg='white', bg='sea green', font='bold')
        self.stable_title = tk.Label(self, text='Stability', fg='white', bg='sea green', font='bold')
        self.condition_title = tk.Label(self, text='Conditions', fg='white', bg='sea green', font='bold')

        self.item_title.grid(column=0, row=0, columnspan=self.number_items, sticky='ew')
        self.stable_title.grid(column=self.number_items+1, row=0, columnspan=2, sticky='ew')
        self.condition_title.grid(column=self.number_items+4, row=0, columnspan=self.number_conditions, sticky='ew')

        # Table item subtitles: item names
        self.item_label = []
        for i in master.frameright.cavitycomputation.computation_elements:
            label = tk.Label(self, text=i['type'], bg='white', bd=0, relief='solid', padx=7)
            self.item_label.append(label)
        # Stability column
        label_sub_tan = tk.Label(self, text='Tangential', bg='white', bd=0, relief='solid', padx=7)
        label_sub_sag = tk.Label(self, text='Sagital', bg='white', bd=0, relief='solid', padx=7)
        label_sub_tan.grid(column=self.number_items+1, row=1)
        label_sub_sag.grid(column=self.number_items+2, row=1)

        # Positioning
        for j,i in enumerate(self.item_label):
            i.grid(column=j, row=1)

        # Table condition subtitles: condition names
        self.condition_label = []
        for i in master.frameright.cavitycomputation.conditions_list:
            #label = tk.Label(self, text='Condition %s' % i['number'], bg='white', bd=0, relief='solid', padx=7)
            label = tk.Label(self, text=i['condition_var'].get(), bg='white', bd=0, relief='solid', padx=7)
            self.condition_label.append(label)
        # Positioning
        for j,i in enumerate(self.condition_label):
            i.grid(column=self.number_items+4+j, row=1)

        # Vertical separator between items and stability
        self.separator1 = ttk.Separator(self, orient='vertical')
        self.separator1.grid(column=self.number_items, row=0, rowspan=2, sticky="ns")
        # Vertical separator between stability and conditions
        self.separator2 = ttk.Separator(self, orient='vertical')
        self.separator2.grid(column=self.number_items+3, row=0, rowspan=2, sticky="ns")
        # Horizontal separator after subtitles
        self.separator3 = ttk.Separator(self, orient='horizontal')
        self.separator3.grid(column=0, row=3, columnspan=100, sticky="ew")


    def create_results(self):
        x = master.frameright.cavitycomputation.combination_final
        y = master.frameright.cavitycomputation.results_final
        for n, (k,l) in enumerate(zip(x,y)):
            self.combination_label = []
            for i in k:
                label = tk.Label(self, text='%.1f' % i, bg='white')
                self.combination_label.append(label)

            # Stability column
            label_tan = tk.Label(self, text='%.2f' %master.frameright.cavitycomputation.stable_final[n][0] , bg='light cyan')
            label_sag = tk.Label(self, text='%.2f' %master.frameright.cavitycomputation.stable_final[n][1] , bg='light cyan')

            # Positioning
            for j,i in enumerate(self.combination_label):
                i.grid(column=j, row=self.row_counter)

            label_tan.grid(column=self.number_items+1, row=self.row_counter, sticky='ew')
            label_sag.grid(column=self.number_items+2, row=self.row_counter, sticky='ew')

            self.results_label = []
            for i in l:
                label = tk.Label(self, text='%.2f' % i, bg='palegreen')
                # Binds for mouse enter / leave
                label.bind('<Enter>', self.func_mouse_enter)
                label.bind('<Leave>', self.func_mouse_leave)
                # Bind for clicking
                label.bind("<Button-1>", self.label_clicked)
                self.results_label.append(label)
            # Positioning
            for j,i in enumerate(self.results_label):
                i.grid(column=self.number_items+4+j, row=self.row_counter, sticky='ew')

            self.row_counter = self.row_counter + 1
        return True

    def func_mouse_enter(self, event):
        event.widget.configure(highlightcolor='black', relief='ridge')

    def func_mouse_leave(self, event):
        event.widget.configure(highlightcolor='white', relief='flat')

    def label_clicked(self, event):
        # Get the row number, and substracts 4 due to title rows.
        number = event.widget.grid_info()["row"]-4
        self.draw_results(number)

    def draw_results(self, number):
        x = master.frameright.cavitycomputation.combination_final[number]
        for i, (element,combination) in enumerate(zip(master.physics.element_list,x)):
            # Delete current value of entry 1
            master.physics.element_list[i]['entry1'].delete(0, tk.END)
            # Writes new (computed) value
            master.physics.element_list[i]['entry1'].insert(0, round(combination*100)/100)
            master.elementbox.func_button_calc()
            master.warningbar.warbar_message('Solution ported to cavity','lawngreen')

#==============================================================================
#%% Frame on the right
class Frameright(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.pack_propagate(0)

        self.cavityelements = Cavityelements(self, bd=0, bg='white')
        self.cavityelements.columnconfigure((0,1), weight=1)

        self.show_cavityelements()

    def show_cavityelements(self):
        try:
            #master.cavityplot.pack_forget()
            #master.stabilityplot.pack_forget()
            self.cavitycomputation.destroy()
        except:
            pass
        self.cavityelements.pack(ipadx=2, ipady=2, fill='x')
        return True

    def show_cavitycomputation(self):
        # 1. Tries to close cavityelements frame and to destroy previous cavitycomputation frame.
        #       If fails nothing happens (cause means they don't exist).
        #       But if an error happens then what??
        # 2. If there are less than 3 elements it doesn't open (can't have a cavity with 2 elements) and EXIT.
        # 3. warningbar message, creates cavitycomputation frame and packs it.

        try:
            self.cavityelements.pack_forget()
            self.cavitycomputation.destroy()
        except:
            pass

        if len(master.physics.element_list) < 3:
            master.warningbar.warbar_message('Error: Not enough elements','firebrick')
            return False
        else:
            master.warningbar.warbar_message('Happy computation','lawn green')
            self.cavitycomputation = Cavitycomputation(self, bd=0, bg='white')
            self.cavitycomputation.pack(fill='x')
            self.cavitycomputation.columnconfigure((0,1,2,3,4), weight=1)
            return True

#==============================================================================

#==============================================================================
#%% Bottom frame
#       For stability plot, computations results...
class Framebottom(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.stabilityplot = Stabilityplot(self, relief='flat', borderwidth=0)
        self.show_stabilityplot()

#==============================================================================
#     def create_computationtable(self):
#         self.computationtable = ResultsWindow3(self, relief='flat', borderwidth=0)
#         return self.computationtable
#==============================================================================

    def show_stabilityplot(self):
#==============================================================================
#         try:
#             self.computationtable.destroy()
#         except:
#             pass
#==============================================================================
        #self.frameright.cavityelements.pack_forget()
        self.stabilityplot.pack(side='top', fill='both', pady=0)

#==============================================================================
#     def show_computationtable(self):
#         try:
#             self.stabilityplot.destroy()
#         except:
#             pass
#         self.computationtable.pack(side='top', fill='both', pady=0)
#==============================================================================

class ResizingCanvas(tk.Canvas):
    def __init__(self,parent,**kwargs):
        tk.Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)

#==============================================================================
#%% Main frame
class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.newcavplot = True
        self.newstabplot = True

        self.parent = parent
        self.toolbar = Toolbar(self, bg='white', bd=0, pady=2)
        self.warningbar = Warningbar(self, relief='solid', bd=0)
        self.elementbox = Elementbox(self, relief='solid', borderwidth=3, width=300, bg='white')
        self.frameright = Frameright(self, relief='solid', borderwidth=3, width=360, height=300, bg='white')

        self.physics = Physics()
        self.framecentral = Framecentral(self, relief='solid', borderwidth=3, bg='white')

        self.toolbar.pack(side="top", fill="x", padx=3, pady=3, ipadx=5, ipady=2)
        self.warningbar.pack(side="bottom", fill="x")
        self.elementbox.pack(side='left', fill='y', ipady=3, padx=3, pady=3)
        self.frameright.pack(side='right', fill='y', ipady=3, padx=3, pady=3)
        self.framecentral.pack(side='top', fill='both', anchor='s', expand=True,
                               pady=3, ipady=0, ipadx=0)
#==============================================================================


#%%
if __name__ == "__main__":

    def killing_root():
        root.quit()

    root = tk.Tk()
    # Start maximized
    try:
        # 'zoomed' is an error in linux
        root.wm_state('zoomed')
    except:
        root.attributes('-zoomed', True)
    # Window title
    root.wm_title("SimCav 4.7")
    try:
        # This is for windows
        root.wm_iconbitmap(resource_path("Icons/logo-tg3.ico"))#root.wm_iconbitmap(resource_path("Icons/Icon2.ico"))
    except:
        # This is for linux
        myicon = tk.PhotoImage(file=resource_path("Icons/logo-tg3.png"))
        root.tk.call('wm', 'iconphoto', root._w, myicon)
    root.minsize(1100,400)
    # Kill process when click on window close button
    root.protocol("WM_DELETE_WINDOW", killing_root)
    # Create main frame
    master = MainApplication(root, bg='white')
    master.pack(side="top", fill="both", expand=True)

    root.mainloop()
