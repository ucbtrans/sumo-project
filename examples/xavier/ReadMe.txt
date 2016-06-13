In the "Sumo Projects" folder, all of the files needed to run platooning simulations can be found.



Launching an experiment:

-Save the user settings in an xml file in the "code/ExperimentConFile" folder
-Update the "Experiments_File.xml" file to include the name of the xml created in the first step - this file is located in the folder
"code/ExperimentConFile"
-In the command prompt, go to the "code" folder and then run the "ProgramLauncher.py" in python



Decription of the folders in the "Sumo Projects" folder:

"Huntington Colorado" - This folder contains all of the files relating to the huntington-colorado
test site. The file tited "HuntingtonColorado - SiteInformation" is a file with information on the
network which was kindly provided by the UC Berkeley PATH department. There are 8 different versions
of the site as there were many itterations during the construction of the network. There is a file 
titled "Version log" which gives a brief description on each version. Version 6 is the main file for
tests on the whole network and Version 7 is the main file for tests on the first junction.

"code" - This folder contains all of the code needed to run simulations in SUMO. Within this folder
can be found two more folders: "ExperimentConFile" which contains the user configuration files to run experiments
and "Tests/Experiments" which is were the data from the experiments will be saved to - do not change the name of
these folders. There are also many python files: the constants file is used to load the user settings from
the user configuration file, the MyClasses contains all of the code used to implement platooning. The "ProgramLauncher"
is used to run a series of different simulations which are refered in the experiment configuration file in the
"ExperimentsConFile". The "runner2" file is used to establish the connection between the external program and the
SUMO simulator. 

"Practice" - Simple practice network in SUMO

"Map Data" - Simple example of the openmap software

"SimpleIntersection" - Version 1 of a simple intersection network in SUMO

"SimpleIntersection2" - Version 2 of a simple intersection network in SUMO

"SimpleIntersection3" - Version 3 of a simple intersection network in SUMO

"SimpleIntersection4" - Version 4 of a simple intersection network in SUMO

"SimpleIntersection5" - Version 5 of a simple intersection network in SUMO

"Test Network"- Version 1 of a simple straight road network in SUMO

"Test Network2"- Version 2 of a simple straight road network in SUMO
