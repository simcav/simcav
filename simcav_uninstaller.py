#!/usr/bin/env python3

# Defining exceptions
class PythonVersionError(Exception):
	def __init__(self):
		self.expression = "\nError: Incompatible Python version."
		self.message = "  SimCav only works with Python 3, but an older version was detected.\n  Please update to Python 3.\n"
class UserCancel(Exception):
	def __init__(self):
		self.expression = "\nError: Cancelled by user."
		self.message = ""
		
# Install with pip
def install(package):
	print("\n ---------------------\n Installing " + package)
	try:
		pipcode = pipmain(['install', package, '--user', '--disable-pip-version-check', '--no-warn-conflicts'])
		if not pipcode:
			return True
		else:
			return False
	except Exception as inst:
		print(inst)
		print("Error")
		return False
# Uninstall with pip
def uninstall(package):
	try:
		pipmain(['uninstall', package, '-y', '--disable-pip-version-check'])
		return True
	except Exception as inst:
		print(inst)
		print("Error")
		return False

# Ask user input
def askuser(message):
	while True:
		useranswer = input(message)
		if useranswer.lower() == 'y' or useranswer.lower() == 'yes':
			return True
		elif useranswer.lower() == 'n' or useranswer.lower() == 'no':
			return False
		else:
			print("Your response was not one of the expected responses: (y/n)")

try:
	import sys, os
	
	# Require Python 3 to work
	if sys.version_info.major < 3:
		raise PythonVersionError
	else:
		print("OK:	Python version.")
		
	# Check operating system
	guestOS = sys.platform
	
	# Windows uninstall will require Winshell
	haveIinstalled = False
	if guestOS == 'win32':
		try:
			import winshell
		except:
			# Require Pip
			try:
				pip = __import__('pip')
				print("OK:	Pip")
			except ModuleNotFoundError:
				print("Warning: Pip module not found.")
				print("         Pip is required to proceed with the uninstall.")
			# Import pip installer
			try:
				from pip._internal import main as pipmain
			except:
				from pip import main as pipmain
			haveIinstalled = install(winshell)
			import winshell
	
	# Get paths
	if guestOS == 'win32':
		import winshell
		user_home = winshell.folder("profile")
		desktop_path = os.path.join(winshell.desktop(), 'SimCav.lnk')
		startmenu_path = os.path.join(winshell.start_menu(), 'SimCav.lnk')
	else:
		user_home = os.path.expanduser('~')
		desktop_path = os.path.join(user_home, 'Desktop', 'SimCav.desktop')
		startmenu_path = os.path.join(user_home,'.local','share','applications','SimCav.desktop')
	simcav_home = os.path.join(user_home, 'SimCav')
	
	# Removing SimCav folder
	print("This will completely remove SimCav, including 'Saves' folder.")
	print("Path to delete: " + simcav_home)
	user_asnwer = askuser('Continue? (y/n) ')
	
	if not user_asnwer:
		raise UserCancel
		
	import shutil
	print('Deleting files...')
	for i in os.listdir(simcav_home):
		todelete = os.path.join(simcav_home, i)
		if os.path.isfile(todelete):
			print('    Removing ' + i)
			print(os.path.realpath(todelete))
			os.remove(todelete)
		elif os.path.isdir(todelete):
			print("    Removing folder '" + i + "'")
			print(os.path.realpath(todelete))
			shutil.rmtree(todelete)
	# Can't delete main folder while using it!
	#shutil.rmtree(simcav_home)
		
	# Removing shortcuts
	print('Deleting shortcuts')
	print(    'Removing ' + desktop_path)
	os.remove(desktop_path)
	print(    'Removing ' + startmenu_path)
	os.remove(startmenu_path)
	
	print('\nUninstall finished!')
		

except Exception as inst:
	print('\nError: ' + type(inst).__name__)
	if type(inst).__name__ in ['PythonVersionError', 
								'NotModuleError',
								'PipInstallError',
								'UserCancel']:
		print(inst.message)
	else:
		print(inst)
    
finally:
    if haveIinstalled:
        uninstall(winshell)
    
    input("\nQuitting. Press enter...")
    