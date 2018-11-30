#!/usr/bin/env python3
import os, requests, misc
import tkinter as tk
import shutil

class TheCode():
    def __init__(self, title=None):
        self.Tk = tk.Tk()
        self.Tk.title(title)
        # Kill process when click on window close button
        self.Tk.protocol("WM_DELETE_WINDOW", self.killing_root)

        gui_app = misc.Display(self.Tk)
        self.gui_app = gui_app
        self.func_update(self.gui_app)
        self.Tk.mainloop()
    
    def killing_root(self):
        self.Tk.destroy()
    
    def func_update(self, gui_app):
        try:
            # Web urls
            simcav_api = gui_app.get_api()
            simcav_url = gui_app.get_repo()

            simcav_home = os.path.dirname(os.path.realpath(__file__))
            gui_app.printcmd("Updating SimCav in " + simcav_home)
            
            # DELETE OLD FILES
            simcav_old_files = ['simcav_main.py', 'simcav_CavityComputation.py', 'scrolledframe.py', 'simcav_ElementFeatures.py', 'simcav_abcd.py', 'simcav_simulator.py', 'tooltips.py', 'simcav_uninstaller.py', 'manual.pdf', 'CHANGELOG', 'README.md', 'LICENSE', 'Disclaimer.txt']
            gui_app.printcmd("Deleting old files...")
            for file in simcav_old_files:
                todelete = os.path.join(simcav_home, file)
                try:
                    os.remove(todelete)
                except FileNotFoundError:
                    pass
            # Delete old icons
            todelete = os.path.join(simcav_home, "Icons")
            if os.path.exists(todelete):
                shutil.rmtree(todelete, ignore_errors=True)
            # Delete pycache
            todelete = os.path.join(simcav_home, "__pycache__")
            if os.path.exists(todelete):
                shutil.rmtree(todelete, ignore_errors=True)

            # CREATING SUBFOLDERS
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

            # DOWNLOAD THE NEW FILES
            gui_app.printcmd("Downloading new files...")
            gui_app.download_simcav(simcav_home)
            gui_app.printcmd("Done!")
            
            # Deleting update files
            # This is so if there is any issue with the download of the new files
            # it is still possible to run the updater again.
            old_updater_files = ['simcav_updater.py', 'misc.py']
            for file in old_updater_files:
                todelete = os.path.join(simcav_home, file)
                try:
                    os.remove(todelete)
                except FileNotFoundError:
                    pass
        except:
            gui_app.printcmd("Error!")
            raise
        finally:
            gui_app.printcmd('You may close this window.')

def func_main():
    uninstall_window = TheCode('Updating SimCav')

if __name__ == '__main__':
	func_main()