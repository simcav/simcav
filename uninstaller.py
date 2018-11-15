#!/usr/bin/env python3
import sys, os, shutil
import tkinter as tk
from tkinter import messagebox

# Add user site to path, just in case.
import site
sys.path.insert(0, site.USER_SITE)

class TheCode():
	def __init__(self, title=None):
		self.Tk = tk.Tk()
		self.Tk.title(title)
		# Kill process when click on window close button
		self.Tk.protocol("WM_DELETE_WINDOW", self.killing_root)
		
		self.installed_modules = []

		gui_app = Display(self.Tk)
		self.gui_app = gui_app
		self.func_main(self.gui_app)
		self.Tk.mainloop()

	def killing_root(self):
		self.Tk.destroy()

	def func_main(self, gui_app):
		try:
			# If windows, we need Winshell
			if 'win' in gui_app.guestOS:
				try:
					import winshell
				except:
					self.install('winshell')
					self.installed_modules.append('winshell')
					import winshell
					
			# Uninstall from:
			uninstallFilePath = os.path.realpath(__file__)
			uninstallPath = uninstallFilePath.replace('uninstaller.py', '')
					
			# Other install locations (links)
			if 'win' in gui_app.guestOS:
				desktop_path = os.path.join(gui_app.winshell.desktop(), 'SimCav.lnk')
				startmenu_path = os.path.join(gui_app.winshell.start_menu(), 'Programs', 'SimCav.lnk')
			else:
				user_home = os.path.expanduser('~')
				desktop_path = os.path.join(user_home, 'Desktop', 'SimCav.desktop')
				startmenu_path = os.path.join(user_home, '.local', 'share', 'applications', 'SimCav.desktop')
				
			# Display uninstallation plan
			gui_app.printcmd("Uninstalling SimCav from:")
			gui_app.printcmd(uninstallPath)
			gui_app.printcmd("Deleting links from:")
			gui_app.printcmd(desktop_path)
			gui_app.printcmd(startmenu_path)
			
			# Files to delete
			simcav_files = ['gui.ui', 'load_icons.py', 'main.py', 'matrixWidget.py', 'matrixWidget.ui', 'simcav_ABCD.py', 'simcav_conditions.py', 'simcav_designer.py', 'simcav_elementFeatures.py', 'simcav_physics.py', 'simcav_statusBar.py', 'simcav_updates.py', 'style_designerSolutions.css', 'style_main.css', 'updater.py', 'installer.py', 'uninstaller.py']
			simcav_misc = ['LICENSE', 'Disclaimer.txt', 'README.md', 'CHANGELOG', 'manual.pdf']
			# ...and everything in SimCav/Icons/
			
			gui_app.printcmd("\nSave files must be deleted manually.\n")
			# Final confirmation
			user_asnwer = gui_app.askuserbox('Continue?')
			if not user_asnwer:
			 		raise UserCancel
					
			gui_app.printcmd('Deleting files...')
			# Main files
			for i in simcav_files:
				self.deleteFile(uninstallPath, i)
				
			# Misc files
			for i in simcav_misc:
				self.deleteFile(uninstallPath, i)
				
			# Icons
			gui_app.printcmd('Deleting icons...')
			iconsPath = os.path.join(uninstallPath, 'Icons')
			for i in os.listdir(iconsPath):
				self.deleteFile(iconsPath, i)
			shutil.rmtree(iconsPath)
			
			# Cache
			gui_app.printcmd('Deleting cache...')
			cachePath = os.path.join(uninstallPath, '__pycache__')
			for i in os.listdir(cachePath):
				self.deleteFile(cachePath, i)
			shutil.rmtree(cachePath)
				
			# Removing shortcuts
			gui_app.printcmd('Deleting shortcuts')
			gui_app.printcmd(    'Removing ' + desktop_path)
			os.remove(desktop_path)
			gui_app.printcmd(    'Removing ' + startmenu_path)
			os.remove(startmenu_path)
			
			# And we are done!
			gui_app.printcmd('\nUninstall finished!')
			
			# Remove installed Python modules
			for i in self.installed_modules:
				self.uninstall(i)
			
		except Exception as inst:
			gui_app.printcmd('\nError: ' + type(inst).__name__)
			if type(inst).__name__ in ['PythonVersionError', 
										'NotModuleError',
										'PipInstallError',
										'UserCancel']:
				gui_app.printcmd(inst.message)
			else:
				gui_app.printcmd(inst)
				
		finally:
			gui_app.printcmd('You may close this window.')
			
			
	# Delete file function
	def deleteFile(self, folder, file):
		todelete = os.path.join(folder, file)
		try:
			os.remove(todelete)
			self.gui_app.printcmd('    Removing ' + file)
		except:
			self.gui_app.printcmd('    Could not delete ' + file)
		
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
			
# Console GUI
class Display(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)		
        self.parent = parent

        self.output = tk.Text(self, width=100, height=15, background = 'black', fg='white')
        self.output.pack(side=tk.LEFT, fill='both', expand=1)

        self.scrollbar = tk.Scrollbar(self, orient="vertical", command = self.output.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        self.output['yscrollcommand'] = self.scrollbar.set
        
        self.pythoncheck()
        self.guestOS = sys.platform

        self.count = 1
        self.configure(background='black')
        self.pack(fill='both', expand=1)
        #self.wait_window()
        #self.thecode = thecode(self)
        #self.thecode.func_install(self)
		
    def printcmd(self, txt):
        self.output.insert(tk.END,str(txt))
        self.output.insert(tk.END,'\n')
        self.output.see(tk.END)
        self.update_idletasks()

    def askuserbox(self, message):
        askbox = messagebox.askyesno('Question', message)
        return askbox
		
	# Python version
    def pythoncheck(self):
        # Require Python 3 to work
        if sys.version_info.major < 3:
            raise PythonVersionError
            return 1
        else:
            self.printcmd("OK:	Python version.")
            return 0
    	
    def call_close(self, parent):
        messagebox.showinfo('quit', "Quitting.")
        parent.killing_root()
		
# Defining exceptions
class PythonVersionError(Exception):
	def __init__(self):
		self.expression = "\nError: Incompatible Python version."
		self.message = "  SimCav only works with Python 3, but an older version was detected.\n  Please update to Python 3.\n"
class PipInstallError(Exception):
	def __init__(self, package):
		self.message = "Install the package '" + package + "' manually and try again."
class NotModuleError(Exception):
	def __init__(self, package):
		self.message = "Please install '" + package + "' before installing SimCav."
class WebFileError(Exception):
	def __init__(self, thefile):
		self.message = "Error: '" + thefile + "' not found'"
class HashError(Exception):
	def __init__(self):
		self.message = "Error hashing"
class UserCancel(Exception):
	def __init__(self):
		self.expression = "\nError: Cancelled by user."
		self.message = ""

if __name__ == '__main__':
	uninstall_window = TheCode('Uninstalling SimCav')