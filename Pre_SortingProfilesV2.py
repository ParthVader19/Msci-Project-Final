import numpy as np
import matplotlib.pyplot as plt
import os
import time
import numpy.ma as ma
import datetime 
import random
#import concurrent.futures
#from scipy.optimize import curve_fit


MatchedDataMainPath = r'C:\MSci2020\Current Version\MSci2020\Clean Data Rosby\Matched'
ProfileDataMainPath = r'C:\MSci2020\Current Version\MSci2020\Clean Data Rosby\Profiles'
allDataMatchedExportPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Matched'
allDataExportPath = r'C:\MSci2020\Current Version\MSci2020\ProfilesV3\Profiles'

#%% Functions

def find_nearest(array, value):
    '''
    Finds the index of the entry in the array closest to the "value" input
    '''
    array = np.array(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def cleaningArray(height,testArray):
    indices = np.argwhere(np.isnan(testArray)).flatten()
    newHeight = np.delete(height,indices)
    newTestArray = np.delete(testArray,indices)
    return newHeight,newTestArray

def returnMin(timeStr):
    return float(timeStr[:2])*60 + float(timeStr[2:])

def avgAtHeightFORTIMEAVERAGE(height,arraySlices):
    WS = [arraySlices[i][0] for i in range(0,np.shape(arraySlices)[0])]
    WD = [arraySlices[i][1] for i in range(0,np.shape(arraySlices)[0])]
    U = [arraySlices[i][2] for i in range(0,np.shape(arraySlices)[0])]
    V = [arraySlices[i][3] for i in range(0,np.shape(arraySlices)[0])]
    W = [arraySlices[i][4] for i in range(0,np.shape(arraySlices)[0])]
    

    combinedWS = np.nanmedian(WS)
    combinedWD = np.nanmedian(WD)
    combinedU = np.nanmedian(U)
    combinedV = np.nanmedian(V)
    combinedW = np.nanmedian(W)
    #combinedWSErr = np.nanstd(WS)/ np.sqrt(np.count_nonzero(~np.isnan(WS)))
    #combinedWDErr = np.nanstd(WD)/ np.sqrt(np.count_nonzero(~np.isnan(WD)))
    
    
    return height,combinedWS,combinedWD,combinedU,combinedV,combinedW#,combinedWSErr,combinedWDErr
#%% TESTING FOR AUTOCORRELATION
# done 1.0, 0.8, 0.6, 0.4, 0.2, 0.0
terminateCorr = 0.0 #min level of acceptable autocorrelation: Lower the better
referenceHeight = 1500

filePath = 0
profileMatchedUnsorted = []
noProfiles = 0

BoundaryHeightBias = 0

noFilesInPath = len(os.listdir(MatchedDataMainPath))
counter = 0

savePart = 0

# Collecting the profiles in unsorted (big) groups seperate files
'''
Saving all profiles in a single array and saving the array takes a lot of time and 
takes up all the RAM avaliable. Currently, Saving arrays in groups of 50,000 profiles and saving them.
'''
shiftArray = []
autoCorrArray = []

indepTimeArray = []
for file in os.listdir(MatchedDataMainPath):
    # if file.split()[0] == 'YUTU':
        # if file.split()[2] == 'SSP' and file.split()[3].split('.')[0] == 'W3B':
            counter += 1
            print('filename:',file,counter,'/',noFilesInPath)
            timeStart= time.perf_counter()
            filePath = os.path.join(MatchedDataMainPath,file)
            data = np.load(filePath,allow_pickle=True)
            
            
            #The average timestep between subsequent profile in data
            avgTimeshiftArray = []
            for i in range(np.shape(data)[0]-1):
                diff = returnMin(data[i+1][-1][4]) - returnMin(data[i][-1][4])
                if diff > 0:
                    avgTimeshiftArray.append(diff)  
            avgTimeshiftInterval = np.nanmedian(avgTimeshiftArray)
            boundaryLayerIndex = find_nearest(data[0][1], referenceHeight)
            #Array of reference speeds of each [profiles]
            URefArray = [np.nanmedian(data[i][2][boundaryLayerIndex-2:boundaryLayerIndex+2]) for i in range(np.shape(data)[0])]
            
            autocorr = []
            maxshift = len(URefArray)-1
            
            indepTimeInterval = 0
            for shift in range(1,maxshift):
                A = URefArray[:-shift]
                B = URefArray[shift:]
                corr = ma.corrcoef(ma.masked_invalid(A), ma.masked_invalid(B))[0,1]
                if corr <= terminateCorr: #determines the time interval for which the autocorrelation is for the first time lower than terminateCorr
                    indepTimeInterval = shift*avgTimeshiftInterval
                    break
            #     corr = np.corrcoef(URefArray[:-shift],URefArray[shift:])[0,1]
            #     autocorr.append(corr)
            # shiftArray.append(range(1,maxshift))
            # autoCorrArray.append(autocorr)
            indepTimeArray.append([ " ".join([data[0][-1][0]+data[0][-1][3]]),indepTimeInterval])
            
            
            '''
            plt.ylabel("AutoCorrelation of Reference speed")
            plt.xlabel("Shift")
            plt.grid()
            plt.plot(range(1,maxshift),autocorr,'-',label = " ".join([file.split()[0],file.split()[1],'%s' % float('%.3g' % avgTimeshiftInterval)]))
            plt.legend()
            '''
            cumcumulativeTime = 0
            independentTimeBlock = []
            for i in range(np.shape(data)[0]-1):
                diff = returnMin(data[i+1][-1][4]) - returnMin(data[i][-1][4])
                if diff > 0:
                    cumcumulativeTime += diff
                    independentTimeBlock.append(data[i])
                    

                if cumcumulativeTime >= indepTimeInterval:
                    #print("----number of profiles in independent block: %s (%s,%s) ----" % (len(independentTimeBlock),indepTimeInterval,diff))
                    noProfiles += 1
                    initialTime = datetime.datetime(day=int(independentTimeBlock[0][-1][1]),month=int(independentTimeBlock[0][-1][2]),year=int(independentTimeBlock[0][-1][3]),hour = int(independentTimeBlock[0][-1][4][:2]),minute = int(independentTimeBlock[0][-1][4][2:]))
                    medianTime = initialTime + datetime.timedelta(minutes = int(indepTimeInterval/2))
                    
                    longAvg = np.nanmedian([float(independentTimeBlock[g][-1][6]) for g in range(np.shape(independentTimeBlock)[0])])
                    latAvg = np.nanmedian([float(independentTimeBlock[g][-1][7]) for g in range(np.shape(independentTimeBlock)[0])])
                        
                    metaMaterial = [independentTimeBlock[0][-1][0],medianTime,independentTimeBlock[0][-1][5],longAvg,latAvg]
                    avgHeight = []
                    avgWS = []
                    avgWD = []
                    avgU = []
                    avgV = []
                    avgW = []
                    
                    for l in range(np.shape(independentTimeBlock[0][0])[0]):
                        heightAvg,WSAvg,WDAvg,UAvg,VAvg,WAvg= avgAtHeightFORTIMEAVERAGE(independentTimeBlock[0][1][l], [[independentTimeBlock[k][2][l],independentTimeBlock[k][3][l],independentTimeBlock[k][4][l],independentTimeBlock[k][5][l],independentTimeBlock[k][6][l]] for k in range(np.shape(independentTimeBlock)[0])])
                        # print(heightAvg)
                        avgHeight.append(heightAvg)
                        avgWS.append(WSAvg)
                        avgWD.append(WDAvg)
                        avgU.append(UAvg)
                        avgV.append(VAvg)
                        avgW.append(WAvg)
                        
                        pass
                        
                    profileMatchedUnsorted.append([avgHeight,avgWS,avgWD,avgU,avgV,avgW,metaMaterial])
                    cumcumulativeTime = 0
                    independentTimeBlock = []
            # timeStop = time.perf_counter()
            # print('time:',timeStop - timeStart)
            
            print('Average Time interval between profiles: %s mins' % float('%.3g' % avgTimeshiftInterval))
            print("Time interval for independent profiles: ",'%s mins' % float('%.3g' % indepTimeInterval))
            print("Number of profiles so far: ",noProfiles)
            print('----------------------')
        

if noProfiles > 50000:
    array_to_save = random.sample(profileMatchedUnsorted, 50000)
else:
    array_to_save = profileMatchedUnsorted


print("No. of profiles: ",len(array_to_save))
np.save(os.path.join(allDataMatchedExportPath, 'AutoCorrected Each profiles Not_Sorted Not_Binned Matched AutoCorr = %s ' %float('%.3g' % terminateCorr)), array_to_save,allow_pickle=True)

        


#%% Collecting all matched profiles into a single array
filePath = 0
profileMatchedUnsorted = []
noProfiles = 0

referenceHeight = 0
BoundaryHeightBias = 0

noFilesInPath = len(os.listdir(MatchedDataMainPath))
counter = 0

savePart = 0

# Collecting the profiles in unsorted (big) groups seperate files
'''
Saving all profiles in a single array and saving the array takes a lot of time and 
takes up all the RAM avaliable. Currently, Saving arrays in groups of 50,000 profiles and saving them.
'''
for file in os.listdir(MatchedDataMainPath):
    # if file.split()[0] == 'YUTU':
        if noProfiles < 50000:
            counter += 1
            print('filename:',file,counter,'/',noFilesInPath)
            timeStart= time.perf_counter()
            filePath = os.path.join(MatchedDataMainPath,file)
            data = np.load(filePath,allow_pickle=True)
        #        print('length of file:',len(data))
            for profile in data:
                # print('top height data:',profile[1][-1],len(profile[0]))
                noProfiles += 1
                profileMatchedUnsorted.append(profile)
            timeStop = time.perf_counter()
            print('time:',timeStop - timeStart)
        else:
            np.save(os.path.join(allDataMatchedExportPath, 'Part {} Each profiles Not_Sorted Not_Binned Matched '.format(savePart)), profileMatchedUnsorted,allow_pickle=True)
            savePart += 1
            
            profileMatchedUnsorted = []
            noProfiles = 0
            
            counter += 1
            print('filename:',file,counter,'/',noFilesInPath)
            timeStart= time.perf_counter()
            filePath = os.path.join(MatchedDataMainPath,file)
            data = np.load(filePath,allow_pickle=True)
        #        print('length of file:',len(data))
            for profile in data:
                # print('top height data:',profile[1][-1],len(profile[0]))
                noProfiles += 1
                profileMatchedUnsorted.append(profile)
            timeStop = time.perf_counter()
            print('time:',timeStop - timeStart)
            
if noProfiles > 0:
    np.save(os.path.join(allDataMatchedExportPath, 'Part {} Each profiles Not_Sorted Not_Binned Matched '.format(savePart)), profileMatchedUnsorted,allow_pickle=True)

        
#%% Collecting all Profile [without track information] profiles into a single array
#Use when analysis anything not requiring track information/ rosby number
filePath = 0
profileUnsorted = []
noProfiles = 0

referenceHeight = 0
BoundaryHeightBias = 0




savePart = 0

# Collecting the profiles in unsorted (big) groups seperate files
'''
Saving all profiles in a single array and saving the array takes a lot of time and 
takes up all the RAM avaliable. Currently, Saving arrays in groups of 50,000 profiles and saving them.
'''
for folder in os.listdir(ProfileDataMainPath):
    counter = 0
    folderPath = os.path.join(ProfileDataMainPath,folder)
    noFilesInPath = len(os.listdir(folderPath))
    for file in os.listdir(folderPath):
        if noProfiles < 50000:
            counter += 1
            print('filename:',file,counter,'/',noFilesInPath,noProfiles)
            timeStart= time.perf_counter()
            filePath = os.path.join(folderPath,file)
            data = np.load(filePath,allow_pickle=True)
            print(np.shape(data))
            if len(data) > 1:
                data = np.concatenate(data)
            else:
                data = data[0]
                
            for profile in data:
                # print('top height data:',profile[1][-1],len(profile[0]))
                noProfiles += 1
                profileUnsorted.append(profile)
            timeStop = time.perf_counter()
            print('time:',timeStop - timeStart)
        else:
            np.save(os.path.join(allDataExportPath, 'Part {} Each profiles Not_Sorted Not_Binned Just_Porfiles '.format(savePart)), profileUnsorted,allow_pickle=True)
            savePart += 1
            
            profileUnsorted = []
            noProfiles = 0
            
            counter += 1
            print('filename:',file,counter,'/',noFilesInPath)
            timeStart= time.perf_counter()
            filePath = os.path.join(folderPath,file)
            data = np.load(filePath,allow_pickle=True)
            print(np.shape(data))
            if len(data) > 1:
                data = np.concatenate(data)
            else:
                data = data[0]
                
            for profile in data:
                # print('top height data:',profile[1][-1],len(profile[0]))
                noProfiles += 1
                profileUnsorted.append(profile)
            timeStop = time.perf_counter()
            print('time:',timeStop - timeStart)
            
if noProfiles > 0:
    np.save(os.path.join(allDataExportPath, 'Part {} Each profiles Not_Sorted Not_Binned Just_Porfiles '.format(savePart)), profileUnsorted,allow_pickle=True)
