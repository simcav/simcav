import sys, os, requests

# Python version
def pythoncheck():
    # Require Python 3 to work
    if sys.version_info.major < 3:
        raise PythonVersionError
        return 1
    else:
        print("OK:	Python version.")
        return 0

# Import pip installer
def pipimport():
    try:
        pip = __import__('pip')
        print("OK:	Pip")
    except ModuleNotFoundError:
        return 1
    try:
        from pip._internal import main as pipmain
        return 0
    except:
        from pip import main as pipmain
        return 0

# SimCav
def list_simcav_modules():
    simcav_files = ['simcav_main.py', 'simcav_CavityComputation.py', 'scrolledframe.py', 'simcav_ElementFeatures.py', 'simcav_abcd.py', 'simcav_simulator.py', 'tooltips.py', 'simcav_uninstaller.py']#, 'simcav_updater.py', 'misc.py']
    return simcav_files

def list_simcav_misc():
    simcav_misc = ['LICENSE', 'Disclaimer.txt', 'README.md', 'CHANGELOG']
    return simcav_misc
    
def list_simcav_icons():
    simcav_icons = []
    simcav_api = get_api()
    # Get icons list from repo
    r = requests.get(simcav_api+'tree?ref=master&per_page=100', params={'path':'Icons/'})
    for i in r.json():
        if not '.svg' in i['name']:
            simcav_icons.append(i['name'])
    return simcav_icons
    
def list_simcav_saves():
    simcav_saves = []
    simcav_api = get_api()
    # Get icons list from repo
    r = requests.get(simcav_api+'tree?ref=master&per_page=100', params={'path':'Saves/'})
    for i in r.json():
        simcav_saves.append(i['name'])
    return simcav_saves
            
def gethomepath(theguestOS):
    # Get paths
    if theguestOS == 'win32':
        user_home = winshell.folder("profile")
    else:
        user_home = os.path.expanduser('~')
    simcav_home = os.path.join(user_home, 'SimCav')
    return simcav_home

# URL functions
def get_api():
    api_url = 'https://gitlab.com/api/v4/projects/6789132/repository/'
    return api_url

def get_repo():
    repo_url = 'https://gitlab.com/simcav/simcav/raw/master/'
    return repo_url




# DOWNLOADS
# Download a file
def download_manual(simcav_home):
    import urllib.request
    simcav_url = get_repo()
    url = simcav_url + 'Manual/manual.pdf'
    folderfile = os.path.join(simcav_home, 'manual.pdf')
    try:
        urllib.request.urlretrieve(url, folderfile)
        return 0
    except:
        raise
        return 1

def download_file(thefile, thefolder):
    import urllib.request
    simcav_url = get_repo()
    url = simcav_url + thefile
    folderfile = os.path.join(thefolder, thefile)
    try:
        print("     Downloading " + thefile)
        urllib.request.urlretrieve(url, folderfile)
        return 0
    except:
        raise
        return 1

def download_group(onegroup, group_folder):
    for i in onegroup:
        download_error = download_file(i, group_folder)
        if download_error:
            print('Error downloading ' + i)
            raise
            return 1
    return 0
# Download all files
def download_simcav(simcav_home):
    #Downloading SimCav files
    print('\n Downloading modules...')
    simcav_modules = list_simcav_modules()
    download_group(simcav_modules, simcav_home)

    print('\n Downloading icons...')
    simcav_icons = list_simcav_icons()
    download_group(simcav_icons, os.path.join(simcav_home,'Icons'))
        
    # print('\n Downloading examples...')
    # simcav_saves = list_simcav_saves()
    # download_group(simcav_saves, os.path.join(simcav_home,'Saves'))
    
    print('\n Downloading other files...')
    simcav_misc = list_simcav_misc()
    download_group(simcav_misc, simcav_home)
        
    print('\n Downloading manual...')
    download_error = download_manual(simcav_home)
    print('\n Files downloaded')



# Installing functions
def guestOS():
    return sys.platform
    
def pipinstall(package):
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
        
def pipuninstall(package):
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
class UserCancel(Exception):
	def __init__(self):
		self.expression = "\nError: Cancelled by user."
		self.message = ""


pythoncheck()
pipimport()

if guestOS() == 'win32':
    try:
        import winshell
    except:
        haveIinstalled = pipisntall(winshell)
        if haveIinstalled:
            import winshell
        else:
            raise