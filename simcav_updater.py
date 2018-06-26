#!/usr/bin/env python3
import os, requests, misc
import tkinter as tk

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
            gui_app.download_simcav(simcav_home)
            gui_app.printcmd("Done!")
        except:
            gui_app.printcmd("Error!")
            raise
        finally:
            gui_app.printcmd('You may close this window.')

def func_main():
    uninstall_window = TheCode('Updating SimCav')

if __name__ == '__main__':
	func_main()