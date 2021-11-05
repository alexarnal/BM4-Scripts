#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 30 18:05:39 2021

@author: latente
"""
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from scipy.stats import multivariate_normal, gaussian_kde
from matplotlib import cm
from matplotlib.colors import ListedColormap
from glob import glob

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
    return coords, np.array(viewBox[1].split(' '), dtype='float')

def getProjectDetails(path):
    myDictionary = {}
    file = open(path,"r")
    for line in file:
        fields = [x.replace(' ','').replace('\n','') for x in line.split(",")]
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

#Directory to Cell Body Data Set Up
dataDir='../cells/raw/'
outDir ='../cells/isopleths/'

print('Writing to ../cells/summary.txt')
#Set up report
f = open("../cells/summary.txt", "w")
f.write("Summary report for cell bodies")
f.close()

#Generate summary file for cell bodies
ids = len(markers)*len(cases)
filled= 0
empty = 0
for marker in markers:
    for case in cases:
        for level in levels:
             for i in range(ids):#['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18']:

                fileName = '%s%s_%s_lvl%s_%s-01.svg'%(dataDir,case,marker,level,i+1)
                try:
                    coordinates, viewBox = getCoordsFromSVG(fileName)
                except: continue
                
                f = open("../cells/summary.txt", "a")
                f.write('\n\nFound: %s_%s_lvl%s_%s'%(case,marker,level,i+1))
                f.write('\tNumber of Cells: %d'%len(coordinates))
                f.close()
                
                if len(coordinates)==0: empty+=1
                else: filled+=1

f = open("../cells/summary.txt", "a")
f.write('\n\nThere is a total of %d cell body files:\n\t%d filled\n\t%d empty'%(filled+empty, filled, empty))
f.write('\n\nEnd of report.')
f.close()  

print('There is a total of %d cell body files:\n%d filled\n%d empty'%(filled+empty, filled, empty))
print('End of report.\n') 
