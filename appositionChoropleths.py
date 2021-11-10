#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 18:46:02 2021

@author: latente
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage.segmentation import slic
from matplotlib import cm
from matplotlib.colors import ListedColormap
import os
import re

def newColorMap(oldCmap, nColors, reverse=False, opacity=True):
    #https://matplotlib.org/3.1.0/tutorials/colors/colormap-manipulation.html
    big = cm.get_cmap(oldCmap, nColors) #sample a large set of colors from cmap
    if reverse: newCmap = big(np.linspace(1, 0, nColors))
    else: newCmap = big(np.linspace(0, 1, nColors))
    if opacity: newCmap[:,3] = np.linspace(0, 1, nColors)
    return ListedColormap(newCmap)
newCM = newColorMap('viridis', 1000, opacity=True, reverse=False) 

"""
lets try making a csv with all the info or one level, since we got that template to work, and lets make a function for the choropleth
""" 

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
        #elif 'path=' in line:
        #    coord = re.search('"M(.*?)a', line, re.I)
        #    coord = coord.group(1).split(',')   
        else: continue
        X.append(float(coord[0]))
        Y.append(-float(coord[1]))
    
    coords = np.vstack((np.array(X), np.array(Y))).T
    return coords, np.array(viewBox[1].split(' '), dtype='float')

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
            print('Apposition out of frame – Skipping')
            continue
    return canvas

def choropleth(regionShapes, cells, scale):
    #ids = np.unique(template.reshape(-1, template.shape[2]), axis=0)
    vals = np.zeros(len(regionShapes))
    areas = np.zeros(len(regionShapes))
    mapa = np.zeros(regionShapes[0].shape[0:2])
    for i in range(len(regionShapes)):
        #brainRegion = np.all(template == ids[i], axis=-1)
        #if np.sum(brainRegion)<500: continue
        vals[i] = np.sum(cells[regionShapes[i]])*scale#/np.sum(brainRegion)
        areas[i] = np.sum(regionShapes[i])*scale
        mapa[regionShapes[i]] = vals[i]
    return mapa, vals, areas

def write(outDir, level,case,marker,vals,areas,brainRegionNames,replicate):
    f = open(outDir+"lvl%s.csv"%level, "a")
    if n == 0: 
        f.writelines([level+',,,,',','.join(brainRegionNames), '\n'])
        f.writelines([',,,,',','.join(areas.astype('str').tolist()), '\n'])
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
        os.mkdir(directory+'perGridRegion')
    except:
        print('Directory %s already exist'%(directory+'perGridRegion'))

levels = ['23', '24', '25', '26', '27', '28', '29', '30']
markers = ['aMSH','nNOS','MCH', 'HO','Copeptin','saMSH','sMCH']
cases = ['17-020', '17-022', '17-024', '18-012', '18-014', '18-016', '20-005','20-011', '20-012']
dataDir='../appositions/raw/'
outDir ='../appositions/choropleths/'
setUpFolders(outDir)
scaleFactor = 6
metricScale = 1 # we want every pixel to be equal to 1 so if we add the number of pixels, we get the count of each cell
for level in levels:
    n = 0
    print('Getting Brain Regions for Level %s'%level)
    brainRegionShapes, brainRegionNames = getRegions(level,"brainRegions")
    #template = plt.imread('Research/data/closed BM4/wGrids/BM4 level %s.png'%level)
    print('Analyzing All Cases & Markers Per Brain Region')
    for case in cases:
        for marker in markers:
            for i in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18']:
                fileName = '%s%s_%s_lvl%s_%s-01.svg'%(dataDir,case,marker,level,i)
                try:
                    coordinates, viewBox = getCoordsFromSVG(fileName)
                except: continue
                cells = cellLocations(coordinates,viewBox,scaleFactor)
                mapa, vals, areas= choropleth(brainRegionShapes, cells, metricScale)
                #plt.imsave(outDir+"perBrainRegion/"+'%s_%s_lvl%s-%s.png'%(case,marker,level,i),mapa,cmap=newCM)
                write(outDir+"perBrainRegion/",level,case,marker,vals,areas,brainRegionNames,i)
                #plt.imsave('%schoropleths/%s_%s_lvl%s-%s.png'%(directory,case,marker,level,i),mapa,cmap=newCM)
                #m = plt.imread('%schoropleths/%s_%s_lvl%s-%s.png'%(directory,case,marker,level,i))
                #plt.imsave('%schoropleths/%s_%s_lvl%s-%s.png'%(directory,case,marker,level,i), 0.5*m[:,:,0:3]+0.5*im[:,:,0:3])
                n += 1
print('\tFinished generating choropleth maps for %d SVG files.'%n) 

#Per Grid Region
for level in levels:
    n = 0
    print('Getting Grid Regions for Level %s'%level)
    brainRegionShapes, brainRegionNames = getRegions(level,"gridRegions")
    #template = plt.imread('Research/data/closed BM4/wGrids/BM4 level %s.png'%level)
    print('Analyzing All Cases & Markers Per Grid Region')
    for case in cases:
        for marker in markers:
            for i in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18']:
                fileName = '%s%s_%s_lvl%s_%s-01.svg'%(dataDir,case,marker,level,i)
                try:
                    coordinates, viewBox = getCoordsFromSVG(fileName)
                except: continue
                cells = cellLocations(coordinates,viewBox,scaleFactor)
                mapa, vals, areas= choropleth(brainRegionShapes, cells, metricScale)
                write(outDir+"perGridRegion/",level,case,marker,vals,areas,brainRegionNames,i)
                #plt.imsave(outDir+"perGridRegion/"+'%s_%s_lvl%s-%s.svg'%(case,marker,level,i),mapa,cmap=newCM)
                #m = plt.imread('%schoropleths/%s_%s_lvl%s-%s.png'%(directory,case,marker,level,i))
                #plt.imsave('%schoropleths/%s_%s_lvl%s-%s.png'%(directory,case,marker,level,i), 0.5*m[:,:,0:3]+0.5*im[:,:,0:3])
                n += 1
print('\tFinished generating choropleth maps for %d SVG files.'%n) 

"""
scratch

levels = ['23', '24', '25', '26', '27', '28', '29', '30']
markers = ['aMSH','nNOS','MCH', 'HO']
cases = ['17-020', '17-022', '17-024', '18-012', '18-016', '20-011', '20-012']

directory='Desktop/data/fibers/cropped/'

for marker in markers:
    for level in levels:
        print('Level %s'%level)
        template = np.mean(plt.imread('Research/data/closed BM4/BM4 level 28-01.png'), axis=-1)
        ids = np.unique(template)
        
        for case in cases:
            for i in ['01','02','03','04','05','06','07','08','09','10']:
                fileName = '%s%s_%s_lvl%s-%s.png'%(directory,case,marker,level,i)
                try:
                    im = plt.imread(fileName)[:,:,0]
                except: continue
                n += 1
                print('\nFound: ', fileName)
                density = fiberDensityMap(im,sigma)
                print('Im shape', density.shape)
                print('Range:', np.min(density), np.max(density))
                np.save('%sdensities/%s_%s_lvl%s-%s'%(directory,case,marker,level,i),
                        density)
        print('\n\n')
print('\tFinished generating density maps for %d PNG files.'%n) 
"""