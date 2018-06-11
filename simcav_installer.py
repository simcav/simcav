#!/usr/bin/env python3

# Defining exceptions
class PythonVersionError(Exception):
	def __init__(self):
		self.expression = "\nError: Incompatible Python version."
		self.message = "  SimCav only works with Python 3, but an older version was detected.\n  Please update to Python 3.\n"
class PipmainError(Exception):
	def __init__(self, package):
		self.expression = "\nError: Couldn't install from pip."
		self.message = "  Install the package " + package + "yourself and try again."

# Install with pip
def install(package):
	print("\n ---------------------\n Installing " + package)
	try:
		pipmain(['install', package, '--user', '--disable-pip-version-check'])
		return True
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
			print("Your response ('') was not one of the expected responses: (y/n)")

def download_file(url, folderfile):
	#print('Downloading ' + url.split('/')[-1])
	#wget.download(url, folder)
	request.urlretrieve(url, folderfile)

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
	installation_modules = ['wget', 'winshell']
	installed_modules = []
	# Check that modules exist / can be imported
	print("\nChecking required modules:")
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
				if haveIinstalled and  i in installation_modules:
					installed_modules.append(i)
				else:
					raise PipmainError
			else:
				print('\n Please install ' + i + ' before installing SimCav.')
				raise ModuleNotFoundError
	if haveIinstalled:
		print('All dependencies satisfied! Continuing installation...\n')
					
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
	else:
		print(simcav_home + 'already exist. Overwrite? (y/n)')
		
	# Downloading files
	import requests#, wget
	#simcav_url = 'https://zenodo.org/record/1184130/files/simcav/simcav-v4.8.2.zip'
	#simcav_url = 'https://gitlab.com/simcav/simcav'
	#simcav_url = 'https://gitlab.com/simcav/simcav/-/archive/master/simcav-master.zip'
	simcav_api = 'https://gitlab.com/api/v4/projects/6789132/repository/'
	simcav_url = 'https://gitlab.com/simcav/simcav/raw/master/'
	
	# Required files
	simcav_files = ['simcav_main.py', 'simcav_CavityComputation.py', 'scrolledframe.py', 'simcav_ElementFeatures.py', 'simcav_abcd.py', 'simcav_simulator.py', 'tooltips.py']
	simcav_icons = []
	simcav_misc = ['LICENSE', 'Disclaimer.txt', 'README.md']
	
	# Download zip and extract in simcav home
	r = requests.get(simcav_api+'tree?ref=master&per_page=100', params={'path':'Icons/'})
	for i in r.json():
		if not '.svg' in i['name']:
			simcav_icons.append(i['name'])
	#z = zipfile.ZipFile(io.BytesIO(r.content))
	#z.extractall(simcav_home)
	# Rename simcav folder
	#os.rename(os.path.join(user_home, 'simcav-master'), simcav_home)
	# for i in simcav_files:
	# 	r = requests.get(simcav_url+i)
	# 	with open(os.path.join(user_home, i), "wb") as myfile:
	# 		myfile.write(r.content)
	
	#=================================
	print('\n Creating subfolders...')
	# Icons folder
	try:
		icons_folder = os.path.join(simcav_home,'Icons')
		if not os.path.exists(icons_folder):
			os.makedirs(icons_folder)
	except:
		print('Error creating Icons folder')
	# Saves folder
	try:
		saves_folder = os.path.join(simcav_home,'Saves')
		if not os.path.exists(saves_folder):
			os.makedirs(saves_folder)
	except:
		print('Error creating Saves folder')
	
	#=================================
	#Downloading SimCav files
	print('\n Downloading modules...')
	for i in simcav_files:
		if not i in os.listdir(simcav_home):
			download_file(simcav_url + i, os.path.join(simcav_home,i))
	
	print('\n Downloading icons...')
	for i in simcav_icons:
		if not i in os.listdir(icons_folder):
			download_file(simcav_url + 'Icons/' + i, os.path.join(icons_folder,i))
	
	print('\n Downloading readmes...')
	for i in simcav_misc:
		if not i in os.listdir(simcav_home):
			download_file(simcav_url+i, os.path.join(simcav_home,i))
	print('\n Downloading manual...')
	if not 'manual.pdf' in os.listdir(simcav_home):
		download_file(simcav_url+'Manual/manual.pdf', os.path.join(simcav_home,'manual.pdf')
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
		desktop_path = os.path.join(os.path.join(user_home, 'Desktop'), 'SimCav2.desktop')
		desktop_content = "[Desktop Entry]\nType=Application\nName=SimCav\nGenericName=Laser cavity simulator\nComment=Application for design and simulation of laser resonators\nExec=python " + os.path.join(simcav_home, 'simcav_main.py') + "\nIcon=" + os.path.join(icons_folder, 'logo-tg3.png') + "\nPath=" + simcav_home + "\nTerminal=false\nStartupNotify=false\nCategories=Education;Science"
		
		with open(desktop_path, 'w') as desktop_file:
			desktop_file.write(desktop_content)
		with open(os.path.join(user_home,'.local','share','applications','SimCav.desktop'), 'w') as desktop_file:
			desktop_file.write(desktop_content)
		
		
except PythonVersionError as inst:
	print(inst.expression)
	print(inst.message)	
except Exception as inst:
	print(inst)
finally:
	print('\nCleaning installation files...')
	for i in installed_modules:
		uninstall(i)
	#os.remove(os.path.join(simcav_home,tar_file))
	input("Quitting. Press any key...")