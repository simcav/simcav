#!/usr/bin/env python3

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

def download_file(url, folderfile):
	import urllib.request
	try:
		urllib.request.urlretrieve(url, folderfile)
		print("     Downloading " + os.path.basename(folderfile))
	except:
		raise

def writepath(user_site):
	with open("user_path.txt") as f:
		f.write(user_site)

try:	
	import sys
	
	guestOS = sys.platform
	
	# Var to control if pip has installed anything
	haveIinstalled = False

	# Require Python 3 to work
	if sys.version_info.major < 3:
		raise PythonVersionError
	else:
		print("OK:	Python version.")
	
	try:
		pip = __import__('pip')
		print("OK:	Pip")
	except ModuleNotFoundError:
		print("Warning: Pip module not found.")
		print("         Required dependencies won't be automatically installed.")
		
	try:
		from pip._internal import main as pipmain
	except:
		from pip import main as pipmain

	# List of modules required by SimCav
	simcav_modules = ['tkinter',  'numpy', 'requests', 'matplotlib']#, 'itertools', 'os', 'pickle', 'webbrowser'] 
	# The last ones, commented, are part of the standard python distribution.
	
	# List of modules required by the installer
	installation_modules = []
	if guestOS == 'win32':
		installation_modules.append('winshell')
	installed_modules = []
	# Check that modules exist / can be imported
	print("\nChecking required modules:")
	haveIinstalled = False
	for i in simcav_modules+installation_modules:
		try:
			__import__(i)
			print("OK:	" + i)
		except ModuleNotFoundError:
			print('x:	' + i)
			print('\n Module ' + i + ' not found, but is required for SimCav to work')

			useranswer = askuser(' Should I try to install it? (y/n): ')
			if useranswer:
				haveIinstalled = install(i)
				if haveIinstalled:
					if  i in installation_modules:
						installed_modules.append(i)
				else:
					raise PipInstallError(i)
			else:
				raise NotModuleError(i)
	print('\nAll dependencies satisfied! Continuing installation...\n')
					
	#===============================================
	# SIMCAV INSTALLATION
	import os
	#from pip._internal import locations as piploc
	
	# Locations
	#user_home = piploc.user_dir
	if guestOS == 'win32':
		import winshell
		user_home = winshell.folder("profile")
	else:
		user_home = os.path.expanduser('~')
		
	simcav_home = os.path.join(user_home, 'SimCav')
	
	print('Install location: ' + simcav_home)
	
	# Checking / creating SimCav folder
	if not os.path.exists(simcav_home):
		os.makedirs(simcav_home)
		user_proceed = True
	else:
		user_proceed = askuser('The install directory already exist. Overwrite? (y/n) ')
		
	if not user_proceed:
		raise UserCancel
		
	# Downloading files
	import requests
	#simcav_url = 'https://zenodo.org/record/1184130/files/simcav/simcav-v4.8.2.zip'
	#simcav_url = 'https://gitlab.com/simcav/simcav'
	#simcav_url = 'https://gitlab.com/simcav/simcav/-/archive/master/simcav-master.zip'
	simcav_api = 'https://gitlab.com/api/v4/projects/6789132/repository/'
	simcav_url = 'https://gitlab.com/simcav/simcav/raw/master/'
	
	# Required files
	simcav_files = ['simcav_main.py', 'simcav_CavityComputation.py', 'scrolledframe.py', 'simcav_ElementFeatures.py', 'simcav_abcd.py', 'simcav_simulator.py', 'tooltips.py', 'simcav_uninstaller.py', 'simcav_updater.py', 'misc.py']
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
	print('\n Creating subfolders...')
	# Icons folder
	try:
		icons_folder = os.path.join(simcav_home,'Icons')
		if not os.path.exists(icons_folder):
			os.makedirs(icons_folder)
	except:
		print("Error creating 'Icons' folder")
	# Saves folder
	try:
		saves_folder = os.path.join(simcav_home,'Saves')
		if not os.path.exists(saves_folder):
			os.makedirs(saves_folder)
	except:
		print("Error creating 'Saves' folder")
	
	#=================================
	#Downloading SimCav files
	print('\n Downloading modules...')
	for i in simcav_files:
		download_file(simcav_url + i, os.path.join(simcav_home, i))
	
	print('\n Downloading icons...')
	for i in simcav_icons:
		download_file(simcav_url + 'Icons/' + i, os.path.join(icons_folder, i))
		
	print('\n Downloading examples...')
	for i in simcav_saves:
		download_file(simcav_url + 'Saves/' + i, os.path.join(icons_folder, i))
	
	print('\n Downloading readmes...')
	for i in simcav_misc:
		download_file(simcav_url+i, os.path.join(simcav_home, i))
		
	print('\n Downloading manual...')
	if not 'manual.pdf' in os.listdir(simcav_home):
		download_file(simcav_url + 'Manual/manual.pdf', os.path.join(simcav_home, 'manual.pdf'))
	print('\n Files downloaded')
	#=================================================================
	# Create system links
	
	# Create desktop shortcut
	if guestOS == 'win32':
		# NOT WORKING YET
		
		def create_shortcut(thepath, thehome):
			print('\n Creating shortcut in ' + thepath)
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
		startmenu_path = os.path.join(winshell.start_menu(),'Programs','SimCav.lnk')
		create_shortcut(startmenu_path, simcav_home)
			
	elif guestOS == 'linux':
		desktop_path = os.path.join(os.path.join(user_home, 'Desktop'), 'SimCav.desktop')
		desktop_content = "[Desktop Entry]\nType=Application\nName=SimCav\nGenericName=Laser cavity simulator\nComment=Application for design and simulation of laser resonators\nExec=python " + os.path.join(simcav_home, 'simcav_main.py') + "\nIcon=" + os.path.join(icons_folder, 'logo-tg3.png') + "\nPath=" + simcav_home + "\nTerminal=false\nStartupNotify=false\nCategories=Education;Science"
		
		with open(desktop_path, 'w') as desktop_file:
			desktop_file.write(desktop_content)
		with open(os.path.join(user_home,'.local','share','applications','SimCav.desktop'), 'w') as desktop_file:
			desktop_file.write(desktop_content)
	
	print('\nInstallation finished!')
		
except Exception as inst:
	print('\nError: ' + type(inst).__name__)
	if type(inst).__name__ in ['PythonVersionError', 
								'NotModuleError',
								'PipInstallError',
								'UserCancel']:
		print(inst.message)
	else:
		raise
		
finally:
	print('\nCleaning installation files...')
	for i in installed_modules:
		uninstall(i)
	#os.remove(os.path.join(simcav_home,tar_file))
	input("\nQuitting. Press enter...")