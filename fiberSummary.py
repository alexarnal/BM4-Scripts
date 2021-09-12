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

print('\nGenerating Summary')

#Project's Experimental Set Up
levels = ['23', '24', '25', '26', '27', '28', '29', '30']
markers = ['aMSH','nNOS','MCH', 'HO', 'sMCH', 'asMSH', 'Copeptin']
cases = ['17-020', '17-022', '17-024', '18-012', '18-014', '18-016', '20-005', '20-011', '20-012']

#Directory to Fiber Data Set Up
dataDir='../fibers/raw/'
outDir ='../fibers/isopleths/'

print('Writing to ../fibers/summary.txt')
#Set up report
f = open("../fibers/summary.txt", "w")
f.write("Summary report for fibers")
f.close()

#Generate density files for each SVG file
filled= 0
empty = 0
for marker in markers:
    for case in cases:
        for level in levels:
            for i in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']:

                fileName = '%s%s_%s_lvl%s_%s.png'%(dataDir,case,marker,level,i)
                try:
                    im = (plt.imread(fileName)[:,:,0]<1).astype(np.float32)
                except: continue
                
                f = open("../fibers/summary.txt", "a")
                f.write('\n\nFound: %s_%s_lvl%s_%s'%(case,marker,level,i))
                f.write('\tNumber of Fiber Pixels: %d'%np.sum(im))
                f.close()

                if np.sum(im)==0: empty+=1
                else: filled+=1

f = open("../fibers/fiber_summary.txt", "a")
f.write('\n\nThere is a total of %d fiber files:\n\t%d filled\n\t%d empty'%(filled+empty, filled, empty))
f.write('\n\nEnd of report.')
f.close()  

print('There is a total of %d fiber files:\n%d filled\n%d empty'%(filled+empty, filled, empty))
print('End of report.\n') 