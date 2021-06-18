import numpy as np
import matplotlib.pyplot as plt
import os
import time
from haversine import haversine, Unit


#%% Functions
def find_nearest(array, value):
    '''
    Finds the index of the entry in the array closest to the "value" input
    '''
    array = np.array(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def findIntercept(fit1,fit2,cov1,cov2):
    '''
    Takes the fitting parameters and covariance matrix of 2 linear fits and return the point of intersection and its error
    '''
    delta_c = fit2[1] - fit1[1] #change in intercept
    delta_m = fit2[0] - fit1[0] #change in gradient
    
    x_inter = delta_c / (-delta_m) 
    A = fit1[0]*x_inter 
    y_inter = A + fit1[1]
    
    err_delta_c = np.sqrt((cov1[1,1]) + (cov2[1,1]))
    err_delta_m = np.sqrt((cov1[0,0]) + (cov2[0,0]))
#    
#    err_x_inter = x_inter*np.sqrt((err_delta_m/delta_m)**2 + (err_delta_c/delta_c)**2)
#    err_A = A*np.sqrt((cov1[0,0]/fit1[0])**2 + (err_x_inter/x_inter)**2)
#    err_y_inter = np.sqrt((err_A)**2 + (cov1[1,1])**2)
#    return x_inter,y_inter,err_x_inter,err_y_inter
    
    err_x_inter = np.sqrt((-err_delta_c/delta_m)**2 + (delta_c * err_delta_m/delta_m**2)**2)
    err_y_inter = 0
    return x_inter,y_inter,err_x_inter,err_y_inter

def cleaningArray(height,testArray):
    indices = np.argwhere(np.isnan(testArray)).flatten()
    newHeight = np.delete(height,indices)
    newTestArray = np.delete(testArray,indices)
    return newHeight,newTestArray

def findBoundaryHeight(height,deflection,L1,L2,U1,U2):
    x_inter = np.nan
    y_inter = np.nan
    err_x_inter = np.nan
    err_y_inter = np.nan
    
    LowLayerIndex = find_nearest(height,L1)
    HighLayerIndex = find_nearest(height,L2)
    LowLayerIndexUpper = find_nearest(height,U1)
    HighLayerIndexUpper = find_nearest(height,U2)
    try:
        testHeight,testDef = cleaningArray(height[LowLayerIndex:HighLayerIndex],deflection[LowLayerIndex:HighLayerIndex])
        fit,cov = np.polyfit(testHeight,testDef,1,cov=True)
        
        testHeightUpper,testDefUpper = cleaningArray(height[LowLayerIndexUpper:HighLayerIndexUpper],deflection[LowLayerIndexUpper:HighLayerIndexUpper])
        fitUpper,covUpper = np.polyfit(testHeightUpper,testDefUpper,1,cov=True)
        
        x_inter,y_inter,err_x_inter,err_y_inter = findIntercept(fit,fitUpper,cov,covUpper)
        
    except:
        print("Err in fitting")
    
    return x_inter,y_inter,err_x_inter,err_y_inter
    


#%% Setting import and export paths


allDataMatchedPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Matched'
allDataProfilePath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Profiles'
exportVarPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3'

dataExportPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Seperated'
dataExportTotalPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Seperated\Total'

#%% Varaibles
referenceHeight = 1500
singleNo = 0

'''
partial = 'yes' = Loads a smaller group of the profiles
        = 'no' = Loads all of the profiles
        = 'single' = loads only a single profile
'''
partial = 'no'
vectorDeflect = False
#%% Loading data

'''
Creates the directory for observation relating to all profile, eg. Average profile of all profiles etc
'''
if os.path.exists(dataExportTotalPath) == False:
    os.makedirs(dataExportTotalPath)
    
#%% for Non-matched Profiles
'''
DONT RUN!!!
'''
profileArray = []

for file in os.listdir(allDataProfilePath):
    counter = 0
    if file.split()[0] == 'Binned':
        print(file)
        dataUnsorted = np.load(os.path.join(allDataProfilePath, file),allow_pickle=True)
        numProfiles = len(dataUnsorted)
        for profile in dataUnsorted:
            counter += 1
        
            boundaryLayerIndex = find_nearest(profile[0],referenceHeight)
            
            WDDeflectAvg = []
            
            normHeight = np.array(profile[0])/profile[0][boundaryLayerIndex]
            normSpeed = np.array(profile[1])/profile[1][boundaryLayerIndex]
            
            if vectorDeflect: 
                '''
                Vector method: rotates wind vectors in a profile and performs a basis transformation(rotation
                such that the vector at reference height after tranformation is (0,1). Then determines the 
                deflection by taking the dot product and determines the sign of the deflection by looking at
                the component.)
                '''
                refVectorFwd = [profile[3][boundaryLayerIndex],profile[4][boundaryLayerIndex]]
                refVectorPerp = [profile[4][boundaryLayerIndex],-profile[3][boundaryLayerIndex]]
                
                refVectorFwdNorm = refVectorFwd / np.linalg.norm(refVectorFwd)
                refVectorPerpNorm = refVectorPerp / np.linalg.norm(refVectorPerp)
                
                transM = np.array([[refVectorFwdNorm[0],refVectorPerpNorm[0]],[refVectorFwdNorm[1],refVectorPerpNorm[1]]])
        
                transMInv = np.linalg.inv(transM)
        
                refVectorFwdPrime = np.dot(transMInv,np.array([[refVectorFwdNorm[0]],[refVectorFwdNorm[1]]]))
                refVectorFwdPrimeNorm =  refVectorFwdPrime / np.linalg.norm(refVectorFwdPrime)
                
                for j in range(np.shape(profile)[1]):
                    transVector = np.dot(transMInv,np.array([[profile[3][j]],[profile[4][j]]]))
                    
                    if not np.isnan( profile[3][j]):
        #                    print('A:',np.array([[profile[3][j]],[profile[4][j]]]),'REF:',refVectorFwd)
                        pass
                    transVectorNorm = transVector / np.linalg.norm(transVector)
                    
                    angDev = (180/np.pi)*np.arccos(np.dot(transVectorNorm.flatten(),refVectorFwdPrimeNorm.flatten()))
        
                    if transVectorNorm.flatten()[0] > 0:
                        angDev = -angDev
        
                    WDDeflectAvg.append(angDev)
        
            else:
                '''
                Bearing method: determines the deflection by taking the difference between the bearing at 
                a given height and the bearing at the reference height. Correction is then applied as 
                ocassionally the absolute value of the deflection can be > 180.
                '''
                for j in range(np.shape(profile[0])[0]):
                    print(file,counter,'/',numProfiles,j)
                    originalDeflection = profile[2][j] - profile[2][boundaryLayerIndex]
                    
                    if abs(originalDeflection) > 180:
                        if originalDeflection > 0:
                            REF_boundary = profile[2][boundaryLayerIndex] + 360
                            WDDeflectAvg.append(profile[2][j] - REF_boundary)
                        else:
                            REF_height = profile[2][j] + 360
                            WDDeflectAvg.append(REF_height - profile[2][boundaryLayerIndex])
                    else:
                        WDDeflectAvg.append(profile[2][j] - profile[2][boundaryLayerIndex])
        
        #        profileArrayNorm.append([normHeight,normSpeed,np.array(WDDeflectAvg)])
            
            profileArray.append([normHeight,normSpeed,np.array(WDDeflectAvg),profile[0],profile[1],profile[2],profile[3],profile[4],profile[5],profile[6]])
        
np.save(os.path.join(allDataProfilePath, 'Single Array of Norm Unmatched Profile Unsorted'), profileArray)
#%% for Matched Profiles

for file in os.listdir(allDataMatchedPath):

    counter = 0
    if file.split()[0] == 'Binned':
        profileArray = []
        print(file)
        dataUnsorted = np.load(os.path.join(allDataMatchedPath, file),allow_pickle=True)
        numProfiles = len(dataUnsorted)
        for profile in dataUnsorted:
            counter += 1
            print(counter,'/',numProfiles,file)
            boundaryLayerIndex = find_nearest(profile[0],referenceHeight)
            
            WDDeflectAvg = []
            
            normHeight = np.array(profile[0])/profile[0][boundaryLayerIndex]
            normSpeed = np.array(profile[1])/np.nanmedian(profile[1][boundaryLayerIndex-3:boundaryLayerIndex+4])
            #normSpeed = np.array(profile[1])/profile[1][boundaryLayerIndex]
            
            if vectorDeflect: 
                '''
                Vector method: rotates wind vectors in a profile and performs a basis transformation(rotation
                such that the vector at reference height after tranformation is (0,1). Then determines the 
                deflection by taking the dot product and determines the sign of the deflection by looking at
                the component.)
                '''
                refVectorFwd = [profile[3][boundaryLayerIndex],profile[4][boundaryLayerIndex]]
                refVectorPerp = [profile[4][boundaryLayerIndex],-profile[3][boundaryLayerIndex]]
                
                refVectorFwdNorm = refVectorFwd / np.linalg.norm(refVectorFwd)
                refVectorPerpNorm = refVectorPerp / np.linalg.norm(refVectorPerp)
                
                transM = np.array([[refVectorFwdNorm[0],refVectorPerpNorm[0]],[refVectorFwdNorm[1],refVectorPerpNorm[1]]])
        
                transMInv = np.linalg.inv(transM)
        
                refVectorFwdPrime = np.dot(transMInv,np.array([[refVectorFwdNorm[0]],[refVectorFwdNorm[1]]]))
                refVectorFwdPrimeNorm =  refVectorFwdPrime / np.linalg.norm(refVectorFwdPrime)
                
                for j in range(np.shape(profile)[1]):
                    transVector = np.dot(transMInv,np.array([[profile[3][j]],[profile[4][j]]]))
                    
                    if not np.isnan( profile[3][j]):
        #                    print('A:',np.array([[profile[3][j]],[profile[4][j]]]),'REF:',refVectorFwd)
                        pass
                    transVectorNorm = transVector / np.linalg.norm(transVector)
                    
                    angDev = (180/np.pi)*np.arccos(np.dot(transVectorNorm.flatten(),refVectorFwdPrimeNorm.flatten()))
        
                    if transVectorNorm.flatten()[0] > 0:
                        angDev = -angDev
        
                    WDDeflectAvg.append(angDev)
        
            else:
                '''
                Bearing method: determines the deflection by taking the difference between the bearing at 
                a given height and the bearing at the reference height. Correction is then applied as 
                ocassionally the absolute value of the deflection can be > 180.
                '''
                for j in range(np.shape(profile[0])[0]):
                    #print(file,counter,'/',numProfiles,j)
                    originalDeflection = profile[2][j] - np.nanmedian(profile[2][boundaryLayerIndex-3:boundaryLayerIndex+4])
                    #profile[2][boundaryLayerIndex]
                    
                    if abs(originalDeflection) > 180:
                        if originalDeflection > 0:
                            REF_boundary = np.nanmedian(profile[2][boundaryLayerIndex-3:boundaryLayerIndex+4]) + 360
                            WDDeflectAvg.append(profile[2][j] - REF_boundary)
                        else:
                            REF_height = profile[2][j] + 360
                            WDDeflectAvg.append(REF_height - np.nanmedian(profile[2][boundaryLayerIndex-3:boundaryLayerIndex+4]))
                    else:
                        WDDeflectAvg.append(originalDeflection)
        
        #        profileArrayNorm.append([normHeight,normSpeed,np.array(WDDeflectAvg)])
            
            profileArray.append([normHeight,normSpeed,np.array(WDDeflectAvg),profile[0],profile[1],profile[2],profile[3],profile[4],profile[5],profile[-1]])
        
        np.save(os.path.join(allDataMatchedPath, 'Normalised ' + file), profileArray)
#%% Sorting non-matched Profiles


'''
sortBy = 'speed' = sort based on mean/median speeds around the reference height
        = 'gradientBelowDef' = sort based on linear gradient below the reference height
        = 'gradientAboveDef' = sort based on linear gradient above the reference height
        = 'BoundaryHeightDef' = sort based on the boundary height determined by linear intercept method on Deflection profile 
        = 'BoundaryHeightSpeed' = sort based on the boundary height determined by linear intercept method on wind speed profile 
        = 'Rossby' = sort based on the rosby number of the profile [still needs work]
'''
sortBy = ['speed','gradientBelowDef','gradientAboveDef','gradientBelowSpeed','gradientAboveSpeed','BoundaryHeightDef','BoundaryHeightSpeed']#,'Rosby']
#sortBy = ['gradientBelowDef']
sepSpeed = 20

sepGradBelowDef_L = -0.01 
sepGradBelowDef_U = 0.01 


sepGradAboveDef_L = -0.01
sepGradAboveDef_U = 0.01

sepGradBelowSpeed_L = -0.005
sepGradBelowSpeed_U = 0.005

sepGradAboveSpeed_L = -0.001
sepGradAboveSpeed_U = 0.001

sepBHeight = 1000

sepRosby = 1000

exportVar = {
        "speed" : sepSpeed,
        
        "gradientBelowDef" : 0,
        "gradientBelowDef L": sepGradBelowDef_L,
        "gradientBelowDef U": sepGradBelowDef_U,
        "gradientAboveDef" : 0,
        "gradientAboveDef L": sepGradAboveDef_L,
        "gradientAboveDef U": sepGradAboveDef_U,
        
        "gradientBelowSpeed" : 0,
        "gradientBelowSpeed L": sepGradBelowSpeed_L,
        "gradientBelowSpeed U": sepGradBelowSpeed_U,
        "gradientAboveSpeed" : 0,
        "gradientAboveSpeed L": sepGradAboveSpeed_L,
        "gradientAboveSpeed U": sepGradAboveSpeed_U,
        "BoundaryHeightDef": sepBHeight,
        "BoundaryHeightSpeed": sepBHeight,
        "Rossby" : sepRosby

        }

np.save(os.path.join(exportVarPath, 'Sorting Variabled'), exportVar)

#%%


sortedProfileGroups = []


profileArray= np.load(os.path.join(allDataProfilePath,'Single Array of Norm Unmatched Profile Unsorted.npy'),allow_pickle=True)
numProfile = len(profileArray)
gradientCheck = [ [] for _ in range(5) ]
for sortingType in sortBy:
    counter = 0
    lowerProfiles = []
    midProfiles = []
    higherProfiles = []
    
    for profile in profileArray:
        counter += 1
        print(sortingType,counter,'/',numProfile)
        '''
        profile[0] = normalised height
        profile[1] = normalised speed
        profile[2] = deflection
        profile[3] = height
        profile[4] = speed
        profile[5] = bearing
        profile[6] = U
        profile[7] = V
        profile[8] = W
        profile[9] = metadata 
        '''
        if sortingType == 'speed':
            boundaryLayerIndex = find_nearest(profile[3],referenceHeight)
            if np.nanmean(profile[4][boundaryLayerIndex-3:boundaryLayerIndex+3]) <= sepSpeed:
                lowerProfiles.append(profile)
            else:
                higherProfiles.append(profile)
        elif sortingType == 'gradientBelowDef':
            
            LowLayerIndex = find_nearest(profile[3],200 )
            HighLayerIndex = find_nearest(profile[3],1000)
            try:
                testHeight,testDef = cleaningArray(profile[3][LowLayerIndex:HighLayerIndex],profile[2][LowLayerIndex:HighLayerIndex])
                fit,cov = np.polyfit(testHeight,testDef,1,cov=True)
                
                gradientCheck[0].append(fit[0])

                if fit[0] <= sepGradBelowDef_L:
                    lowerProfiles.append(profile)
                elif sepGradBelowDef_L < fit[0] and fit[0] < sepGradBelowDef_U:
                    midProfiles.append(profile)
                elif sepGradBelowDef_U <= fit[0]:
                    higherProfiles.append(profile)
            except:
#                print("------ Error in linear fit Below, Profile not sorted ------")
                pass
        elif sortingType == 'gradientAboveDef':
            
    
            LowLayerIndex = find_nearest(profile[3],1800)
            HighLayerIndex = find_nearest(profile[3],3000)
            try:
                testHeight,testDef = cleaningArray(profile[3][LowLayerIndex:HighLayerIndex],profile[2][LowLayerIndex:HighLayerIndex])
                fit,cov = np.polyfit(testHeight,testDef,1,cov=True)                
                
                gradientCheck[1].append(fit[0])
                if fit[0] <= sepGradAboveDef_L:
                    lowerProfiles.append(profile)
                elif sepGradAboveDef_L < fit[0] and fit[0] < sepGradAboveDef_U:
                    midProfiles.append(profile)
                elif sepGradAboveDef_U <= fit[0]:
                    higherProfiles.append(profile)
            except:
#                print("------ Error in linear fit Above, Profile not sorted ------")
                pass
        elif sortingType == 'gradientBelowSpeed':
    
            LowLayerIndex = find_nearest(profile[3],200)
            HighLayerIndex = find_nearest(profile[3],1000)
            try:
                testHeight,testDef = cleaningArray(profile[3][LowLayerIndex:HighLayerIndex],profile[4][LowLayerIndex:HighLayerIndex])
                fit,cov = np.polyfit(testHeight,testDef,1,cov=True)                
                
                gradientCheck[2].append(fit[0])
                if fit[0] <= sepGradBelowSpeed_L:
                    lowerProfiles.append(profile)
                elif sepGradBelowSpeed_L < fit[0] and fit[0] < sepGradBelowSpeed_U:
                    midProfiles.append(profile)
                elif sepGradBelowSpeed_U <= fit[0]:
                    higherProfiles.append(profile)
            except:
#                print("------ Error in linear fit Above, Profile not sorted ------")
                pass
        elif sortingType == 'gradientAboveSpeed':
    
            LowLayerIndex = find_nearest(profile[3],1800)
            HighLayerIndex = find_nearest(profile[3],3000)
            try:
                testHeight,testDef = cleaningArray(profile[3][LowLayerIndex:HighLayerIndex],profile[4][LowLayerIndex:HighLayerIndex])
                fit,cov = np.polyfit(testHeight,testDef,1,cov=True)                
                
                gradientCheck[3].append(fit[0])
                if fit[0] <= sepGradAboveSpeed_L:
                    lowerProfiles.append(profile)
                elif sepGradAboveSpeed_L < fit[0] and fit[0] < sepGradAboveSpeed_U:
                    midProfiles.append(profile)
                elif sepGradAboveSpeed_U <= fit[0]:
                    higherProfiles.append(profile)
            except:
#                print("------ Error in linear fit Above, Profile not sorted ------")
                pass
        elif sortingType == 'BoundaryHeightDef':
            
            BHeight = findBoundaryHeight(profile[3],profile[2],200,1000,1800,3000)[0]
            

            if BHeight <= sepBHeight:
                lowerProfiles.append(profile)
            else:
                higherProfiles.append(profile)
                
        elif sortingType == 'BoundaryHeightSpeed':
            
            BHeight = findBoundaryHeight(profile[3],profile[4],200,1000,1800,3000)[0]
            

            if BHeight <= sepBHeight:
                lowerProfiles.append(profile)
            else:
                higherProfiles.append(profile)

    if not midProfiles:
        sortedProfileGroups.append([lowerProfiles,higherProfiles,sortingType])
    else:
        sortedProfileGroups.append([lowerProfiles,midProfiles,higherProfiles,sortingType])
            
        
np.save(os.path.join(allDataProfilePath, 'Sorted Single Array of Norm Unmatched Profile Unsorted'), sortedProfileGroups)

#%% Sorting matched Profiles


'''
sortBy = 'Rossby' = sort based on the rosby number of the profile [still needs work]
'''

stationPos = {
    'CCH': [22.3,114.0],
    'SHW' : [22.3,114.0],
    'SLW' : [22.3 , 113.9],
    'SSP' : [22.3, 114.2],
    } #Lat,Long




sortedProfileGroups = []

# R = 6371e3 #radius of earth in m
omega = 7.272e-5 #rad/s 

RoDist = []
    
profileArray= np.load(os.path.join(allDataMatchedPath,'Single Array of Norm matched Profile Unsorted.npy'),allow_pickle=True)

numProfile = len(profileArray)
gradientCheck = [ [] for _ in range(5) ]


lowerProfiles = []
midProfiles = []
higherProfiles = []


counter = 0
for profile in profileArray:
    counter += 1
    print(counter,'/',numProfile)
    '''
    profile[0] = normalised height
    profile[1] = normalised speed
    profile[2] = deflection
    profile[3] = height
    profile[4] = speed
    profile[5] = bearing
    profile[6] = U
    profile[7] = V
    profile[8] = W
    profile[9] = metadata 
    '''
    
    
    station = profile[-1][5]
    stationLL = stationPos[station]
    #r seperation in Km
    L = haversine(stationLL, [float(profile[-1][6]),float(profile[-1][7])], unit=Unit.KILOMETERS)      
    CPara = 2*omega*np.sin(np.deg2rad(stationLL[0]))
    
    boundaryLayerIndex = find_nearest(profile[3],referenceHeight)
    U = np.nanmean(profile[4][boundaryLayerIndex-3:boundaryLayerIndex+3])
    
    Ro = U/(L*CPara)
    RoDist.append(Ro)

    if Ro <= sepRosby:
        lowerProfiles.append(profile)
    elif Ro > sepRosby:
        higherProfiles.append(profile)
    '''
    Need to now just calculate the rossby number:
        serperate the files based on the Ro
        save the Ro in a seperate file to see its distribution
    '''
if not midProfiles:
    sortedProfileGroups.append([lowerProfiles,higherProfiles,"Rossby"])
else:
    sortedProfileGroups.append([lowerProfiles,midProfiles,higherProfiles,"Rossby"])
    

np.save(os.path.join(allDataMatchedPath, 'Sorted Single Array of Norm matched Profile Unsorted'), sortedProfileGroups)

    
    


