# SimCav
### Laser cavity design and simulation

![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.594565.svg) 

Please visit the [website](https://simcav.gitlab.io/) for more information, downloads, screenshots... 

Simcav is a PC program to design and simulate laser cavities. 
It is able to calculate a stable cavity for some conditions given by the user, being this its best feature. 
It also provides common functionalities, such as drawing the cavities, calculate beam sizes and provide stability ranges.


## Why SimCav?
There are a number of different cavity simulators out there, but not so many are [free software](https://www.gnu.org/philosophy/free-sw.en.html). 
It is also difficult to find one that is cross-platform. Moreover, some of alternatives are already too old, and not working well (or at all) in newest Windows machines. 
SimCav aims to overcome these problems while offering some new features, such as the possibility to automatically find suitable configurations of the resonator.  

The main advantage of SimCav is that it can calculate a complex cavity for you. 
The user can introduce variations in the cavity parameters (such as distance between mirrors, or mirrors' curvature), 
set some conditions the cavity must fulfill and SimCav will find the cavity designs that match the given requirements.


## Installation
From version 4.8.3, an installer is provided for Linux and Windows. It will download SimCav files from the GitLab repository (master branch). All this files are saved in a folder called SimCav in the user directory. Uninstall is as easy as deleting this folder. Shortcut in the desktop and in the start menu are also created.

To install simply download the installer (simcav_installer.py).

- Windows: Double click the file 
(if the code opens means your python distributions is not registered, therefore register it or use the alternative mentioned below).

- Linux: [Grant the file execution rights](https://askubuntu.com/questions/35478/how-do-i-mark-a-file-as-executable-via-a-gui) and double click it.

Alternatively, run it manually:
```python
python3 simcav_installer.py
```

### Requeriments
Python 3 and pip are both required for the installer to work. This make SimCav installation truly lightweight (< 3 MB). Other required modules will be installed in the user environment using pip.



## Portable version

Self contained version of SimCav including the Python interpreter. Simply download and unzip at your preferred location. Then run the SimCav file.


## Running the source code
The main file is simcav_main.py. Of course the rest of the source files are also needed. 
You need Python 3.x installed in your computer. 
Due to changes in the Matplotlib libraries that are not backwards compatible, you need at least version 2.2 of Matplotlib. 


## Contact
Found a bug? Would like a new condition? Want to contribute? Want to share how much you love SimCav?
You can contact the SimCav team (aka me) via GitLab or send an email to simcav at protonmail dot com.
