#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 30 18:05:39 2021

@author: latente
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from matplotlib import cm
from matplotlib.colors import ListedColormap
from glob import glob


def newColorMap(oldCmap, nColors, reverse=False, opacity=True):
    #https://matplotlib.org/3.1.0/tutorials/colors/colormap-manipulation.html
    big = cm.get_cmap(oldCmap, nColors) #sample a large set of colors from cmap
    if reverse: newCmap = big(np.linspace(1, 0, nColors))
    else: newCmap = big(np.linspace(0, 1, nColors))
    if opacity: newCmap[:,3] = np.linspace(0, 1, nColors)
    return ListedColormap(newCmap)


def contour(im, filename, vmin, vmax, cmap):
    #Determine where to draw contours (levels) – 1%, 5%, 10%, 20%, 40%, 60%,
    #   80% (and 100% when the density's maximum value is equal to vmax: a
    #   work around matplotlib.pyplot.contourf()'s 'color fill' and 'levels'
    #   mapping). 
    #https://matplotlib.org/api/_as_gen/matplotlib.pyplot.contourf.html#matplotlib.pyplot.contourf

    #Save a blank image if density is zero.
    shp = np.array((im.shape[1],im.shape[0]))
    dpi = 72
    if np.max(im)==0:
        plt.figure(figsize=tuple(shp/dpi))
        plt.axis('off')
        plt.savefig(filename)
        plt.clf()
        return
    
    #Else, plot and save contours    
    densityRange = np.max(im)-np.min(im)
    lvls = np.min(im) + (densityRange*np.array((0.01,0.05,0.1,0.2,0.4,
                                                0.6,0.8,0.9,0.95,1.0)))
    if np.max(im)==vmax: lvls=lvls[:-1] #remove highest level 

    x = np.linspace(0, im.shape[1], im.shape[1])
    y = np.linspace(0, im.shape[0], im.shape[0])
    X, Y = np.meshgrid(x,y)
    
    plt.figure(figsize=tuple(shp/dpi))
    plt.contourf(X, -Y, im, levels=lvls, cmap=cmap, 
                 origin='image', vmax=vmax, vmin=vmin, extend='both')
    plt.axis('off')
    plt.savefig(filename)
    plt.clf() 

def fiberDensityMap(im, sigma):
    if np.max(im)==0: return im
    print(im.dtype)
    return gaussian_filter(im,sigma)

def setUpFolders(directory):
    try:
        os.mkdir(directory)
    except:
        print('Directory %s already exist'%(directory))
    try:
        os.mkdir(directory+'densities')
    except:
        print('Directory %s already exist'%(directory+'densities'))
    try:
        os.mkdir(directory+'contours')
    except:
        print('Directory %s already exist'%(directory+'contours'))

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

#Project's Experimental Set Up
projectDetails = getProjectDetails("projectDetails.csv")
levels = projectDetails['levels']
markers = projectDetails['markers']
cases = projectDetails['cases']

#Directory to Fiber Data Set Up
dataDir='../fibers/raw/'
outDir ='../fibers/isopleths/'
setUpFolders(outDir)

#Generate density maps for each PNG file
ids = len(markers)*len(cases)
n=0
sigma = 5
for marker in markers:
    for level in levels:
        for case in cases:
            for i in range(ids):
                if os.path.isfile('%sdensities/%s_%s_lvl%s_%s.npy'%(outDir,case,marker,level,i)): continue
                fileName = '%s%s_%s_lvl%s_%s.png'%(dataDir,case,marker,level,i+1)
                try:
                    im = (plt.imread(fileName)[:,:,0]<1).astype(np.float32)
                except: continue
                n += 1
                print('\nFound: ', fileName)
                density = fiberDensityMap(im,sigma)
                print('Im shape', density.shape)
                print('Range:', np.min(density), np.max(density))
                np.save('%sdensities/%s_%s_lvl%s-%s'%(outDir,case,marker,level,i+1),
                        density)
        print('\n\n')
print('\tFinished generating density maps for %d PNG files.'%n) 
     


#Generate contour files for each level using all density files generated ^
n=0
for marker in markers:
    densities=[]
    currentLevel=[]
    peek=0
    for level in levels:
        print('\nLevel', level)
        fileNames = glob('%sdensities/*%s_lvl%s*.npy'%(outDir, marker, level))
        if len(fileNames)==0: continue
        density = np.zeros(np.load(fileNames[0]).shape)
        for fileName in fileNames:
            print(fileName)
            im = np.load(fileName)
            #print(im.shape)
            density += im
        density=density/len(fileNames) 
        peek = np.max((peek, np.max(density)))
        if peek == np.max(density): print('\t\tNew peek at %s'%peek)
        densities.append(density)
    for i, den in enumerate(densities):
        print('%s\t%s'%(np.max(den),peek))
        contour(den, '%scontours/%s_lvl%s_%s.svg'%(outDir, marker, levels[i], np.max(den)), 
                vmin = 0, vmax = peek, cmap = newColorMap('viridis', 1000, opacity=True, reverse=False))
        n+=1

print('\n\tFinished generating %d contour files.'%n)    

print("Done!")