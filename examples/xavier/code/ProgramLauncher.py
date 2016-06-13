import os
import time
import xml.etree.ElementTree as ET

if __name__ == "__main__":

	baseURL = os.path.abspath(os.path.join(os.getcwd(),os.pardir)) + '\\MyProgram\\ExperimentConFile\\'

	tree = ET.parse(baseURL + 'Experiments_File.xml')
	root = tree.getroot()
	ListOfExperimentFiles = []

	for child in root:
		if(child.tag == 'Experiment'):
			ListOfExperimentFiles.append(child.text)


	for exp in ListOfExperimentFiles:
		print 'Starting: ' + exp
		os.system("python runner2.py \"" +baseURL + exp + "\"")
		print 'Ending: ' + exp