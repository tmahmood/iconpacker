import sys
import os
from string import Template

try:
	import gtk
  	import gtk.glade
 	import pygtk
  	pygtk.require("2.0")
except:
	sys.exit(1)


if __name__=="__main__":
	print "Here I am!"
