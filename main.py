import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

# Matplotlib stuff
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse

# Other modules
import os
import math
import numpy as np
import itertools
from collections import OrderedDict
import pickle           # To save and load files
import hashlib, json    # For MD5 computation
import atexit           # To run before exit

import load_icons as LI
import simcav_physics as SP
import simcav_designer as SD
import simcav_conditions as SC
import simcav_statusBar as sBar
import simcav_updates as updates
import matrixWidget

import time


# File path function for deployment in single file with PuInstaller
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)


# ==============================================================================
# Creating the GUI
qtCreatorFile = resource_path("gui.ui")  # Enter GUI file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


# ==============================================================================
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setStyleSheet(open(resource_path('style_main.css')).read())
        self.version = '5.0.3'

        self.setupUi(self)
        self.initUI()

        # Draw canvas for all the plots
        self.drawCanvas()

        self.designer_list_setup()
        self.designer_conditions_setup()
        self.element_list_setup()
        self.cavity_scheme_setup()

        self.cavity = SP.cavity()

        self.elementFocus = []    # This will be a list, even if only one element
        self.conditionFocus = []    # This will be a list, even if only one element
        self.cavityMD5 = hashlib.md5('0'.encode('utf-8'))

        # BUTTON FUNCTIONS =====================================================
        # Cavity buttons
        self.button_moveUp.clicked.connect(self.handle_button_moveUp)
        self.button_moveDown.clicked.connect(self.handle_button_moveDown)
        self.button_delete.clicked.connect(self.handle_button_delete)
        self.button_calcCavity.clicked.connect(self.handle_button_calcCavity)

        # Stability buttons
        self.button_calcStability.clicked.connect(self.handle_button_calcStability)
        # Beam Size Buttons
        self.button_calcBeamsize.clicked.connect(self.handle_button_calcBeamsize)
        # Cross Section Widgets
        self.button_crossSectionUpdate.clicked.connect(self.handle_button_crossSectionUpdate)
        # When user tweaks using the slider
        self.crossSectionSlider.valueChanged[int].connect(self.modified_crossSectionSlider)
        # When user modify via the textBox
        # self.crossSectionBox.editingFinished.connect(self.update_crossSectionSlider)

        # Designer buttons
        self.button_conditionAdd.clicked.connect(self.handle_button_conditionAdd)
        self.button_conditionDel.clicked.connect(self.handle_button_conditionDel)
        self.button_calcSolutions.clicked.connect(self.handle_button_calcSolutions)

        # "Add element" functions
        self.button_flatMirror.clicked.connect(self.handle_button_addElement)
        self.button_curvedMirror.clicked.connect(self.handle_button_addElement)
        self.button_distance.clicked.connect(self.handle_button_addElement)
        self.button_block.clicked.connect(self.handle_button_addElement)
        self.button_brewsterPlate.clicked.connect(self.handle_button_addElement)
        self.button_brewsterCrystal.clicked.connect(self.handle_button_addElement)
        self.button_flatInterface.clicked.connect(self.handle_button_addElement)
        self.button_curvedInterface.clicked.connect(self.handle_button_addElement)
        self.button_thinLens.clicked.connect(self.handle_button_addElement)
        self.button_customElement.clicked.connect(self.handle_button_addElement)

        # Tab controls
        self.tabWidget_controls.currentChanged.connect(self.handle_controlTab_changed)

        # Toolbar Actions
        self.toolBar.actionTriggered.connect(self.handle_toolbar_actions)
        self.wlBox.editingFinished.connect(self.setWavelength)
        self.wlBox.returnPressed.connect(self.setWavelength)

        # Menu
        self.menuFile.triggered[QtWidgets.QAction].connect(self.handle_fileMenu_actions) # Needed if action isn't as well in toolbar
        self.menuView.triggered[QtWidgets.QAction].connect(self.handle_viewMenu_actions)

        # Counting elements
        self.numberOfElements = 0
        dummy, self.savedMD5 = self.constructSavingList()

        try:
            self.checkupdates()
            # SHOULD DO PROPER DEBUGGING HERE
        except:
            self.bottomBar.showMessage('Error fetching updates.')
        self.wlLabel = self.bottomBar.init_statusBar(self.cavity.wl_mm)

    # End INIT
    #===========================================================================



    ############################################################################
    # Other GUI stuff
    def initUI(self):
        # Add wavelength box in toolbar
        wlLabel = QtWidgets.QLabel(text="λ = ")
        wlLabel.setMinimumWidth(35)
        wlLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.wlBox = QtWidgets.QLineEdit(text="1000", placeholderText="nm")
        self.wlBox.setMaximumWidth(90)
        self.wlBox.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        wlUnitsLabel = QtWidgets.QLabel(text=" nm")
        self.toolBar.addWidget(wlLabel)
        self.toolBar.addWidget(self.wlBox)
        self.toolBar.addWidget(wlUnitsLabel)
        self.bottomBar = sBar.StatusBar(self.statusBar)

        # Add property to "calculate!" buttons to CSS them
        self.button_calcCavity.setProperty('calculate', True)
        # THIS ISNT WORKING, COULD DELETE

        # Int validator
        self.validatorInt = QtGui.QIntValidator()
        self.validatorFloatPositive = QtGui.QDoubleValidator(bottom=0)
        # Float validator
        self.validatorFloat = QtGui.QDoubleValidator()
        self.validatorFloat.setNotation(QtGui.QDoubleValidator.StandardNotation)
        # Set validator in wavelength, stability, beam size entries
        self.wlBox.setValidator(self.validatorFloatPositive)
        self.stability_xstart.setValidator(self.validatorFloat)
        self.stability_xend.setValidator(self.validatorFloat)
        self.beamsize_xstart.setValidator(self.validatorFloat)
        self.beamsize_xend.setValidator(self.validatorFloat)

    def drawCanvas(self):
        # Cavity tab
        self.cavityPlot = PlotCanvas(xlabel='z (mm)', ylabel='w (µm)')
        self.cavityPlot_toolbar = NavigationToolbar(self.cavityPlot, self)
        self.tab_cavity.verticalLayout = QtWidgets.QVBoxLayout()
        self.tab_cavity.verticalLayout.addWidget(self.cavityPlot)
        self.tab_cavity.verticalLayout.addWidget(self.cavityPlot_toolbar)
        self.tab_cavity.setLayout(self.tab_cavity.verticalLayout)

        # Stability tab
        self.stabilityPlot = PlotCanvas(xlabel='Variation of element X (mm)', ylabel='Stability (norm.)')
        self.stabilityPlot_toolbar = NavigationToolbar(self.stabilityPlot, self)
        self.tab_stability.layout().addWidget(self.stabilityPlot)
        self.tab_stability.layout().addWidget(self.stabilityPlot_toolbar)

        # Beam Size tab
        self.beamsizePlot = PlotCanvas(xlabel='Variation of element X (mm)', ylabel='Beam size at element X (µm)')
        self.beamsizePlot_toolbar = NavigationToolbar(self.beamsizePlot, self)
        self.tab_beamSize.layout().addWidget(self.beamsizePlot)
        self.tab_beamSize.layout().addWidget(self.beamsizePlot_toolbar)

        # crossSection tab
        self.crossSectionPlot = PlotCanvas(xlabel='Tangential (µm)', ylabel='Sagittal (µm)')
        self.crossSectionPlot_toolbar = NavigationToolbar(self.crossSectionPlot, self)
        self.tab_crossSection.layout().addWidget(self.crossSectionPlot)
        self.tab_crossSection.layout().addWidget(self.crossSectionPlot_toolbar)

        # Default tab
        self.tabWidget_plots.setCurrentIndex(0)
        self.tabWidget_controls.setCurrentIndex(0)
        self.tabWidget_controls.setTabEnabled(1, False)

    def populateComboBoxes(self):
        self.stability_comboBox.clear()
        self.beamsize_comboBox_watch.clear()
        self.beamsize_comboBox_var.clear()
        eList, vList, not_vList = self.cavity.optionMenuLists()
        #elementList = self.cavity.elementList
        self.stability_comboBox.addItems(eList)
        self.beamsize_comboBox_watch.addItems(not_vList)
        self.beamsize_comboBox_var.addItems(eList)

    def cavity_scheme_setup(self):
        # Layout for scroll area.
        # Widgets (cavity elements) have to be added to this layout
        self.cavityIconsLayout = QtWidgets.QHBoxLayout(self.scroll_cavityIconsArea)
        self.cavityIconsLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.cavityIconsLayout.setContentsMargins(0,0,0,0)
        self.cavityIconsLayout.setSpacing(0)

    def designer_list_setup(self):
        # Layout for scroll area.
        # designer widgets have to be added to this layout
        self.designerListLayout = QtWidgets.QVBoxLayout(self.scrollArea_computation_layout)
        self.designerListLayout.setAlignment(QtCore.Qt.AlignTop)
        self.designerListLayout.setContentsMargins(0,0,0,0)
        self.designerListLayout.setSpacing(0)

    def designer_conditions_setup(self):
        # Layout for scroll area.
        # condition widgets have to be added to this layout
        self.designerConditionsLayout = QtWidgets.QVBoxLayout(self.scrollArea_conditions_layout)
        self.designerConditionsLayout.setAlignment(QtCore.Qt.AlignTop)
        self.designerConditionsLayout.setContentsMargins(0,0,0,0)
        self.designerConditionsLayout.setSpacing(0)
        # Printing solutions
        self.designerSolutionsLayout = QtWidgets.QVBoxLayout(self.scrollArea_solutionsContent)
        self.designerSolutionsLayout.setContentsMargins(0,0,0,0)
        self.designerSolutionsLayout.setSpacing(0)

    def element_list_setup(self):
        # Layout for scroll area.
        # Widgets (cavity elements) have to be added to this layout
        self.elementListLayout = QtWidgets.QVBoxLayout(self.element_list_scroll)
        self.elementListLayout.setAlignment(QtCore.Qt.AlignTop)
        self.elementListLayout.setContentsMargins(0,0,0,0)
        self.elementListLayout.setSpacing(0)

    def updateElementList(self):
        for element in self.cavity.elementList:
            element['Widget'].setParent(None)
            element['Icon'].setParent(None)
        for element in self.cavity.elementList:
            self.elementListLayout.addWidget(element['Widget'])
            self.cavityIconsLayout.addWidget(element['Icon'])
        self.toggleDesigner()

    def handle_controlTab_changed(self, tab):
        if tab == 0:
            # Going back to modify cavity, clear Designer
            self.tab_designer_destruction()
        elif tab == 1:
            # Going into designer, create items
            if not self.tab_designer_creation():
                self.tabWidget_controls.setCurrentIndex(0)


    # End Other GUI stuff
    #===========================================================================

    ############################################################################
    # Menu actions
    def handle_fileMenu_actions(self, q):
        if q.text() == "Save as...":
            self.fileSave(saveAs=True)
        elif q.text() == "Quit":
            #self.closeEvent(self.QCloseEvent())
            print('quit')
            self.actionQuit.triggered.connect(self.close)
        else:
            pass
    def handle_viewMenu_actions(self, q):
        # Hide/Show "Add Element" widget
        if q.text() == "Toolbar":
            self.toolBar.setVisible(q.isChecked())
        elif q.text() == "ABCD matrices":
            self.showABCD()
        elif q.text() == "Calculate solutions Box":
            #self.calculateSolutions.setVisible(q.isChecked())
            pass
        else:
            print(q.text())

    # Toolbar actions
    def handle_toolbar_actions(self, q):
        if q.text() == "New":
            self.fileNew()

        elif q.text() == "Open":
            openFile, filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Load cavity', filter=("SimCav files (*.sc);;All files (*.*)"))

            if not openFile:
                print('Nothing selected')
                return False

            self.fileOpen(openFile)
            self.saveFile = openFile

        elif q.text() == "Save":
            self.fileSave()

        elif q.text() == "Edit":
            pass
        elif q.text() == "Calculator":
            pass
        elif q.text() == "Update":
            goOn = QMessageBox.question(self, 'Update available', "Would you like to update now? \n(This will close SimCav)", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if goOn == QMessageBox.Yes:
                import subprocess
                subprocess.Popen([sys.executable, 'updater.py'])
                sys.exit()
            if goOn == QMessageBox.No:
                self.bottomBar.showMessage('Update cancelled', 10E3)
        elif q.text() == "Quit":
            pass
        else:
            print("Button not recognized")
            print(q.text())

    def toggleDesigner(self):
        if self.cavity.minimumElements() and self.cavity.closedCavity():
            self.tabWidget_controls.setTabEnabled(1, True)
        else:
            self.tabWidget_controls.setTabEnabled(1, False)

    ############################################################################
    # ToolBar functions
    def fileNew(self):
        # Delete cavity elements
        for element in reversed(self.cavity.elementList):
            self.elementFocus = [element['ID']]
            self.handle_button_delete()
        # Delete save file not to overwrite by mistake
        try:
            del self.saveFile
            del self.savedMD5
        except:
            pass

    def fileOpen(self, openFile):
        # Open file
        with open(openFile, 'rb') as file:
            # Load into a list
            loadedList = pickle.load(file)
        # Clear program
        self.fileNew()
        hashingData = json.dumps(loadedList, sort_keys=True).encode('utf-8')
        self.savedMD5 = hashlib.md5(hashingData)
        # adds the saved elements
        for element in loadedList:
            # Create elements
            window.handle_button_addElement(element['type'], element['entry1_val'], element['entry2_val'])

        # Set wavelength
        wl_loaded = round(loadedList[0]['wavelength']*1E8)/100
        self.wlBox.setText(str(wl_loaded))
        self.setWavelength()

        # Draw cavity
        self.handle_button_calcCavity()

        self.bottomBar.showMessage('Load successful', 5E3)

    def fileSave(self, saveAs=False, quit=False, theList=None, theHash=None):
        try:
            # If already saved, use that file
            self.saveFile
        except:
            # If not saved before, behave as "Save as..."
            saveAs = True

        if saveAs:
            saveFile, filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save cavity', filter=("SimCav files (*.sc)"))
            # In case no file was chosen (eg. clicked on cancel)
            if not saveFile:
                print('Nothing selected')
                return False
            # Add extension if needed
            if saveFile[-3:] != ".sc":
                saveFile = saveFile + ".sc"
            self.saveFile = saveFile

        print('Saving in ' + self.saveFile)
        if not quit:
            # Creating data to save
            savingList, savingListMD5 = self.constructSavingList()

            # If hash match, then dont save
            if self.checkHash(savingListMD5) and not saveAs:
                self.bottomBar.showMessage('No changes to save.', 5E3)
                return True
        else:
            savingList = theList
            savingListMD5 = theHash

        # In any case (quit or not) if needed, save
        try:
            with open(self.saveFile, 'wb') as file:
                pickle.dump(savingList, file)
        except:
            self.bottomBar.showMessage('Error: could not save.')
            return False
        self.savedMD5 = savingListMD5

        self.bottomBar.showMessage('Save successful', 5E3)
        return True

    def constructSavingList(self):
        # Construct data to save
        savingList = []
        for element in self.cavity.elementList:
            my_dict = {}
            my_dict['type'] = element['Type']
            my_dict['entry1_val'] = element['Widget'].readEntry('entry1')
            my_dict['entry2_val'] = element['Widget'].readEntry('entry2')
            my_dict['wavelength'] = self.cavity.wl_mm
            savingList.append(my_dict)
        # Creating hash
        hashingData = json.dumps(savingList, sort_keys=True).encode('utf-8')
        savingListMD5 = hashlib.md5(hashingData)
        return savingList, savingListMD5

    def checkHash(self, savingListMD5):
        # If hash dont match, then save
        if savingListMD5.hexdigest() == self.savedMD5.hexdigest():
            return True
        else:
            return False


    ################################################
    def cavityChanges(self):
        discard, MD5 = self.constructSavingList()
        if MD5.hexdigest() == self.cavityMD5.hexdigest():
            return False
        else:
            self.cavityMD5 = MD5
            return True

    # Button functions Start
    def handle_button_calcCavity(self):
        if self.cavityChanges():
            # Calculate element matrixes
            self.bottomBar.showMessage('Calculating cavity...')
            #time_start = time.time()
            # If not valid cavity, end calculations
            if not self.cavity.basicSetup():
                self.bottomBar.showMessage('Error: construct a proper cavity first...', messageType='error')
                return False
            # If not stable cavity, error!
            if not self.cavity.calcCavity():
                self.calcCavityStatus = False
                self.bottomBar.showMessage('Error calculating the cavity: Not stable!', messageType='error')
                #self.cavityPlot.plot_init(xlabel='z (mm)', ylabel='w (µm)')
                return False
            #print('\ncalcCavity: {}'.format((time.time() - time_start)*1E6))
            self.bottomBar.showMessage('Cavity calculated!')
            self.calcCavityStatus = True

            # Plot cavity
            #time_start = time.time()
            self.bottomBar.showMessage('Plotting cavity...')
            self.cavityPlot.plotData('cavity', self.cavity.z_tan, self.cavity.wz_tan*1000, self.cavity.z_sag, self.cavity.wz_sag*1000, vmin=0)
            #print('\nplotCavity: {}'.format((time.time() - time_start)*1E6))

            # Plot vertical marks
            #time_start = time.time()
            self.cavityPlot.plotVerticals(self.cavity.z_limits_tan, self.cavity.z_names_tan)
            self.bottomBar.showMessage('Plot finished!')
            #print('\nplotVerticals: {}'.format((time.time() - time_start)*1E6))
            # Update cross section stuff
            #time_start = time.time()
            self.handle_button_crossSectionUpdate()
            #print('\ncrossSection: {}'.format((time.time() - time_start)*1E6))
            # Focus Cavity tab
            self.tabWidget_plots.setCurrentIndex(0)
            self.bottomBar.showMessage('Done')
        return True

    def handle_button_calcStability(self):
        # Get values, validating input
        elementOrder = self.stability_comboBox.currentIndex()
        if elementOrder == -1:
            self.bottomBar.showMessage('Error: Please add some optical elements.', 10E3, 'error')
            return False

        xstart = window.readEntry(self.stability_xstart)
        xend = window.readEntry(self.stability_xend)
        if (xstart is False) or (xend is False):
            self.bottomBar.showMessage('Please enter a variation range.', 5E3, 'warning')
            return False

        z, stab_tan, stab_sag, xname = self.cavity.calcStability(elementOrder, xstart, xend)

        if z is False:
            self.bottomBar.showMessage('Error: Please calculate a stable cavity first.', 10E3, 'error')
            return False

        # Plot stability
        self.stabilityPlot.plotData('stability', z, stab_tan, z, stab_sag, xlabel=xname, vmin=0, vmax=1)
        return True

    def handle_button_calcBeamsize(self):
        # Get values, validating input
        try:
            watchElementOrder = int(self.beamsize_comboBox_watch.currentText()[0])
        except:
            self.bottomBar.showMessage('Error: Please add some optical elements.', 10E3, 'error')
            return False

        varElementOrder = self.beamsize_comboBox_var.currentIndex()
        if varElementOrder == -1:
            self.bottomBar.showMessage('Error: Please add some optical elements.', 10E3, 'error')
            return False

        xstart = window.readEntry(self.beamsize_xstart)
        xend = window.readEntry(self.beamsize_xend)
        if (xstart is False) or (xend is False):
            self.bottomBar.showMessage('Please enter a variation range.', 5E3, 'warning')
            return False

        z, wz_tan, wz_sag, xname, yname = self.cavity.calcBeamsize(watchElementOrder, varElementOrder, xstart, xend)

        if z is False:
            self.bottomBar.showMessage('Error: Please calculate a stable cavity first.', 10E3, 'error')
            return False

        # Plot beam size
        self.beamsizePlot.plotData('beamsize', z, wz_tan, z, wz_sag, xlabel=xname, ylabel=yname)
        return True

    def handle_button_crossSectionUpdate(self):
        # if not self.cavity.calcCavity():
        #     return False                      # I THINK NOT NEEDED (too much)
        # Get z and its shape
        try:
            z = self.cavity.z_tan
        except:
            self.bottomBar.showMessage('Error: Please calculate a stable cavity first.', 10E3, 'error')
            return False
        zShape = np.shape(z)
        # Adjust slider Max value accordingly:
        # number of colums times 100 (should be number of rows zshape[1], but shape may not get it), minus 1
        try:
            maxValue = (zShape[0]*100)-1
        except:
            #print(zShape)
            pass
        self.crossSectionSlider.setMaximum(maxValue)
        self.crossSectionSlider.setTickInterval(round(maxValue/10))

        self.modified_crossSectionSlider(0)

    def modified_crossSectionSlider(self, value):
        try:
            iCoord = int(value/100)
            jCoord = value%100
            zvalue = self.cavity.z_tan[iCoord][jCoord]
            wz_tan = self.cavity.wz_tan[iCoord][jCoord]
            wz_sag = self.cavity.wz_sag[iCoord][jCoord]
            # Update text box
            self.update_crossSectionBox(zvalue)
            # Limits
            max_tan = np.amax(self.cavity.wz_tan)
            max_sag = np.amax(self.cavity.wz_sag)
            max_limit = max(max_tan,max_sag)*1000/2
            max_limit = max_limit + max_limit*0.1
            if max_limit:
                if math.isinf(max_limit) or math.isnan(max_limit):
                    max_limit = 1E6
            # Plot
            self.crossSectionPlot.plotData('crossSection', 0, wz_tan*1000, 0, wz_sag*1000, hmin=-max_limit, hmax=max_limit, vmin=-max_limit, vmax=max_limit)
        except AttributeError:
            self.bottomBar.showMessage('Error: Please calculate a stable cavity first.', 10E3, 'warning')
        except:
            self.bottomBar.showMessage('Error: Please report this error.', 10E3)
            raise

    def update_crossSectionBox(self, value):
        self.crossSectionBox.setText(str(round(value*100)/100))

    def update_crossSectionSlider(self):
        #crossSectionBox_value = self.crossSectionBox.text()
        #self.slider.setSliderPosition(spinbox_value)
        pass

    def tab_designer_creation(self):
        # First of all actually build the cavity (and check for errors)
        if self.cavityChanges():
            if not self.cavity.calcCavity():
                return False
        layout = self.designerListLayout
        #self.scrollArea_computation.
        self.designerElements = []
        for element in self.cavity.elementList:
            try:
                item = DesignerWidget(element['Order'], element['Type'], element['entry1'], element['entry2'])
            except:
                item = DesignerWidget(element['Order'], element['Type'])
            layout.addWidget(item)

            myDict = {'ID': item.itemID, 'Widget': item, 'Type': element['Type'], 'Order': element['Order'], 'oldEntry1': element['entry1'], 'oldEntry2': element['entry2']}
            self.designerElements.append(myDict)

        # Add Stability condition
        self.handle_button_conditionAdd(disableWidget=True)
        return True

    def tab_designer_destruction(self):
        layout = self.designerListLayout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        layout = self.designerConditionsLayout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.cavity.conditionList = []
        return True

    def handle_button_conditionAdd(self, disableWidget=False):
        item = ConditionWidget()
        if disableWidget:
            item.setDisabled(True)
        self.designerConditionsLayout.addWidget(item)
        self.cavity.addCondition(item)

    def handle_button_conditionDel(self):
        if self.conditionFocus != None:
            for item in self.conditionFocus:
                self.cavity.delCondition(item)

    def handle_button_calcSolutions(self):
        self.clearLayout(self.designerSolutionsLayout)
        elementList = self.cavity.elementList
        conditionList = self.cavity.conditionList
        self.solutionsBox = SD.SolutionsTab()
        self.designerSolutionsLayout.addWidget(self.solutionsBox)
        self.tabWidget_plots.setCurrentIndex(4)

        designerList = self.designerElements
        iterElements, combination, stablility, results = self.cavity.calcSolutions(designerList, conditionList)

        if results:
            self.presentResults(self.solutionsBox, iterElements, elementList, conditionList, combination, stablility, results)

    def presentResults(self, the_box, iter_elements, element_list, condition_list, combination, stability, results):
        no_valid_results = True
        # Headers
        the_box.addHeaders(iter_elements, condition_list)
        # Results
        for i, j in enumerate(results):
            # Only results that match all conditions (maybe should be equal to...)
            if len(j) > len(condition_list)-1:
                the_box.addRow(combination[i], stability[i], results[i], condition_list)
                no_valid_results = False

        # Show message in status bar
        if no_valid_results:
            self.bottomBar.showMessage('Attention: No valid results.', messageType='warning')
        else:
            self.bottomBar.showMessage('Calculations finished')


    def setWavelength(self):
        wl_nm = self.readEntry(self.wlBox)
        wl_mm = wl_nm/1E6
        if wl_mm != self.cavity.wl_mm:
            self.cavity.wl_mm = wl_mm
            self.bottomBar.showWavelength(self.wlLabel, wl_mm)

    ############################################################################
    # Move Up
    def handle_button_moveUp(self):
        if self.elementFocus != None:
            for elementID in self.elementFocus:
                element = window.cavity.findElement(elementID)
                element['Widget'].moveUp()
            self.populateComboBoxes()
    def handle_button_moveDown(self):
        if self.elementFocus != None:
            for elementID in reversed(self.elementFocus):
                element = window.cavity.findElement(elementID)
                element['Widget'].moveDown()
            self.populateComboBoxes()

    def handle_button_delete(self):
        if self.elementFocus != None:
            for elementID in reversed(self.elementFocus):
                element = window.cavity.findElement(elementID)
                element['Widget'].moveBottom()
                element['Widget'].deleteLater()
                element['Icon'].deleteLater()
                window.cavity.elementList.pop()
                window.cavity.numberOfElements = window.cavity.numberOfElements - 1
                window.updateElementList()
            self.elementFocus = []
            self.populateComboBoxes()

    # Add element
    def handle_button_addElement(self, name=None, entry1=None, entry2=None):
        if not name:
            buttonName = self.sender().objectName()
            # Nice name for on screen print
            elementName = buttonName[7:].capitalize()
            for i in range(len(buttonName[7:])):
                if buttonName[7+i].isupper():
                    elementName = buttonName[7:7+i].capitalize() + " " + buttonName[7+i:]
        else:
            if len(name) != 1:
                oldName = []
                for word in name.split():
                    oldName.append(word.capitalize())
                elementName = " ".join(oldName)

        newElement = ElementWidget(window.cavity.numberOfElements, elementName, entry1, entry2)
        # Add widget to element box
        self.elementListLayout.addWidget(newElement)

        # Element Icon
        newIcon = IconWidget(elementName)
        # Add icon to cavity representation
        self.cavityIconsLayout.addWidget(newIcon)

        # Element is vectorial?
        if elementName in ['Distance','Block','Brewster Plate','Brewster Crystal']:
            vector = True
        else:
            vector = False
        # Add element to cavity-class
        self.cavity.addElement(newElement, newIcon, vector)

        # Update combo boxes
        self.populateComboBoxes()

        window.cavity.numberOfElements = window.cavity.numberOfElements + 1
        self.toggleDesigner()

    def readEntry(self, entry):
        state = window.validatorFloat.validate(entry.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            #color = '#c4df9b' # green
            color = ''
            try:
                value = float(entry.text().replace(",", "."))
            except:
                # MAYBE PUT A MESSAGE HERE SAYING INVALID FLOAT
                # TO THE MESSAGE BAR
                entry.setText("")
                value = False
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            value = False
        else:
            color = '#f6989d' # red
            value = False
        entry.setStyleSheet('QLineEdit { background-color: %s }' % color)
        return value

    # Button functions End
    ################################################

    # ==========================================================================
    # SHOW ABCD
    # ==========================================================================
    def showABCD(self):
        matrixWindow = matrixWidget.MainWidget()
        matrixWindow.title('ABCD Matrices')

        def formWidgets(name, valueT, valueS):
            widget_tan = matrixWidget.MatrixWidget()
            widget_sag = matrixWidget.MatrixWidget()
            widget_tan.setValues(values_tan)
            widget_sag.setValues(values_sag)
            matrixWindow.addFormContent(0, name, widget_tan)
            matrixWindow.addFormContent(1, name, widget_sag)

        try:
            values_tan = list(itertools.chain.from_iterable(self.cavity.cavityMatrix[0]))
            values_sag = list(itertools.chain.from_iterable(self.cavity.cavityMatrix[1]))
        except:
            self.bottomBar.showMessage('Error: No matrices calculated yet.', 10E3, messageType='error')
            return False

        name = 'Cavity matrix'
        formWidgets(name, values_tan, values_sag)

        for element in self.cavity.elementList:
            if 'matrix' in element:
                values_tan = list(itertools.chain.from_iterable(element['matrix'][0]))
                values_sag = list(itertools.chain.from_iterable(element['matrix'][1]))

                name = str(element['Order']) + ' ' + element['Type']
                formWidgets(name, values_tan, values_sag)

        return True

    # ==========================================================================
    # UPDATES
    # ==========================================================================
    def checkupdates(self):
        status, webVersion = updates.checkupdates(self.version)
        self.inform_updating(status, webVersion)
        return status

    def inform_updating(self, status, webVersion):
        if status == 200:
            message = 'SimCav is up-to-date (v{})'.format(self.version)
            timer = 10E3
        elif status == 0:
            message = 'IMPORTANT UPDATE: please update ASAP.'
            timer = 0
        elif status == 1:
            message = 'A new version is available ({} -> {})'.format(self.version, webVersion)
            timer = 0
        elif status == 2:
            message = 'Error fetching version information: Unknown error.'
            color = 'red'
            timer = 10E3
        elif status == 400:
            message = 'Error fetching version information: Connection error (no internet?)'
            timer = 10E3
        elif status == 404:
            message = 'Unable to retrieve online information, please try again later.'
            timer = 10E3
        elif status == 408:
            message = 'Error fetching online version information: Timeout error.'
            timer = 10E3
        elif status == 1000:
            message = 'You are living in the future! (v{} beta)'.format(self.version)
            timer = 10E3
        else:
            message = "Not sure what's going on..."
        # Corresponding message
        self.bottomBar.showMessage(message)
        # Enable/disable toolbar button.
        if status in [0,1]:
            self.actionUpdate.setEnabled(True)
        else:
            self.actionUpdate.setDisabled(True)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
              child.widget().deleteLater()

    # Reimplement closing event
    def closeEvent(self, theEvent):
        print('close event called')
        # Construct saving list
        savingList, savingListMD5 = self.constructSavingList()
        # Check hash, if no changes then quit
        equalHash = self.checkHash(savingListMD5)
        if equalHash:
            theEvent.accept()
        else:
            # If changes in hash, create modal dialogue and ask for instructions
            msgBox = QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setWindowTitle("Save cavity?")
            msgBox.setText("The document has been modified.");
            msgBox.setInformativeText("Do you want to save your changes?");
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel);
            msgBox.setDefaultButton(QMessageBox.Save);
            reply = msgBox.exec_();

            # If choosing Save
            if reply == QtWidgets.QMessageBox.Save:
                if self.fileSave(quit=True, theList=savingList, theHash=savingListMD5):
                    theEvent.accept()
                else:
                    theEvent.ignore()
            elif reply == QtWidgets.QMessageBox.Cancel:
                theEvent.ignore()
            else:
                theEvent.accept()

#===============================================================================

#===============================================================================
# Canvas plot
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, xlabel='', ylabel=''):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        fig.set_tight_layout(True)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        #FigureCanvas.setSizePolicy(self,
        #        QSizePolicy.Expanding,
        #        QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot_init(xlabel, ylabel)


    def plot_init(self, xlabel, ylabel):
        #self.axes.set_title('Plot init')
        #x = [0,1,2,3,4,5]
        #self.axes.plot(x,x)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.set_ylim(bottom=0) # Adjust the vertical min
        self.axes.set_title("λ = ") # Title
        self.axes.grid(linestyle='dashed')
        self.draw()

    def plotData(self, plotType, x1, y1, x2, y2, xlabel=None, ylabel=None, hmin=None, hmax=None, vmin=None, vmax=None):
        # Get previous labels
        xlabel_old = self.axes.get_xlabel()
        ylabel_old = self.axes.get_ylabel()
        # Clear figure
        self.axes.clear()

        # Plot data
        if plotType == 'cavity':
            # Plot for a whole cavity
            # -> This is due to the Z variable being a multidimensional array!!!
            if len(x1) >= 1:
                for zrow, wrow in zip(x1,y1):
                    tan, = self.axes.plot(zrow, wrow, 'g', label='Tangential')
                for zrow, wrow in zip(x2,y2):
                    sag, = self.axes.plot(zrow, wrow, 'b', label='Sagittal')
            else:
                x1.append(0)
                y1.append(0)
                x2.append(0)
                y2.append(0)
                for zrow, wrow in zip(x1, y1):
                    tan, = self.axes.plot(zrow, wrow, 'g', label='Tangential')
                for zrow, wrow in zip(x2, y2):
                    sag, = self.axes.plot(zrow, wrow, 'b', label='Sagittal')
            self.axes.legend(handles=[tan,sag], loc='upper left')
        elif plotType == 'crossSection':
            self.axes.set_aspect('equal')
            ellipse = Ellipse(xy=(x1,x2), width=2*y2, height=2*y1)
            self.axes.add_artist(ellipse)
        else:
            # Other plots
            tan, = self.axes.plot(x1, y1, 'g', label='Tangential')
            sag, = self.axes.plot(x2, y2, 'b', label='Sagittal')
            self.axes.legend(handles=[tan,sag], loc='upper left')

        # Plot Labels
        if xlabel == None:
            self.axes.set_xlabel(xlabel_old)
        else:
            self.axes.set_xlabel(xlabel)
        # Plot Labels
        if ylabel == None:
            self.axes.set_ylabel(ylabel_old)
        else:
            self.axes.set_ylabel(ylabel)

        # Plot limits
        # xmin and xmax should be an input to the plot function
        if plotType == 'crossSection':
            self.axes.set_xlim(left=2*hmin, right=2*hmax)
            self.axes.set_ylim(bottom=2*vmin, top=2*vmax)
        else:
            self.axes.set_xlim(left=hmin, right=hmax)
            self.axes.set_ylim(bottom=vmin, top=vmax)

        # Plot title
        self.axes.set_title("λ = " + str(window.cavity.wl_mm*1E6) + " nm")

        self.axes.grid(linestyle='dashed')
        self.draw_idle()
        return True
        #toolbar = self.figure.canvas.toolbar
        #toolbar.update()
        #toolbar.push_current()

    def plotVerticals(self, xpoints, xnames):
        y0, y1 = self.axes.get_ylim()
        for xi, element in zip(xpoints,xnames):
            self.axes.axvline(x=xi, color='orange', alpha=0.7, linewidth=0.7)
            if 'Mirror' in element:
                self.axes.text(xi,y0+5, element, rotation=90, horizontalalignment='right', verticalalignment='bottom')
            elif 'Lens' in element:
                self.axes.text(xi, y0+5, element, rotation=90, horizontalalignment='right', verticalalignment='bottom')
            elif 'Block' in element:
                self.axes.text((xi+xold)/2, y1-5, element,rotation=0, horizontalalignment='center', verticalalignment='top', color='w', bbox=dict(facecolor='k', edgecolor='k', boxstyle='round', linewidth=0, alpha=0.65))
            else:
                self.axes.text((xi+xold)/2,y1-5,element,rotation=90, horizontalalignment='center', verticalalignment='top', backgroundcolor='w', bbox=dict(facecolor='w', edgecolor='k', boxstyle='round',linewidth=0.5, alpha=0.65))
            xold = xi
        self.draw_idle()
#===============================================================================

#===============================================================================
# Extra GUI elements
class IconWidget(QtWidgets.QWidget):
    def __init__(self, eType, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.elementType = eType
        #self.icon = QtWidgets.QPushButton()
        self.icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(LI.elementPixmap(eType))
        self.icon.setPixmap(pixmap)
        self.icon.setMinimumWidth(40)
        self.icon.setMinimumHeight(40)
        #self.icon.setFlat(True)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.icon)

        self.setToolTip(eType)

# Element label
class ElementWidget(QtWidgets.QWidget):
    def __init__(self, eOrder, etype, entry1=None, entry2=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.elementID = id(self)
        self.elementType = etype
        self.originalOrder = eOrder

        # Right click menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Set event Filter
        self.installEventFilter(self)

        # Appearance
        layout = QtWidgets.QHBoxLayout(self)


        self.columns = OrderedDict()
        self.columns['label_number'] = QtWidgets.QLabel(text=str(eOrder))
        self.columns['label_name'] = QtWidgets.QLabel(text=etype)
        self.columns['entry1'] = QtWidgets.QLineEdit(placeholderText="mm")
        self.columns['entry2'] = QtWidgets.QLineEdit()


        # CONFIG ---------------------------------------------------------------
        for item in self.columns:
            if 'entry' in item:
                # Validate entry boxes values
                self.columns[item].setValidator(window.validatorFloat)
                # Connect return signal
                self.columns[item].returnPressed.connect(window.button_calcCavity.click)
                # Set size
                #self.columns[item].setFixedWidth(40)
            elif 'number' in item:
                self.columns[item].setMinimumWidth(15)
                #self.columns[item].setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.columns[item].setStyleSheet("background-color: rgba(0, 0, 0, 0);")
            elif 'name' in item:
                # Set minimum width so all labels are equal whatever the element name
                self.columns[item].setMinimumWidth(110)
                self.columns[item].setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        # Validate entry boxes values
        self.columns['entry1'].setValidator(window.validatorFloat)
        self.columns['entry2'].setValidator(window.validatorFloat)
        # Connect return signal
        self.columns['entry1'].returnPressed.connect(self.entry_onReturn)
        self.columns['entry2'].returnPressed.connect(self.entry_onReturn)

        # Default values
        self.assignDefaults(etype)

        # In case of loading, assign loaded values
        if entry1:
            self.columns['entry1'].setText(str(entry1))
        if entry2:
            self.columns['entry2'].setText(str(entry2))

        # Disable entry boxes for Flat mirrors
        if etype == 'Flat Mirror':
            self.columns['entry1'].setDisabled(True)
            self.columns['entry2'].setDisabled(True)
        # CONFIG End -----------------------------------------------------------

        # Add the columns to the widget
        for i in self.columns:
            layout.addWidget(self.columns[i])

    def assignDefaults(self, eType):
        # Default values for the entries
        if eType in ['Block','Brewster Plate','Brewster Crystal']:
            self.columns['entry2'].setPlaceholderText("n")
        elif eType == 'Distance':
            self.columns['entry2'].setText(str(1))
        elif eType in ['Curved Mirror','Thin lens']:
            self.columns['entry2'].setText(str(0))
        elif eType == 'Flat Mirror':
            self.columns['entry1'].setText(str(0))
            self.columns['entry2'].setText(str(0))
            self.columns['entry1'].setDisabled(True)
            self.columns['entry2'].setDisabled(True)
        elif eType == 'Flat Interface':
            self.columns['entry1'].setText(str(0))
            self.columns['entry2'].setPlaceholderText("n2")
            self.columns['entry1'].setDisabled(True)
        elif eType == 'Curved Interface':
            self.columns['entry2'].setPlaceholderText("n2")
        else:
            self.columns['entry2'].setText(str(0))

    # Read entries
    def readEntry(self, entry):
        state = window.validatorFloat.validate(self.columns[entry].text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            #color = '#c4df9b' # green
            color = ''
            try:
                value = float(self.columns[entry].text().replace(",", "."))
            except:
                # MAYBE PUT A MESSAGE HERE SAYING INVALID FLOAT
                # TO THE MESSAGE BAR
                self.columns[entry].setText("")
                value = False
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            value = False
        else:
            color = '#f6989d' # red
            value = False
        self.columns[entry].setStyleSheet('QLineEdit { background-color: %s }' % color)
        return value

    def entry_onReturn(self):
        for element in window.cavity.elementList:
            if element['Widget'].readEntry('entry1') is False:
                element['Widget'].columns['entry1'].setFocus()
                return True
            if element['Widget'].readEntry('entry2') is False:
                element['Widget'].columns['entry2'].setFocus()
                return True
        #window.button_calcCavity.click()
        return True

    # Mouse click events
    def mousePressEvent(self, QMouseEvent):
        # If shift is pressed...
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.setFocus()
            # Save element as focused, add if mayus is pressed.
            if modifiers == QtCore.Qt.ShiftModifier and self.elementID is not None:
                window.elementFocus.append(self.elementID)
            elif modifiers == QtCore.Qt.ControlModifier:
                # Remove focus
                if self.elementID in window.elementFocus:
                    window.elementFocus.remove(self.elementID)
            else:
                window.elementFocus = self.elementID

            # Change focus into list if is an integer
            if type(window.elementFocus) == int:
                focusList = [window.elementFocus]
            else:
                focusList = window.elementFocus

            # Order list
            window.elementFocus = []
            for element in window.cavity.elementList:
                if element['ID'] in focusList:
                    window.elementFocus.append(element['ID'])

            # Change background
            for element in window.cavity.elementList:
                if element['ID'] in window.elementFocus:
                    element['Widget'].setAutoFillBackground(True)
                    element['Widget'].setBackgroundRole(QtGui.QPalette.AlternateBase)
                else:
                    element['Widget'].setAutoFillBackground(False)
                    element['Widget'].setBackgroundRole(QtGui.QPalette.Base)

            #print("Left Button Clicked")
        elif QMouseEvent.button() == QtCore.Qt.RightButton:
            #do what you want here
            self.openMenu(QMouseEvent.pos())
            #print("Right Button Clicked")

    # Filter events
    # def eventFilter(self, object, event):
    #     if event.type() == QtCore.QEvent.FocusIn:
    #         self.setAutoFillBackground(True)
    #         self.setBackgroundRole(QtGui.QPalette.AlternateBase)
    #         #print("widget has gained keyboard focus")
    #     elif event.type() == QtCore.QEvent.FocusOut:
    #         self.setAutoFillBackground(False)
    #         self.setBackgroundRole(QtGui.QPalette.Base)
    #         #print("widget has lost keyboard focus")
    #     #else:
    #     #    print(event.name())
    #     return False

    # Right click menu
    def openMenu(self, position):
        menu = QtWidgets.QMenu()
        upAction = menu.addAction("Move up")
        downAction = menu.addAction("Move down")
        action = menu.exec_(self.mapToGlobal(position))
        if action == upAction:
            self.moveUp()
        elif action == downAction:
            self.moveDown()

    # Right click functions
    def moveUp(self):
        element = window.cavity.findElement(self.elementID)
        valueOld = element['Order']
        valueNew = element['Order'] - 1

        # Do nothing if it's first element
        if element['Order'] != 0:
            # Change the other elements
            for i in window.cavity.elementList:
                if i['Order'] < valueOld and i['Order'] >= valueNew:
                    window.cavity.updateValue(i['ID'], 'Order', i['Order'] + 1)
            # Change THE element
            window.cavity.updateValue(element['ID'], 'Order', valueNew)
            # Reorder the element list
            window.cavity.reorderList()
            # Update GUI
            window.updateElementList()

    def moveDown(self):
        element = window.cavity.findElement(self.elementID)
        valueOld = element['Order']
        valueNew = element['Order'] + 1

        # Do nothing if it's first element
        if element['Order'] < window.cavity.numberOfElements - 1:
            # Change the other elements
            for i in window.cavity.elementList:
                if i['Order'] > valueOld and i['Order'] <= valueNew:
                    window.cavity.updateValue(i['ID'], 'Order', i['Order'] - 1)
            # Change THE element
            window.cavity.updateValue(element['ID'], 'Order', valueNew)
            # Reorder the element list
            window.cavity.reorderList()
            # Update GUI
            window.updateElementList()

    def moveBottom(self):
        element = window.cavity.findElement(self.elementID)
        # Change the other elements
        for i in window.cavity.elementList:
            if i['Order'] > element['Order']:
                window.cavity.updateValue(i['ID'], 'Order', i['Order'] - 1)
        # Change THE element
        window.cavity.updateValue(element['ID'], 'Order', window.cavity.numberOfElements-1)
        # Reorder the element list
        window.cavity.reorderList()
        # Update GUI
        window.updateElementList()

# Designer widget
class DesignerWidget(QtWidgets.QWidget):
    def __init__(self, eOrder, etype, entry1=None, entry2=None, entry3=1, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.elementType = etype
        self.itemID = id(self)

        layout = QtWidgets.QHBoxLayout(self)

        self.columns = OrderedDict()
        self.columns['label_number'] = QtWidgets.QLabel(text=str(eOrder))
        self.columns['label_name'] = QtWidgets.QLabel(text=etype)
        self.columns['entry1'] = QtWidgets.QLineEdit(placeholderText="mm")
        self.columns['entry2'] = QtWidgets.QLineEdit(placeholderText="mm")
        self.columns['entry3'] = QtWidgets.QLineEdit(text=str(entry3))

        # CONFIG ---------------------------------------------------------------
        for item in self.columns:
            if 'entry' in item:
                # Validate entry boxes values
                if '3' in item:
                    self.columns[item].setValidator(window.validatorInt)
                    # Set size
                    self.columns[item].setFixedWidth(30)
                else:
                    self.columns[item].setValidator(window.validatorFloat)
                    # Set size
                    self.columns[item].setFixedWidth(50)
                # Connect return signal
                #self.columns[item].returnPressed.connect(window.button_calcComputation.click)
            elif 'number' in item:
                self.columns[item].setFixedWidth(15)
                #self.columns[item].setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                pass
            elif 'name' in item:
                # Set minimum width so all labels are equal whatever the element name
                self.columns[item].setMinimumWidth(110)

        # Default values
        self.assignDefaults(etype, entry1, entry2)

        # CONFIG End -----------------------------------------------------------

        # Add the columns to the widget
        for i in self.columns:
            layout.addWidget(self.columns[i])

    def assignDefaults(self, eType, entry1, entry2):
        # Assign cavity values
        if entry1:
            self.columns['entry1'].setText(str(entry1))
            self.columns['entry2'].setText(str(entry1))

        # Special configuration for particular entries
        if eType in ['Distance','Block','Brewster Plate','Brewster Crystal']:
            pass
        elif eType in ['Curved Mirror','Thin lens']:
            pass
        elif eType == 'Curved Interface':
            pass
        elif eType == 'Flat Mirror':
            self.columns['entry1'].setText(str(0))
            self.columns['entry2'].setText(str(0))
            self.columns['entry1'].setDisabled(True)
            self.columns['entry2'].setDisabled(True)
            self.columns['entry3'].setDisabled(True)
        elif eType == 'Flat Interface':
            self.columns['entry1'].setPlaceholderText("n2")
            self.columns['entry2'].setPlaceholderText("n2")
            if entry2:
                self.columns['entry1'].setText(str(entry2))
                self.columns['entry2'].setText(str(entry2))
        else:
            pass

    # Read entries
    def readEntry(self, entry):
        state = window.validatorFloat.validate(self.columns[entry].text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            #color = '#c4df9b' # green
            color = ''
            try:
                value = float(self.columns[entry].text().replace(",", "."))
            except:
                # MAYBE PUT A MESSAGE HERE SAYING INVALID FLOAT
                # TO THE MESSAGE BAR
                self.columns[entry].setText("")
                value = False
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            value = False
        else:
            color = '#f6989d' # red
            value = False
        self.columns[entry].setStyleSheet('QLineEdit { background-color: %s }' % color)
        return value

class ConditionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.conditionID = id(self)

        self.setMinimumHeight(40)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(3,3,8,3)

        self.columns = OrderedDict()
        self.columns['condition'] = QtWidgets.QComboBox()
        self.columns['onElement'] = QtWidgets.QComboBox()
        self.columns['entry1'] = QtWidgets.QLineEdit(placeholderText='µm')
        self.columns['entry2'] = QtWidgets.QLineEdit(placeholderText='µm')

        # Default values
        self.assignDefaults()

        # Add the columns to the widget
        for i in self.columns:
            if 'entry' in i:
                self.columns[i].setValidator(window.validatorFloat)
            layout.addWidget(self.columns[i])

    def assignDefaults(self):
        self.columns['condition'].addItems(SC.allConditions)
        self.columns['condition'].currentIndexChanged['QString'].connect(self.setConditionElements)
        self.columns['condition'].setMinimumWidth(100)
        self.columns['onElement'].setMinimumWidth(90)
        self.columns['entry1'].setMinimumWidth(40)
        self.columns['entry2'].setMinimumWidth(40)
        self.setConditionElements("Stability")

    def setConditionElements(self, condition):
        eList, vList, not_vList = window.cavity.optionMenuLists()
        self.columns['onElement'].clear()
        self.columns['entry1'].clear()
        self.columns['entry2'].clear()
        if condition == "w(0)":
            self.columns['onElement'].addItem(eList[0])
            self.columns['onElement'].setDisabled(True)
            self.columns['entry1'].setPlaceholderText('µm')
            self.columns['entry2'].setPlaceholderText('µm')
        elif condition == "w(element)":
            self.columns['onElement'].addItems(not_vList)
            self.columns['onElement'].setDisabled(False)
            self.columns['entry1'].setPlaceholderText('µm')
            self.columns['entry2'].setPlaceholderText('µm')
        elif condition == "Waist":
            self.columns['onElement'].addItems(vList)
            self.columns['onElement'].setDisabled(False)
            self.columns['entry1'].setPlaceholderText('µm')
            self.columns['entry2'].setPlaceholderText('µm')
        elif condition == "Cav. length":
            #self.columns['onElement'].addItem(eList[0])
            self.columns['onElement'].setDisabled(True)
            self.columns['entry1'].setPlaceholderText('mm')
            self.columns['entry2'].setPlaceholderText('mm')
        elif condition == "Stability":
            #self.columns['onElement'].addItem(eList[0])
            self.columns['onElement'].setDisabled(True)
            self.columns['entry1'].setText('0')
            self.columns['entry2'].setText('1')

    # Mouse click events
    def mousePressEvent(self, QMouseEvent):
        # Do nothing if widget is disabled:
        if not self.isEnabled:
            print('Widget disabled')
            QMouseEvent.ignore()
            return False
        # If shift is pressed...
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.setFocus()
            # Save element as focused, add if mayus is pressed.
            if modifiers == QtCore.Qt.ShiftModifier and self.conditionID is not None:
                window.conditionFocus.append(self.conditionID)
            elif modifiers == QtCore.Qt.ControlModifier:
                # Remove focus
                if self.conditionID in window.conditionFocus:
                    window.conditionFocus.remove(self.conditionID)
            else:
                window.conditionFocus = [self.conditionID]

            # Change background
            for element in window.cavity.conditionList:
                if element['ID'] in window.conditionFocus:
                    element['Widget'].setAutoFillBackground(True)
                    element['Widget'].setBackgroundRole(QtGui.QPalette.AlternateBase)
                else:
                    element['Widget'].setAutoFillBackground(False)
                    element['Widget'].setBackgroundRole(QtGui.QPalette.Base)

    # Read entries
    def readEntry(self, entry):
        state = window.validatorFloat.validate(self.columns[entry].text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            #color = '#c4df9b' # green
            color = ''
            try:
                value = float(self.columns[entry].text().replace(",", "."))
            except:
                # MAYBE PUT A MESSAGE HERE SAYING INVALID FLOAT
                # TO THE MESSAGE BAR
                self.columns[entry].setText("")
                value = False
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            value = False
        else:
            color = '#f6989d' # red
            value = False
        self.columns[entry].setStyleSheet('QLineEdit { background-color: %s }' % color)
        return value

#===============================================================================
# Launching the program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MyApp()

    window.show()
    sys.exit(app.exec_())
#===============================================================================
