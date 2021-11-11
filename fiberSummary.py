#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 30 18:05:39 2021

@author: latente
"""
import numpy as np
import matplotlib.pyplot as plt

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

#Directory to Fiber Data Set Up
dataDir='../fibers/raw/'
outDir ='../fibers/isopleths/'

print('Writing to ../fibers/summary.txt')
#Set up report
f = open("../fibers/summary.txt", "w")
f.write("Summary report for fibers")
f.close()

#Generate density files for each SVG file
ids = len(markers)*len(cases)
filled= 0
empty = 0
for marker in markers:
    for case in cases:
        for level in levels:
             for i in range(ids):

                fileName = '%s%s_%s_lvl%s_%s.png'%(dataDir,case,marker,level,i+1)
                try:
                    im = (plt.imread(fileName)[:,:,0]<1).astype(np.float32)
                except: continue
                
                f = open("../fibers/summary.txt", "a")
                f.write('\n\nFound: %s_%s_lvl%s_%s'%(case,marker,level,i+1))
                f.write('\t\tNumber of Fiber Pixels: %d'%np.sum(im))
                f.close()

                if np.sum(im)==0: empty+=1
                else: filled+=1

f = open("../fibers/summary.txt", "a")
f.write('\n\nThere is a total of %d fiber files:\n\t%d filled\n\t%d empty'%(filled+empty, filled, empty))
f.write('\n\nEnd of report.')
f.close()  

print('There is a total of %d fiber files:\n%d filled\n%d empty'%(filled+empty, filled, empty))
print('End of report.\n') 
