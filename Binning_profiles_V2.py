import numpy as np
import matplotlib.pyplot as plt
import os
import time
#import concurrent.futures
#from scipy.optimize import curve_fit
#%% Functions

def binData(data,binwidth,averageType = 'median'):
    '''
    data[0],data[1],data[2],data[3] = QC, Height,WS,WD
    data[4],data[5],data[6] = U,V,W
    data[13]/data[-1] = metadata including track info if avaliable
    '''
    # height = data[1]
    # WS = data[2]
    # WD = data[3]
    # U = data[4]
    # V = data[5]
    # W = data[6]
    
    height = data[0]
    WS = data[1]
    WD = data[2]
    U = data[3]
    V = data[4]
    W = data[5]
    metadata = data[-1]
    
    heightArray = np.arange(binwidth/2,15000,binwidth)
    WSGroupArray = [ [] for _ in range(0,len(heightArray)) ]
    WDGroupArray = [ [] for _ in range(0,len(heightArray)) ]
    UGroupArray = [ [] for _ in range(0,len(heightArray)) ]
    VGroupArray = [ [] for _ in range(0,len(heightArray)) ]
    WGroupArray = [ [] for _ in range(0,len(heightArray)) ]
    
    for i in range(0,len(data[0])):
        sortingIndex = int(height[i]//binwidth)
        WSGroupArray[sortingIndex].append(WS[i])
        WDGroupArray[sortingIndex].append(WD[i])
        UGroupArray[sortingIndex].append(U[i])
        VGroupArray[sortingIndex].append(V[i])
        WGroupArray[sortingIndex].append(W[i])
        
    WSArray= []
    WDArray= []
    UArray= []
    VArray= []
    WArray= []
    
    for i in range(0,len(heightArray)):
        if averageType == 'median':
            WSArray.append(np.nanmedian(WSGroupArray[i]))
            WDArray.append(np.nanmedian(WDGroupArray[i]))
            UArray.append(np.nanmedian(UGroupArray[i]))
            VArray.append(np.nanmedian(VGroupArray[i]))
            WArray.append(np.nanmedian(WGroupArray[i]))
        elif averageType == 'mean':
            WSArray.append(np.nanmean(WSGroupArray[i]))
            WDArray.append(np.nanmean(WDGroupArray[i]))
            UArray.append(np.nanmean(UGroupArray[i]))
            VArray.append(np.nanmean(VGroupArray[i]))
            WArray.append(np.nanmean(WGroupArray[i]))

    return [np.transpose(heightArray),np.transpose(WSArray),np.transpose(WDArray),np.transpose(UArray),np.transpose(VArray),np.transpose(WArray),metadata]


#%%

allDataMatchedExportPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Matched'
allDataProfileExportPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Profiles'

dataMainPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3'
dataExportPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Seperated'
dataExportTotalPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Seperated\Total'

#%% Binning Matched Profiles
numProfiles = 100000
for file in os.listdir(allDataMatchedExportPath):
    if file.split()[0] == 'AutoCorrected':
        profileUnsorted= np.load(os.path.join(allDataMatchedExportPath, file),allow_pickle=True)
        
        if len(profileUnsorted) > numProfiles:
            profileUnsorted = profileUnsorted[0:numProfiles]
            
        profileUnsortedBinned = []
        
        binwidth = 50
        averageType = 'median'
        
        profileUnsortedSize = len(profileUnsorted)
        counter = 0
        
        for profile in profileUnsorted:
            print(file,counter,'/',profileUnsortedSize)
            profileUnsortedBinned.append(binData(profile,binwidth,averageType))
            counter += 1
              
        np.save(os.path.join(allDataMatchedExportPath, 'Binned ' + file), profileUnsortedBinned)
        
#%% Binning non-matched Profiles

for file in os.listdir(allDataProfileExportPath):

    if file.split()[0] == 'Part':
        profileUnsorted= np.load(os.path.join(allDataProfileExportPath, file),allow_pickle=True)[::40]
    
        profileUnsortedBinned = []
        
        binwidth = 50
        averageType = 'median'
        
        profileUnsortedSize = len(profileUnsorted)
        counter = 0
        
        for profile in profileUnsorted:
            print(file,counter,'/',profileUnsortedSize)
            profileUnsortedBinned.append(binData(profile,binwidth,averageType))
            counter += 1
              
        np.save(os.path.join(allDataProfileExportPath, 'Binned ' + file), profileUnsortedBinned)


