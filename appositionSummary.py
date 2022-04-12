#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 30 18:05:39 2021

@author: latente
"""
import re
import numpy as np

def getCoordsFromSVG(fileName):
    file = open(fileName,'r')
    fileContent = file.readline()
    file.close()
    fileContent = fileContent.split('>')
    X=[]
    Y=[]
    viewBox = 0
    for i,line in enumerate(fileContent): 
        coord = 0
        if 'viewBox=' in line:
            viewBox = re.search('viewBox="(.*)"', line)
        if 'circle' in line:
            x = re.search('cx="(.*)" cy', line)
            y = re.search('cy="(.*)" r', line)
            coord = [x.group(1),y.group(1)]
        else: continue
        X.append(float(coord[0]))
        Y.append(-float(coord[1]))
    coords = np.vstack((np.array(X), np.array(Y))).T
    return coords, np.array(viewBox.group(1).split(' '), dtype='float')

def getProjectDetails(path):
    myDictionary = {}
    file = open(path,"r")
    for line in file:
        fields = [x.replace('\n','') for x in line.split(",")] #x.replace(' ','')
        myDictionary[fields[0]]=fields[1:]
    file.close()
    print("\nProject Details:")
    for i in myDictionary:
        print("  ",i, myDictionary[i])
    return myDictionary

print('\nGenerating Summary')

#Project's Experimental Set Up
projectDetails = getProjectDetails("projectDetails.csv")
levels = projectDetails['levels']
markers = projectDetails['markers']
cases = projectDetails['cases']
#Directory to Apposition Data Set Up
dataDir='../appositions/raw/'

print('Writing to ../appositions/summary.txt')
#Set up report
f = open("../appositions/summary.txt", "w")
f.write("Summary report for appositions")
f.close()

#Generate summary file for appositions
ids = len(markers)*len(cases)
filled= 0
empty = 0
for marker in markers:
    for case in cases:
        for level in levels:
            for i in range(ids):
                fileName = '%s%s_%s_lvl%s_%s-01.svg'%(dataDir,case,marker,level,i+1)
                try:
                    coordinates, viewBox = getCoordsFromSVG(fileName)
                except Exception as e: 
                    #print(e)
                    continue
                
                f = open("../appositions/summary.txt", "a")
                f.write('\n\nFound: %s_%s_lvl%s_%s'%(case,marker,level,i+1))
                f.write('\t\tNumber of appositions: %d'%len(coordinates))
                f.close()
                
                if len(coordinates)==0: empty+=1
                else: filled+=1

f = open("../appositions/summary.txt", "a")
f.write('\n\nThere is a total of %d appositions files:\n\t%d filled\n\t%d empty'%(filled+empty, filled, empty))
f.write('\n\nEnd of report.')
f.close()  

print('There is a total of %d appositions files:\n%d filled\n%d empty'%(filled+empty, filled, empty))
print('End of report.\n') 