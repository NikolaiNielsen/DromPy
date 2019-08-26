# Drom.py - a Drom Creator
This program uses python and pdflatex to create a print-friendly Drom for the
RacerBohr board game.

Whenever a new hex is placed, a Drom.tex file is created and compiled with 
pdflatex. 

### Requirements
Python 3+ with Numpy installed.  
pdflatex - must be accessible via the subprocess module.

Currently only tested on Debian

### Notes
It is advised to run this script on a UNIX system, as these allows open files
to be updated. Then you can run the script and have an automatically updating
pdf displayed at the same time.
