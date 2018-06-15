#!/usr/bin/env python3
import sys, os, misc
import tkinter as tk

class TheCode():
	def __init__(self, title=None):
		self.Tk = tk.Tk()
		self.Tk.title(title)
		# Kill process when click on window close button
		self.Tk.protocol("WM_DELETE_WINDOW", self.killing_root)

		gui_app = misc.Display(self.Tk)
		self.gui_app = gui_app
		self.func_main(self.gui_app)
		self.Tk.mainloop()

	def killing_root(self):
		self.Tk.destroy()

	def func_main(self, gui_app):
		try:
			# Require Python 3 to work
			pythonOK = self.gui_app.pythoncheck()
				
			# Check operating system
			guestOS = sys.platform
			
			# Windows uninstall will require Winshell
			if guestOS == 'win32':
				winshell_error = gui_app.install_winshell()
			# Get paths
			if guestOS == 'win32':
				user_home = winshell.folder("profile")
				desktop_path = os.path.join(winshell.desktop(), 'SimCav.lnk')
				startmenu_path = os.path.join(winshell.start_menu(), 'Programs', 'SimCav.lnk')
			else:
				user_home = os.path.expanduser('~')
				desktop_path = os.path.join(user_home, 'Desktop', 'SimCav.desktop')
				startmenu_path = os.path.join(user_home,'.local','share','applications','SimCav.desktop')
			simcav_home = os.path.join(user_home, 'SimCav')
			
			# Removing SimCav folder
			gui_app.printcmd("This will completely remove SimCav, including 'Saves' folder.")
			gui_app.printcmd("Path to delete: " + simcav_home)
			user_asnwer = gui_app.askuserbox('Continue?')
			
			if not user_asnwer:
				raise misc.UserCancel
				
			import shutil
			gui_app.printcmd('Deleting files...')
			for i in os.listdir(simcav_home):
				todelete = os.path.join(simcav_home, i)
				if os.path.isfile(todelete):
					gui_app.printcmd('    Removing ' + i)
					gui_app.printcmd(os.path.realpath(todelete))
					os.remove(todelete)
				elif os.path.isdir(todelete):
					gui_app.printcmd("    Removing folder '" + i + "'")
					gui_app.printcmd(os.path.realpath(todelete))
					shutil.rmtree(todelete)
			# Can't delete main folder while using it!
			#shutil.rmtree(simcav_home)
				
			# Removing shortcuts
			gui_app.printcmd('Deleting shortcuts')
			gui_app.printcmd(    'Removing ' + desktop_path)
			os.remove(desktop_path)
			gui_app.printcmd(    'Removing ' + startmenu_path)
			os.remove(startmenu_path)
			
			gui_app.printcmd('\nUninstall finished!')
				

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

if __name__ == '__main__':
	uninstall_window = TheCode('Uninstalling SimCav')