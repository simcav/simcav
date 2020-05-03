#!/usr/bin/env python3
import sys, os, requests, hashlib
import tkinter as tk
from tkinter import messagebox

# Add user site to path, just in case.
import site

sys.path.insert(0, site.USER_SITE)


# Console GUI
class Display(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.output = tk.Text(self, width=100, height=15, background='black',
                              fg='white')
        self.output.pack(side=tk.LEFT, fill='both', expand=1)

        self.scrollbar = tk.Scrollbar(self, orient="vertical",
                                      command=self.output.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        self.output['yscrollcommand'] = self.scrollbar.set

        self.pythoncheck()
        self.pipimport()

        self.configure(background='black')
        self.pack(fill='both', expand=1)
        # self.wait_window()
        # self.thecode = thecode(self)
        # self.thecode.func_install(self)

    def printcmd(self, txt):
        self.output.insert(tk.END, str(txt))
        self.output.insert(tk.END, '\n')
        self.output.see(tk.END)
        self.update_idletasks()

    def askuserbox(self, message):
        askbox = messagebox.askyesno('Question', message)
        return askbox

    def call_close(self, parent):
        messagebox.showinfo('quit', "Quitting.")
        parent.killing_root()

    # Check Python version
    def pythoncheck(self):
        # Require Python 3 to work
        if sys.version_info.major < 3:
            raise PythonVersionError
            return 1
        else:
            self.printcmd("OK:	Python version.")
            return 0

    # Import pip installer
    def pipimport(self):
        try:
            pip = __import__('pip')
            self.printcmd("OK:	Pip")
        except NotModuleError:
            return 1
        try:
            from pip._internal import main as pipmain
        except:
            from pip import main as pipmain
        self.pipmain = pipmain
        return 0


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
        if 'win' in self.guestOS():
            self.install_winshell()

        # Find path
        updateFilePath = os.path.realpath(__file__)
        updatePath = updateFilePath.replace('updater.py', '')

        self.download_simcav(updatePath)

        self.gui_app.printcmd('\n SimCav updated!')
        self.gui_app.printcmd('\n You may close this window')

    # SimCav
    def list_simcav_modules(self):
        simcav_files = ['gui.ui', 'load_icons.py', 'main.py', 'matrixWidget.py',
                        'matrixWidget.ui', 'simcav_ABCD.py',
                        'simcav_conditions.py', 'simcav_designer.py',
                        'simcav_elementFeatures.py', 'simcav_physics.py',
                        'simcav_statusBar.py', 'simcav_updates.py',
                        'style_designerSolutions.css', 'style_main.css',
                        'updater.py']
        return simcav_files

    def list_simcav_misc(self):
        simcav_misc = ['LICENSE', 'Disclaimer.txt', 'README.md', 'CHANGELOG']
        return simcav_misc

    def list_simcav_icons(self):
        simcav_icons = []
        simcav_api = self.get_api()
        # Get icons list from repo
        r = requests.get(simcav_api + 'tree?ref=future&per_page=100',
                         params={'path': 'Icons/'})
        for i in r.json():
            if not '.svg' in i['name']:
                simcav_icons.append(i['name'])
        return simcav_icons

    def list_simcav_saves(self):
        simcav_saves = []
        simcav_api = self.get_api()
        # Get icons list from repo
        r = requests.get(simcav_api + 'tree?ref=future&per_page=100',
                         params={'path': 'Saves/'})
        for i in r.json():
            simcav_saves.append(i['name'])
        return simcav_saves

    def gethomepath(self, theguestOS):
        # Get paths
        if theguestOS == 'win32':
            user_home = self.winshell.folder("profile")
        else:
            user_home = os.path.expanduser('~')
        simcav_home = os.path.join(user_home, 'SimCav')
        return simcav_home

    # URL functions
    def get_api(self):
        api_url = 'https://gitlab.com/api/v4/projects/6789132/repository/'
        return api_url

    def get_repo(self):
        repo_url = 'https://gitlab.com/simcav/simcav/raw/future/'
        return repo_url

    # DOWNLOADS
    # Download a file
    def download_manual(self, simcav_home):
        simcav_url = self.get_repo()
        url = simcav_url + 'Manual/manual.pdf'
        folder_file = os.path.join(simcav_home, 'manual.pdf')

        if self.compare_hash(folder_file, url):
            self.gui_app.printcmd("     Up-to-date: manual.pdf")
            return 0

        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise RequestsConnectionError(err)
        except requests.exceptions.ConnectionError as err:
            raise RequestsConnectionError(err)
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)

        # On successful connection save file
        with open(folder_file, 'wb') as local_file:
            local_file.write(r.content)

    def compare_hash(self, local_file, remote_file):
        # Compares hashes of two files
        #   Returns 1 if hashes are equal.
        #   Returns 0 if hashes are different or cant compare.

        # Local file hash
        if os.path.isfile(local_file):
            hash1 = self.get_hash(local_file)
        else:
            return 0

        # Web file hash
        try:
            r = requests.get(remote_file)
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.gui_app.printcmd(
                "\nError: file " + remote_file + " not found in the repository.")
            return 1
        hash2 = hashlib.md5(r.content).hexdigest()
        # Equal hash -> 1
        if hash1 == hash2:
            return 1
        else:
            return 0

    def download_file(self, thefile, thefolder):
        simcav_url = self.get_repo()
        if os.path.basename(thefolder) in ['Icons', 'Saves']:
            url = simcav_url + os.path.basename(thefolder) + '/' + thefile
        else:
            url = simcav_url + thefile
        folder_file = os.path.join(thefolder, thefile)

        # Compare hash, if different, download
        try:
            local_file = os.path.join(thefolder, thefile)
            remote_file = url

            if self.compare_hash(local_file, remote_file):
                self.gui_app.printcmd("     Up-to-date: " + thefile)
                return 0
        except:
            raise HashError()

        self.gui_app.printcmd("     Downloading " + thefile)
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise RequestsConnectionError(err)
        except requests.exceptions.ConnectionError as err:
            raise RequestsConnectionError(err)
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)

        # On successful connection save file
        with open(folder_file, 'wb') as local_file:
            local_file.write(r.content)
        return 0

    def download_group(self, onegroup, group_folder):
        for i in onegroup:
            download_error = self.download_file(i, group_folder)
            if download_error:
                self.gui_app.printcmd('Error downloading ' + i)
                raise
                return 1
        return 0

    # Download all files
    def download_simcav(self, simcav_home):
        # Downloading SimCav files
        self.gui_app.printcmd('\n Downloading modules...')
        simcav_modules = self.list_simcav_modules()
        self.download_group(simcav_modules, simcav_home)

        self.gui_app.printcmd('\n Downloading icons...')
        simcav_icons = self.list_simcav_icons()
        self.download_group(simcav_icons, os.path.join(simcav_home, 'Icons'))

        self.gui_app.printcmd('\n Downloading examples...')
        simcav_saves = self.list_simcav_saves()
        self.download_group(simcav_saves, os.path.join(simcav_home, 'Saves'))

        self.gui_app.printcmd('\n Downloading other files...')
        simcav_misc = self.list_simcav_misc()
        self.download_group(simcav_misc, simcav_home)

        self.gui_app.printcmd('\n Downloading manual...')
        download_error = self.download_manual(simcav_home)
        self.gui_app.printcmd('\n Files downloaded')

    def get_hash(self, the_file):
        hasher = hashlib.md5()
        with open(the_file, 'rb') as a_file:
            buf = a_file.read()
            hasher.update(buf)
        return hasher.hexdigest()

    # Installing functions
    def guestOS(self):
        return sys.platform

    def pipinstall(self, package):
        self.gui_app.printcmd(
            "\n ---------------------\n Installing " + package)
        try:
            try:
                pipcode = self.pipmain(['install', package, '--user',
                                        '--disable-pip-version-check',
                                        '--no-warn-conflicts'])
            except:
                # Older versions of pip may lack no-conflicts flag
                pipcode = self.pipmain(['install', package, '--user',
                                        '--disable-pip-version-check'])
            if not pipcode:
                return True
            else:
                return False
        except Exception as inst:
            self.gui_app.printcmd(inst)
            self.gui_app.printcmd("Error")
            return False

    def pipuninstall(self, package):
        try:
            self.pipmain(
                ['uninstall', package, '-y', '--disable-pip-version-check'])
            return True
        except Exception as inst:
            self.gui_app.printcmd(inst)
            self.gui_app.printcmd("Error")
            return False

    def install_winshell(self):
        try:
            import winshell
        except:
            self.gui_app.printcmd("x: Winshell    --    Installing")
            self.pipimport()
            haveIinstalled = self.pipinstall('winshell')
            if haveIinstalled:
                import winshell
            else:
                self.gui_app.printcmd("Error: Couldn't install Winshell")
                raise
                return 1
        else:
            self.winshell = winshell
            self.gui_app.printcmd("OK:     Winshell")
            return 0


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


class RequestsConnectionError(Exception):
    def __init__(self):
        self.message = 'Connection error.'


class RequestsOtherError(Exception):
    def __init__(self):
        self.message = 'Something went wrong.'


if __name__ == '__main__':
    update_window = TheCode('Updating SimCav')
