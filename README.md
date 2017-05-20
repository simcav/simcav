# SimCav
Laser cavity simulation

[![DOI](https://zenodo.org/badge/90370020.svg)](https://zenodo.org/badge/latestdoi/90370020)

Simcav is a PC program to simulate laser cavities. It is able to calculate a stable cavity for some conditions given by the user, being this its best characteristic. It also provides common functionalities, such as drawing the cavities,calculate beam sizes and provide stability ranges.

## How to launch SimCav

* Windows:
Download the latest release. Simply download and unzip at your preferred location. Then run the SimCav shortcut. 
If you prefer you can run it from the source code.

* GNU/Linux:
There is no compiled version so far, you need to run the source code.

* Mac:
Same as in GNU/Linux... maybe!

## Runing the source code
The main file is simcav4_7_GUI. Of course the rest of the source files are also needed.
You need Python 3.x installed in your computer.
Due to changes in the Matplotlib libraries that are not backwards compatible, you need at least version 1.5 of Matplotlib.
The version of the different modules are described in the Manual.

# Why SimCav?
There are a number of different cavity simulators out there, but not so many are [free software](https://www.gnu.org/philosophy/free-sw.en.html). It is also difficult to find one that is cross-platform. Some of the programs are already too old, and not working well in newest Windows machines. SimCav aims to overcome these problems while offering some new features.

The main advantage of SimCav is that it can calculate a complex cavity for you. The user can introduce variations in the cavity parameters (such as distance between mirrors, or mirrors' curvature), set some conditions the cavity must fulfill and SimCav will find the cavity designs that match the given requirements.

# Contact
Found a bug? Would like a new condition? Want to contribute? Want to share how much you love SimCav?
You can contact the SimCav team (aka me) via GitHub or send an email to simcav at protonmail dot com.
