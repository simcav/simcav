#!/usr/bin/env python3
import sys, os
import tkinter as tk
from tkinter import messagebox

# Add user site to path, just in case.
import site
sys.path.insert(0, site.USER_SITE)

# Defining exceptions
class PythonVersionError(Exception):
	def __init__(self):
		self.message = "  SimCav only works with Python 3, but an older version was detected.\n  Please update to Python 3.\n"
class PipInstallError(Exception):
	def __init__(self, package):
		self.message = "Install the package '" + package + "' manually and try again."
class NotModuleError(Exception):
	def __init__(self, package):
		self.message = "Please install '" + package + "' before installing SimCav."
class UserCancel(Exception):
	def __init__(self):
		self.expression = "\nError: Cancelled by user."
		self.message = ""

class TheCode():
	def __init__(self, gui_app):
		self.gui_app = gui_app
		self.func_install(self.gui_app)
	
	# Install with pip
	def install(self, package):
		self.gui_app.printcmd("\n ---------------------\n Installing " + package)
		try:
			try:
				pipcode = self.pipmain(['install', package, '--user', '--disable-pip-version-check', '--no-warn-conflicts'])
			except:
				# Older versions of pip may lack no-conflicts flag
				pipcode = self.pipmain(['install', package, '--user', '--disable-pip-version-check'])
			if not pipcode:
				return True
			else:
				self.gui_app.printcmd(" Error: could not find'" + package + "'")
				return False
		except Exception as inst:
			self.gui_app.printcmd(inst)
			self.gui_app.printcmd("Error")
			return False
	# Uninstall with pip
	def uninstall(self, package):
		try:
			self.pipmain(['uninstall', package, '-y', '--disable-pip-version-check'])
			return True
		except Exception as inst:
			self.gui_app.printcmd(inst)
			self.gui_app.printcmd("Error")
			return False

	def download_file(self, url, folderfile):
		import urllib.request
		try:
			urllib.request.urlretrieve(url, folderfile)
		except:
			raise

	def writepath(self, user_site):
		with open("user_path.txt") as f:
			f.write(user_site)

	def func_install(self, gui_app):
		try:	
			import sys
			
			guestOS = sys.platform
			
			# Require Python 3 to work
			if sys.version_info.major < 3:
				raise PythonVersionError
			else:
				gui_app.printcmd("OK:	Python 3")
			
			try:
				pip = __import__('pip')
				gui_app.printcmd("OK:	Pip")
			except ModuleNotFoundError:
				gui_app.printcmd("Warning: Pip module not found.")
				gui_app.printcmd("         Required dependencies won't be automatically installed.")
				
			try:
				from pip._internal import main as pipmain
			except:
				from pip import main as pipmain
			self.pipmain = pipmain

			# List of modules required by SimCav
			simcav_modules = ['tkinter',  'numpy', 'requests', 'matplotlib', 'PyQt5']#, 'itertools', 'os', 'pickle', 'webbrowser'] 
			# The last ones, commented, are part of the standard python distribution.
			
			# List of modules required by the installer
			installation_modules = []
			if guestOS == 'win32':
				installation_modules.append('winshell')
			installed_modules = []
			# Check that modules exist / can be imported
			gui_app.printcmd("\nChecking required modules:")
			haveIinstalled = False
			for i in simcav_modules+installation_modules:
				try:
					__import__(i)
					gui_app.printcmd("OK:	" + i)
				except ModuleNotFoundError:
					gui_app.printcmd('x:	' + i)
					gui_app.printcmd('\n Module ' + i + ' not found, but is required for SimCav to work')

					useranswer = gui_app.askuserbox("Should I try to install '" +i+"'?")
					if useranswer:
						haveIinstalled = self.install(i)
						if haveIinstalled:
							if  i in installation_modules:
								installed_modules.append(i)
						else:
							raise PipInstallError(i)
					else:
						raise NotModuleError(i)
			gui_app.printcmd('\nAll dependencies satisfied! Continuing installation...\n')
							
			#===============================================
			# SIMCAV INSTALLATION
						
			# Locations
			if guestOS == 'win32':
				import winshell
				user_home = winshell.folder("profile")
			else:
				user_home = os.path.expanduser('~')
				
			simcav_home = os.path.join(user_home, 'SimCav')
			
			gui_app.printcmd('Install location: ' + simcav_home)
			
			# Checking / creating SimCav folder
			if not os.path.exists(simcav_home):
				os.makedirs(simcav_home)
				user_proceed = gui_app.askuserbox("This will install SimCav in your system.\nContinue?")
			else:
				user_proceed = gui_app.askuserbox("The install directory already exist \n(" + simcav_home + ")\nOverwrite?")	
			if not user_proceed:
				raise UserCancel
			install_window.update_idletasks()	
			# Downloading files
			import requests
			simcav_api = 'https://gitlab.com/api/v4/projects/6789132/repository/'
			simcav_url = 'https://gitlab.com/simcav/simcav/raw/master/'
			
			# Required files
			simcav_files = ['gui.ui', 'load_icons.py', 'main.py', 'matrixWidget.py', 'matrixWidget.ui', 'simcav_ABCD.py', 'simcav_conditions.py', 'simcav_designer.py', 'simcav_elementFeatures.py', 'simcav_physics.py', 'simcav_statusBar.py', 'simcav_updates.py', 'style_designerSolutions.css', 'style_main.css', 'updater.py']
			simcav_icons = []
			simcav_saves = []
			simcav_misc = ['LICENSE', 'Disclaimer.txt', 'README.md', 'CHANGELOG']
			
			# Get icons list from repo
			r = requests.get(simcav_api+'tree?ref=master&per_page=100', params={'path':'Icons/'})
			for i in r.json():
				if not '.svg' in i['name']:
					simcav_icons.append(i['name'])
			# Get saves list from repo
			r = requests.get(simcav_api+'tree?ref=master&per_page=100', params={'path':'Saves/'})
			for i in r.json():
				simcav_saves.append(i['name'])	
			#=================================
			gui_app.printcmd('\n Creating subfolders...')
			# Icons folder
			try:
				icons_folder = os.path.join(simcav_home,'Icons')
				if not os.path.exists(icons_folder):
					os.makedirs(icons_folder)
			except:
				gui_app.printcmd("Error creating 'Icons' folder")
			# Saves folder
			try:
				saves_folder = os.path.join(simcav_home,'Saves')
				if not os.path.exists(saves_folder):
					os.makedirs(saves_folder)
			except:
				gui_app.printcmd("Error creating 'Saves' folder")
			
			#=================================
			#Downloading SimCav files
			gui_app.printcmd('\n Downloading modules...')
			for i in simcav_files:
				gui_app.printcmd("     Downloading " + i)
				self.download_file(simcav_url + i, os.path.join(simcav_home, i))
			
			gui_app.printcmd('\n Downloading icons...')
			for i in simcav_icons:
				gui_app.printcmd("     Downloading " + i)
				self.download_file(simcav_url + 'Icons/' + i, os.path.join(icons_folder, i))
				
			gui_app.printcmd('\n Downloading examples...')
			for i in simcav_saves:
				gui_app.printcmd("     Downloading " + i)
				self.download_file(simcav_url + 'Saves/' + i, os.path.join(saves_folder, i))
			
			gui_app.printcmd('\n Downloading readmes...')
			for i in simcav_misc:
				gui_app.printcmd("     Downloading " + i)
				self.download_file(simcav_url+i, os.path.join(simcav_home, i))
				
			gui_app.printcmd('\n Downloading manual...')
			if not 'manual.pdf' in os.listdir(simcav_home):
				self.download_file(simcav_url + 'Manual/manual.pdf', os.path.join(simcav_home, 'manual.pdf'))
			#gui_app.printcmd('\n Files downloaded')
			#=================================================================
			# Create system links
			gui_app.printcmd('\n Creating shortcuts...')
			# Create desktop shortcut
			if guestOS == 'win32':
				# NOT WORKING YET
				
				def create_shortcut(thepath, thehome):
					gui_app.printcmd('\n Creating shortcut in ' + thepath)
					python_path = os.path.join(os.path.dirname(sys.executable),'pythonw.exe')
					mainfile_path = os.path.join(thehome, 'simcav_main.py')
					icons_folder = os.path.join(thehome,'Icons')
					with winshell.shortcut(thepath) as thelink:
						thelink.path = python_path
						thelink.arguments = '"'+mainfile_path+'"'
						thelink.working_directory = thehome
						thelink.description = "Shortcut to SimCav"
						thelink.icon_location = (os.path.join(icons_folder,'logo-tg3.ico'),0)
				
				# Create icon in Desktop
				#python_path = os.path.dirname(sys.executable)
				shortcut_path = os.path.join(winshell.desktop(), 'SimCav.lnk')
				create_shortcut(shortcut_path, simcav_home)
				
				# Create StartMenu access
				startmenu_path = os.path.join(winshell.start_menu(),'Programs', 'SimCav.lnk')
				create_shortcut(startmenu_path, simcav_home)
					
			elif guestOS == 'linux':
				desktop_path = os.path.join(os.path.join(user_home, 'Desktop'), 'SimCav.desktop')
				desktop_content = "[Desktop Entry]\nType=Application\nName=SimCav\nGenericName=Laser cavity simulator\nComment=Application for design and simulation of laser resonators\nExec=python " + os.path.join(simcav_home, 'simcav_main.py') + "\nIcon=" + os.path.join(icons_folder, 'logo-tg3.png') + "\nPath=" + simcav_home + "\nTerminal=false\nStartupNotify=false\nCategories=Education;Science"
				
				with open(desktop_path, 'w') as desktop_file:
					desktop_file.write(desktop_content)
				with open(os.path.join(user_home,'.local','share','applications','SimCav.desktop'), 'w') as desktop_file:
					desktop_file.write(desktop_content)
			
			gui_app.printcmd('\nInstallation finished!')
				
		except Exception as inst:
			gui_app.printcmd('\nError: ' + type(inst).__name__)
			if type(inst).__name__ in ['PythonVersionError', 
										'NotModuleError',
										'PipInstallError',
										'UserCancel']:
				gui_app.printcmd(inst.message)
			else:
				raise
				
		finally:
			for i in installed_modules:
				self.uninstall(i)
			gui_app.printcmd('\nYou may close this window.')

class Display(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)		
		self.parent = parent

		self.output = tk.Text(self, width=100, height=15, background = 'black', fg='white')
		self.output.pack(side=tk.LEFT, fill='both', expand=1)

		self.scrollbar = tk.Scrollbar(self, orient="vertical", command = self.output.yview)
		self.scrollbar.pack(side=tk.RIGHT, fill="y")

		self.output['yscrollcommand'] = self.scrollbar.set

		self.count = 1
		self.configure(background='black')
		self.pack(fill='both', expand=1)
		
		self.thecode = TheCode(self)
		
	def printcmd(self, txt):
		self.output.insert(tk.END,str(txt))
		self.output.insert(tk.END,'\n')
		self.output.see(tk.END)
		self.update_idletasks()
		install_window.update_idletasks()
	
	def askuserbox(self, message):
		askbox = messagebox.askyesno('Question', message)
		return askbox
			
	def call_close(self):
		messagebox.showinfo('quit', "Quitting.")
		killing_root()


def killing_root():
	install_window.destroy()

if __name__ == '__main__':
	global install_window
	install_window = tk.Tk()
	install_window.title("SimCav installer")
	# Kill process when click on window close button
	install_window.protocol("WM_DELETE_WINDOW", killing_root)
	
	cmd_frame = Display(install_window)
	install_window.mainloop()