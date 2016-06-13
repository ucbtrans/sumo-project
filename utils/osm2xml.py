'''
from subprocess import call
from Tkinter import Tk
import tkFileDialog

print tkFileDialog.askopenfilename(**sdefaultextension)
'''

import Tkinter
import pdb
import os
from subprocess import call
from tkFileDialog import *

root = Tkinter.Tk()
root.withdraw()


file_path = askopenfilename()
file_name = str(os.path.basename(file_path)) 


call(["netconvert","--osm-files", file_name, "-o","map.net.xml"])
call(["netconvert","--osm-files", file_name, "--plain-output","map"])
call(["polyconvert","--net-file","map.net.xml","--osm-files",file_name,"--type-file","typemap.xml","-o","map.poly.xml"])

dir_name= raw_input('Enter folder name: ')
dir_name = str(dir_name)

call(["mkdir",dir_name])

#outputs from --plain-output file
call(["mv","map.con.xml",dir_name])
call(["mv","map.edg.xml",dir_name])
call(["mv","map.nod.xml",dir_name])
call(["mv","map.tll.xml",dir_name])
call(["mv","map.typ.xml",dir_name])


call(["mv","map.net.xml",dir_name])
call(["mv","map.poly.xml",dir_name])
call(["cp","typemap.xml",dir_name])
call(["cp","map.osm",dir_name])
call(["cp","testmap.sumocfg",dir_name])
os.chdir(os.getcwd()+"\\"+dir_name)

print "-------------------------------------------------------------------------------------------"
print "Find the python script 'randomTrips.py' in your directory (should be under sumo-0.25.0/tools/trip)"
print "-------------------------------------------------------------------------------------------"


py_path = askopenfilename()
py_path = str(py_path)

call(["python",py_path,"-n","map.net.xml","-e","100","-l"])
call(["python",py_path,"-n","map.net.xml","-r","map.rou.xml","-e","100","-l"])

print "-------------------------------------------------------------------------------------------"
print "In the testmap.sumocfg file, rewrite the net-file, route-file and additional-file values accordingly to the new files generated and continue."
print "-------------------------------------------------------------------------------------------"

raw_input("After this, press enter to continue...")
call(["sumo-gui","testmap.sumocfg"])










