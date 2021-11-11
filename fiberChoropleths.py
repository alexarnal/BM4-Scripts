#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 18:46:02 2021

@author: latente
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
import os
from glob import glob

def newColorMap(oldCmap, nColors, reverse=False, opacity=True):
    #https://matplotlib.org/3.1.0/tutorials/colors/colormap-manipulation.html
    big = cm.get_cmap(oldCmap, nColors) #sample a large set of colors from cmap
    if reverse: newCmap = big(np.linspace(1, 0, nColors))
    else: newCmap = big(np.linspace(0, 1, nColors))
    if opacity: newCmap[:,3] = np.linspace(0, 1, nColors)
    return ListedColormap(newCmap)
newCM = newColorMap('viridis', 1000, opacity=True, reverse=False) 

def choropleth(regionShapes, fibers, scale):
    vals = np.zeros(len(regionShapes))
    areas = np.zeros(len(regionShapes))
    mapa = np.zeros(regionShapes[0].shape[0:2])
    for i in range(len(regionShapes)):
        vals[i] = np.sum(fibers[regionShapes[i]])*scale
        areas[i] = np.sum(regionShapes[i])*scale
        mapa[regionShapes[i]] = vals[i]
    return mapa, vals, areas

def write(outDir,level,case,marker,vals,areas,brainRegionNames,replicate):
    if n == 0: 
        f = open(outDir+"lvl%s.csv"%level, "w")
        f.writelines(['level,case,replicate,peptide,',','.join(brainRegionNames), '\n'])
        f.writelines([',,,,',','.join(areas.astype('str').tolist()), '\n'])
    else:
        f = open(outDir+"lvl%s.csv"%level, "a")
        l = [level + ',' + case + ',' + replicate + ',' + marker + ',' , ','.join(vals.astype('str').tolist()), '\n']
        f.writelines(l)
        f.close()

def getRegions(lvl, regionType):
    directory = '../%s/'%(regionType)
    names=os.listdir(directory)
    regionShapes = []
    regionNames = []
    for name in names:
        if "lvl"+lvl not in name: continue
        try:
            regionShapes.append(plt.imread(directory+name)[:,:,0]<0.5)
        except: continue
        regionNames.append(name[6:-4]) #remove lvlNum and .png
    return regionShapes, regionNames 

def setUpFolders(directory):
    try:
        os.mkdir(directory)
    except:
        print('Directory %s already exist'%(directory))
    try:
        os.mkdir(directory+'perBrainRegion')
    except:
        print('Directory %s already exist'%(directory+'perBrainRegion'))
    try:
        os.mkdir(directory+'perBrainRegion/individual')
    except:
        print('Directory %s already exist'%(directory+'perBrainRegion/individual'))
    try:
        os.mkdir(directory+'perBrainRegion/average')
    except:
        print('Directory %s already exist'%(directory+'perBrainRegion/average'))
    try:
        os.mkdir(directory+'perGridRegion')
    except:
        print('Directory %s already exist'%(directory+'perGridRegion'))
    try:
        os.mkdir(directory+'perGridRegion/individual')
    except:
        print('Directory %s already exist'%(directory+'perGridRegion/individual'))
    try:
        os.mkdir(directory+'perGridRegion/average')
    except:
        print('Directory %s already exist'%(directory+'perGridRegion/average'))

def getScale(lvl):
    regionShapes, regionNames = getRegions(lvl, "gridRegions")
    area=0
    n = 0
    for i in range(len(regionShapes)):
        width= np.max(np.where(np.any(regionShapes[i], axis=0))[0]) - np.min(np.where(np.any(regionShapes[i], axis=0))[0])
        height = np.max(np.where(np.any(regionShapes[i], axis=1))[0]) - np.min(np.where(np.any(regionShapes[i], axis=1))[0])
        area += (1/height * 1/width) #each "square" on the grid is equivalent to 1mm x 1mm so every pixel is equivalnt to 1/numberOfPixelsHigh * 1/numberOfPixelsWide
        n+=1
    try:
        return area/n
    except:
        print("Detected %s grid regions. Returing metric equivalent scale = %s"%(n,area))
        return area

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
outDir ='../fibers/choropleths/'
setUpFolders(outDir)

#Generate brain-region-wise count tables and choropleth maps for each PNG file
print('\nGenerating brain-region-wise count tables and choropleth maps for each PNG file.')
ids = len(markers)*len(cases)
n=0
for level in levels:
    n = 0
    metricScale = getScale(level)
    print('Getting Brain Regions for Level %s'%level)
    brainRegionShapes, brainRegionNames = getRegions(level, "brainRegions")
    print('Analyzing All Cases & Markers')
    for case in cases:
        for marker in markers:
            for i in range(ids):
                fileName = '%s%s_%s_lvl%s_%s.png'%(dataDir,case,marker,level,i+1)
                try:
                    fibers = plt.imread(fileName)[:,:,0] < 1
                except: continue
                mapa, vals, areas= choropleth(brainRegionShapes, fibers, metricScale)
                write(outDir+"perBrainRegion/",level,case,marker,vals,areas,brainRegionNames,str(i+1))
                np.save("%sperBrainRegion/individual/%s_%s_lvl%s_%s"%(outDir,case,marker,level,i+1),mapa)
                n += 1
print('\tFinished generating brain-region-wise count tables and choropleth maps for %d PNG individual files.'%n) 

#Generate brain-region-wise average choropleths for each level using all maps generated ^
print('\nGenerating brain-region-wise average choropleths for each level using all maps generated ^')
n=0
for marker in markers:
    densities=[]
    currentLevel=[]
    peek=0
    for level in levels:
        print('\nLevel', level)
        fileNames = glob('%sperBrainRegion/individual/*%s_lvl%s*.npy'%(outDir, marker, level))
        if len(fileNames)==0: continue
        density = np.zeros(np.load(fileNames[0]).shape)
        for fileName in fileNames:
            print(fileName)
            im = np.load(fileName)
            density += im
        density=density/len(fileNames) 
        peek = np.max((peek, np.max(density)))
        if peek == np.max(density): print('\t\tNew peek at %s'%peek)
        densities.append(density)
    for i, den in enumerate(densities):
        print('%s\t%s'%(np.max(den),peek))
        plt.imsave('%sperBrainRegion/average/%s_lvl%s_%s.png'%(outDir, marker, levels[i],np.max(den)),den,cmap=newCM)
        n+=1
print('\n\tFinished generating %d brain-region-wise average choropleth maps.'%n)  

#Generate grid-region-wise count tables and choropleth maps for each PNG file
print('\nGenerating grid-region-wise count tables and choropleth maps for each PNG file.')
ids = len(markers)*len(cases)
n = 0
for level in levels:
    metricScale = getScale(level) #metric equivelent 
    print('Getting Grid Regions for Level %s'%level)
    gridRegionShapes, gridRegionNames = getRegions(level, "gridRegions")
    print('Analyzing All Cases & Markers')
    for case in cases:
        for marker in markers:
            for i in range(ids):
                fileName = '%s%s_%s_lvl%s_%s.png'%(dataDir,case,marker,level,i+1)
                try:
                    fibers = plt.imread(fileName)[:,:,0] < 1
                except: continue
                mapa, vals, areas= choropleth(gridRegionShapes, fibers, metricScale)
                write(outDir+"perGridRegion/",level,case,marker,vals,areas,gridRegionNames,str(i+1))
                np.save("%sperGridRegion/individual/%s_%s_lvl%s_%s"%(outDir,case,marker,level,i+1),mapa)
                n += 1
print('\tFinished generating grid-region-wise count tables and choropleth maps for %d PNG individual files.'%n) 

#Generate grid-region-wise average choropleths for each level using all maps generated ^
print('\nGenerating grid-region-wise average choropleths for each level using all maps generated ^')
n=0
for marker in markers:
    densities=[]
    currentLevel=[]
    peek=0
    for level in levels:
        print('\nLevel', level)
        fileNames = glob('%sperGridRegion/individual/*%s_lvl%s*.npy'%(outDir, marker, level))
        if len(fileNames)==0: continue
        density = np.zeros(np.load(fileNames[0]).shape)
        for fileName in fileNames:
            print(fileName)
            im = np.load(fileName)
            density += im
        density=density/len(fileNames) 
        peek = np.max((peek, np.max(density)))
        if peek == np.max(density): print('\t\tNew peek at %s'%peek)
        densities.append(density)
    for i, den in enumerate(densities):
        print('%s\t%s'%(np.max(den),peek))
        plt.imsave('%sperGridRegion/average/%s_lvl%s_%s.png'%(outDir, marker, levels[i],np.max(den)),den,cmap=newCM)
        n+=1
print('\n\tFinished generating %d grid-region-wise average choropleth maps.'%n)  

print("Done!")