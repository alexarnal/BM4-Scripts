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
import re
from glob import glob

def newColorMap(oldCmap, nColors, reverse=False, opacity=True):
    #https://matplotlib.org/3.1.0/tutorials/colors/colormap-manipulation.html
    big = cm.get_cmap(oldCmap, nColors) #sample a large set of colors from cmap
    if reverse: newCmap = big(np.linspace(1, 0, nColors))
    else: newCmap = big(np.linspace(0, 1, nColors))
    if opacity: newCmap[:,3] = np.linspace(0, 1, nColors)
    return ListedColormap(newCmap)
newCM = newColorMap('viridis', 1000, opacity=True, reverse=False) 

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

def cellLocations(coordinates,viewBox, scaleFactor):
    #first remove duplicates
    coords = [tuple(row) for row in coordinates]
    coords = np.unique(coords,axis=0)
    canvas = np.zeros((int(viewBox[3]*scaleFactor),int(viewBox[2]*scaleFactor))).astype(np.float32)
    
    if len(coordinates)==0: return canvas
    x=-coords[:,1]
    y=coords[:,0]
    for i in range(len(x)):
        try:
            # print(int(x[i]),int(y[i]))
            canvas[int(x[i]*scaleFactor),int(y[i]*scaleFactor)] += 1
        except: 
            print('Cell out of frame – Skipping')
            continue
    return canvas

def choropleth(regionShapes, fibers, scale, normalized_by_region_area=False):
    vals = np.zeros(len(regionShapes))
    areas = np.zeros(len(regionShapes))
    mapa = np.zeros(regionShapes[0].shape[0:2])
    if normalized_by_region_area:
        for i in range(len(regionShapes)):
            vals[i] = np.sum(fibers[regionShapes[i]])*scale/np.sum(regionShapes[i])
            areas[i] = np.sum(regionShapes[i])*scale/np.sum(regionShapes[i])
            mapa[regionShapes[i]] = vals[i] 
    else:
        for i in range(len(regionShapes)):
            vals[i] = np.sum(fibers[regionShapes[i]])*scale
            areas[i] = np.sum(regionShapes[i])*scale
            mapa[regionShapes[i]] = vals[i]        
    return mapa, vals, areas

def write(outDir,level,case,marker,vals,areas,brainRegionNames,replicate, metric_scale,n):
    if n == 0: 
        f = open(outDir+"lvl%s.csv"%level, "w")
        f.writelines(['level,case,randomID,peptide,',','.join(brainRegionNames), '\n'])
        f.writelines(['metric_scale = %s,,,,'%(metric_scale),','.join(areas.astype('str').tolist()), '\n'])
    else:
        f = open(outDir+"lvl%s.csv"%level, "a")
        l = [level + ',' + case + ',' + replicate + ',' + marker + ',' , ','.join(vals.astype('str').tolist()), '\n']
        f.writelines(l)
        f.close()

def getRegions(lvl, regionType):
    directory = '../%s/'%(regionType)
    names=os.listdir(directory)
    regionShapes = []
    regionSizes = []
    regionNames = []
    for name in names:
        if "lvl"+lvl not in name: continue
        try:
            x = plt.imread(directory+name)[:,:,0]<0.5
        except: continue
        regionShapes.append(x)
        regionSizes.append(np.sum(x))
        regionNames.append(name[6:-4]) #remove lvlNum and .png
    indxs = np.argsort(np.array(regionSizes))
    sortedNames = []
    sortedShape = []
    for indx in indxs[::-1]:
        sortedNames.append(regionNames[indx])
        sortedShape.append(regionShapes[indx])
    return sortedShape, sortedNames 

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

def getProjectDetails(path):
    myDictionary = {}
    file = open(path,"r")
    for line in file:
        fields = [x.replace('\n','') for x in line.split(",")] #.replace(' ','')
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
scaleFactor = 6 # SVG scale multiplier
metricScale = 1 # we want every pixel to be equal to 1 so if we add the number of pixels, we get the count of each cell
normalize_by_area=True #if true, the program will output choropleth maps, if false it will output tabulted counts

#Directory to Apposition Data Set Up
dataDir='../cells/raw/'
outDir ='../cells/choropleths/'
setUpFolders(outDir)

#Process each SVG file brain-region-wise 
if normalize_by_area: print('\nGenerating choropleth maps of counts normalized by brain region area for each SVG file.')
else: print('\nGenerating brain-region-wise count tables from all SVG file.')
ids = len(markers)*len(cases)
nSVG=0
for level in levels:  
    n = 0
    print('Getting Brain Regions for Level %s'%level)
    brainRegionShapes, brainRegionNames = getRegions(level,"brainRegions")
    print('Analyzing All Cases & Markers Per Brain Region')
    for case in cases:
        for marker in markers:
            for i in range(ids):
                fileName = '%s%s_%s_lvl%s_%s-01.svg'%(dataDir,case,marker,level,i+1)
                try:
                    coordinates, viewBox = getCoordsFromSVG(fileName)
                except: continue
                cells = cellLocations(coordinates,viewBox,scaleFactor)
                mapa, vals, areas= choropleth(brainRegionShapes, cells, metricScale, normalize_by_area)
                if not normalize_by_area:
                    write(outDir+"perBrainRegion/",level,case,marker,vals,areas,brainRegionNames,str(i+1), metricScale,n)
                if normalize_by_area:
                    np.save("%sperBrainRegion/individual/%s_%s_lvl%s_%s"%(outDir,case,marker,level,i+1),mapa.astype('float32'))
                n += 1
                nSVG+=1
print('\tFinished processing %d SVG individual files.'%nSVG) 

#Generate brain-region-wise average choropleths for each level using all maps generated ^
if normalize_by_area:
    print('\nGenerating brain-region-wise average choropleths for each level using all maps generated ^')
    n=0
    for marker in markers:
        densities=[]
        currentLevel=[]
        peek=0
        for level in levels:
            print('\nLevel', level)
            ext = '%sperBrainRegion/individual/*%s_lvl%s*.npy'%(outDir, marker, level)
            ext = re.sub('([\[\]])','[\\1]',ext) # https://stackoverflow.com/questions/2595119/glob-and-bracket-characters
            fileNames = glob(ext)
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
            plt.imsave('%sperBrainRegion/average/%s_lvl%s_%s.png'%(outDir, marker, levels[i],np.max(den)),den.astype('float32'),cmap=newCM, vmin=0, vmax=peek)
            n+=1
    print('\n\tFinished generating %d brain-region-wise average choropleth maps.'%n) 

#Process each SVG file grid-region-wise 
if normalize_by_area: print('\nGenerating choropleth maps of counts normalized by grid region area for each SVG file.')
else: print('\nGenerating grid-region-wise count tables from all SVG file.')
ids = len(markers)*len(cases)
nSVG = 0
for level in levels:
    n=0
    print('Getting Grid Regions for Level %s'%level)
    brainRegionShapes, brainRegionNames = getRegions(level,"gridRegions")
    print('Analyzing All Cases & Markers Per Grid Region')
    for case in cases:
        for marker in markers:
            for i in range(ids):
                fileName = '%s%s_%s_lvl%s_%s-01.svg'%(dataDir,case,marker,level,i+1)
                try:
                    coordinates, viewBox = getCoordsFromSVG(fileName)
                except: continue
                cells = cellLocations(coordinates,viewBox,scaleFactor)
                mapa, vals, areas= choropleth(brainRegionShapes, cells, metricScale, normalize_by_area)
                if not normalize_by_area:
                    write(outDir+"perGridRegion/",level,case,marker,vals,areas,brainRegionNames,str(i+1), metricScale,n)
                if normalize_by_area: 
                    np.save("%sperGridRegion/individual/%s_%s_lvl%s_%s"%(outDir,case,marker,level,i+1),mapa.astype('float32'))
                n += 1
                nSVG+=1
print('\tFinished generating grid-region-wise count tables and choropleth maps for %d SVG individual files.'%nSVG) 


#Generate grid-region-wise average choropleths for each level using all maps generated ^
if normalize_by_area:
    print('\nGenerating grid-region-wise average choropleths for each level using all maps generated ^')
    n=0
    for marker in markers:
        densities=[]
        currentLevel=[]
        peek=0
        for level in levels:
            print('\nLevel', level)
            ext = '%sperGridRegion/individual/*%s_lvl%s*.npy'%(outDir, marker, level)
            ext = re.sub('([\[\]])','[\\1]',ext) # https://stackoverflow.com/questions/2595119/glob-and-bracket-characters
            fileNames = glob(ext)
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
            plt.imsave('%sperGridRegion/average/%s_lvl%s_%s.png'%(outDir, marker, levels[i],np.max(den)),den.astype('float32'),cmap=newCM, vmin=0, vmax=peek)
            n+=1
    print('\n\tFinished generating %d grid-region-wise average choropleth maps.'%n)  

print("Done!")