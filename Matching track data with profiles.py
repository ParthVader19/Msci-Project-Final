# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 11:56:33 2021

@author: p_vag
"""
import re
import numpy as np
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import datetime 
#%%
"""
Filepaths
"""
trackDataPath = r'D:\MSci2020\Current Version\MSci2020\TrackData.csv'
cleanProfileDataPath = r'D:\MSci2020\Current Version\MSci2020\Clean Data Rosby\Profiles'
cleanDataTrackPath = r'D:\MSci2020\Current Version\MSci2020\Clean Data Rosby\Track'
exportMatchedDataPath = r'D:\MSci2020\Current Version\MSci2020\Clean Data Rosby\Matched'


trackData = np.array(pd.read_csv(trackDataPath))
#%% seperating the track data based on the storm

allProfilesTrack = []
currentStorm = trackData[0][5]
checkStorm = trackData[0][5]
yyyy = trackData[0][1]
profileTrack = [[] for x in range(np.shape(trackData)[1])]

changeToFloat = [8,9,59,60]

for i in range(0,np.shape(trackData)[0]):
    print(i)
    currentStorm = trackData[i][5]
    if currentStorm == checkStorm:#Check to see when the storm in the data has changed
        for j in range(np.shape(trackData)[1]): #Appending all data in the row to the profileTrack array
            profileTrack[j].append(trackData[i][j])
        yyyy = trackData[i][1] #year of storm
        
        for k in changeToFloat: #changing USA and HKO Long and Lat to floats as everything is imported as strings
            for m in  range(len(profileTrack[k])):
                if profileTrack[k][m] != ' ' :
                    profileTrack[k][m] = np.float(profileTrack[k][m])
                else: 
                    profileTrack[k][m] = np.nan
        
        if i == np.shape(trackData)[0] - 1: #if on final line of the trackData, save the track data
            file_Name = [checkStorm,str(yyyy)]
            np.save(os.path.join(cleanDataTrackPath, " ".join(file_Name)), profileTrack)
        
    else:#if the storm has changed: 1) resetcheckStorm, 2) save data from previous, 3)set allProfilesTrack to empty, 4) perform previous computation
        print(checkStorm)
        
        file_Name = [checkStorm,str(yyyy)]
        np.save(os.path.join(cleanDataTrackPath, " ".join(file_Name)), profileTrack)
        
        checkStorm = trackData[i][5]
        
        # allProfilesTrack.append(profileTrack)
        
        profileTrack = [[] for x in range(np.shape(trackData)[1])]
        for j in range(np.shape(trackData)[1]):
            profileTrack[j].append(trackData[i][j])
            
        for k in changeToFloat: #changing USA and HKO Long and Lat to floats as everything is imported as strings
            for m in  range(len(profileTrack[k])):
                if profileTrack[k][m] != ' ' :
                    profileTrack[k][m] = np.float(profileTrack[k][m])
                else: 
                    profileTrack[k][m] = np.nan
            
#%% Plotting track

counter = 0

plt.figure()
for file in os.listdir(cleanDataTrackPath):
    if counter < 5:
        filePathTrack = os.path.join(cleanDataTrackPath,file)
        storm = np.load(filePathTrack,allow_pickle = True)
        plt.plot(storm[8].astype(np.float),storm[9].astype(np.float),label=storm[5][0]+storm[1][0]  )
        plt.legend()
        counter += 1
        # plt.xticks(np.arange(min(storm[8]), max(storm[8])+1, 1.0))
        # plt.yticks(np.arange(min(storm[9]), max(storm[9])+1, 1.0))

plt.xlabel('LAT')
plt.ylabel('LONG')
plt.show()
    
#%% Functions

def turnToDateTimeFormat(stringArray): #Turns the data and time into a usable format
    return str(stringArray[1] + '/' + stringArray[2] + '/' + stringArray[3] + ' ' + stringArray[4][0:2] + ':' + stringArray[4][2:4])

def LinearInter(long,lat,num,timeArray,deltaTime):
    longInter = []
    latInter = []
    timeInter = [timeArray[0]]
    for i in range(len(long)-1):
        longInter.append(np.linspace(long[i],long[i+1],num=num,endpoint=False))
        latInter.append(np.linspace(lat[i],lat[i+1],num=num,endpoint=False))
        
        if i == len(long)-2:
            pass
        
    longInter = np.array(longInter).flatten()
    latInter = np.array(latInter).flatten()
    
    for i in range(len(longInter)-1):
        timeInter.append(timeInter[-1] + datetime.timedelta(minutes=deltaTime))

    return longInter,latInter,timeInter    

#%%


'''
index for trackdata:
    1 = year
    5 = storm name
    6 = date and time Eg. 10/07/2010  06:00:00
    8 = USA LAt
    9 = USA Long
    59 = HKO Lat
    60 = HKO Long
'''
# for subfolder in os.listdir(cleanProfileDataPath):
#     subfolderPath = os.path.join(cleanProfileDataPath, subfolder)
    
#     for profileFile in os.listdir(subfolderPath):
#         profilePath = os.path.join(subfolderPath, profileFile)

#         singleStormProfile = np.load(profilePath,allow_pickle = True )
        
#         start = turnToDateTimeFormat(singleStormProfile[0][0][-1]) #earliest time for profiles
#         end = turnToDateTimeFormat(singleStormProfile[-1][-1][-1]) #lastest time for profiles
        
        
for trackFile in os.listdir(cleanDataTrackPath):
    
    stormName_track = trackFile.split()[0]
    stormYear_track = trackFile.split()[1].split('.')[0]
    for subfolder in os.listdir(cleanProfileDataPath):
        subfolderPath = os.path.join(cleanProfileDataPath, subfolder)
        for profileFile in os.listdir(subfolderPath):
            stormName_profile = profileFile.split()[0]
            stormYear_profile = profileFile.split()[1]
            
            if stormName_track == stormName_profile and stormYear_track == stormYear_profile:
                print("Track data:",trackFile,'/',"Profile data:",profileFile)

                trackPath = os.path.join(cleanDataTrackPath, trackFile)
                profilePath = os.path.join(subfolderPath, profileFile)
                
                singleStormTrack = np.load(trackPath,allow_pickle = True )
                singleStormProfile = np.load(profilePath,allow_pickle = True )
                
                start = turnToDateTimeFormat(singleStormProfile[0][0][-1]) #earliest time for profiles
                end = turnToDateTimeFormat(singleStormProfile[-1][-1][-1]) #lastest time for profiles
                
                profileStartFormatted = datetime.datetime.strptime(start,"%d/%m/%Y %H:%M")
                profileEndFormatted = datetime.datetime.strptime(end,"%d/%m/%Y %H:%M")
                
                if profileEndFormatted.time() > datetime.datetime.strptime("00:00","%H:%M").time() :
                    profileEndFormatted += datetime.timedelta(days=1)
                    
                TrackTime = singleStormTrack[6]
                dateTimeFormated = []
                for timeSingle in TrackTime: #formatting track time and date
                    t = datetime.datetime.strptime(timeSingle,"%d/%m/%Y %H:%M")
                    dateTimeFormated.append(t)
                
                smallerTrackdataIndex = []
                for i in range(np.shape(dateTimeFormated)[0]): #checking which track data fall within the range of the profiles
                    '''
                    NEED TO CHECK: Does the track data always happens over a longer time than profile?? Currently (with Conson 2010) it is assumed so.
                    '''
                    if dateTimeFormated[i] >= profileStartFormatted and dateTimeFormated[i] <= profileEndFormatted:
                        smallerTrackdataIndex.append(i)
                        # print(dateTimeFormated[i],i)
                
                #collecting data that fits in the time of the profile data. All including 1 data above and below the range
                # smallerTrackdata = [singleStormTrack[x][smallerTrackdataIndex[0]-1:smallerTrackdataIndex[-1]+2] for x in range(len(singleStormTrack))]
                # smallerTrackdataTime = dateTimeFormated[smallerTrackdataIndex[0]-1:smallerTrackdataIndex[-1]+2]
                smallerTrackdata = singleStormTrack
                smallerTrackdataTime = dateTimeFormated

                
                #time steps for the profiles in minutes (likely)
                profileTimeStep = float(singleStormProfile[0][1][-1][4]) - float(singleStormProfile[0][0][-1][4])
                
                delta = dateTimeFormated[1]-dateTimeFormated[0] #difference between subsquent time entries in track data (in seconds)
                numToInterp = int(delta.seconds // (60)) #Hight resoltuon,how many values need to be interpolated between subsquent entries (based on profile time step in minutes)
                
                #interpolated Lat,Long and time
                #High resoltution: USA
                InterLong, InterLat, InterTime = LinearInter(smallerTrackdata[9].astype(np.float),smallerTrackdata[8].astype(np.float),num=numToInterp,timeArray = smallerTrackdataTime,deltaTime = 1) 
                #HKO
                InterLongHKO, InterLatHKO, InterTimeHKO = LinearInter(smallerTrackdata[60].astype(np.float),smallerTrackdata[59].astype(np.float),num=numToInterp,timeArray = smallerTrackdataTime,deltaTime = 1) 
                
                #matching interpoated track time with profile time
                
                if len(singleStormProfile) > 1:
                    profileDataSingleArray = np.concatenate(singleStormProfile)
                else:
                    profileDataSingleArray = singleStormProfile[0]
                
                profileTimeArray = [datetime.datetime.strptime(turnToDateTimeFormat(profileDataSingleArray[p][-1]),"%d/%m/%Y %H:%M") for p in range(len(profileDataSingleArray))]
                        
                # matchingStartIndex = InterTime.index(profileTimeArray[0])
                # matchingStopIndex = InterTime.index(profileTimeArray[-1])
                    
                
                for g in range(len(profileTimeArray)):
                    try:
                        matchingIndex = InterTime.index(profileTimeArray[g]) #index of interpolated data that matches profiletime
                        profileDataSingleArray[g][-1] = np.append(profileDataSingleArray[g][-1],[InterLat[matchingIndex],InterLong[matchingIndex],InterLatHKO[matchingIndex],InterLongHKO[matchingIndex]])
                    except:
                        # print("profile time does not match Track time")
                        profileDataSingleArray[g][-1] = np.append(profileDataSingleArray[g][-1],[np.nan,np.nan,np.nan,np.nan])
       
                    
                
                file_Name = [profileFile,"Matched"]
                np.save(os.path.join(exportMatchedDataPath, " ".join(file_Name)), profileDataSingleArray)
                
            else:
                # print("error")
                pass

    
    
#%%  previous verson of Matching code for reference

savefolderPathSingle = r'D:\MSci2020\Current Version\MSci2020\Clean Data Rosby\Profiles\CONSON2010'
singleStormTrack = np.load(os.path.join(cleanDataTrackPath,"CONSON 2010.npy"),allow_pickle = True )
singleStormProfile = np.load(os.path.join(savefolderPathSingle,"CONSON 2010 CCH w1b.npy"),allow_pickle = True )

start = turnToDateTimeFormat(singleStormProfile[0][0][-1]) #earliest time for profiles
end = turnToDateTimeFormat(singleStormProfile[-1][-1][-1]) #lastest time for profiles

profileStartFormatted = datetime.datetime.strptime(start,"%d/%m/%Y %H:%M")
profileEndFormatted = datetime.datetime.strptime(end,"%d/%m/%Y %H:%M")

# Some profile data (for a given file) goes beyond 24 hrs, so if it does, it adds a data to the latest time.
if profileEndFormatted.time() > datetime.datetime.strptime("00:00","%H:%M").time() :
    profileEndFormatted += datetime.timedelta(days=1)

TrackTime = singleStormTrack[6]
dateTimeFormated = []
for timeSingle in TrackTime: #formatting track time and date
    t = datetime.datetime.strptime(timeSingle,"%d/%m/%Y %H:%M")
    dateTimeFormated.append(t)

smallerTrackdataIndex = []
for i in range(np.shape(dateTimeFormated)[0]): #checking which track data fall within the range of the profiles
    '''
    NEED TO CHECK: Does the track data always happens over a longer time than profile?? Currently (with Conson 2010) it is assumed so.
    '''
    if dateTimeFormated[i] >= profileStartFormatted and dateTimeFormated[i] <= profileEndFormatted:
        smallerTrackdataIndex.append(i)
        print(dateTimeFormated[i],i)
        

#collecting data that fits in the time of the profile data. All including 1 data above and below the range
smallerTrackdata = [singleStormTrack[x][smallerTrackdataIndex[0]-1:smallerTrackdataIndex[-1]+2] for x in range(len(singleStormTrack))]
smallerTrackdataTime = dateTimeFormated[smallerTrackdataIndex[0]-1:smallerTrackdataIndex[-1]+2]

#time steps for the profiles in minutes (likely)
profileTimeStep = float(singleStormProfile[0][1][-1][4]) - float(singleStormProfile[0][0][-1][4])
'''
Need to check if the timestep is always constant
'''



delta = dateTimeFormated[1]-dateTimeFormated[0] #difference between subsquent time entries in track data (in seconds)
numToInterp = int(delta.seconds // (60)) #Hight resoltuon,how many values need to be interpolated between subsquent entries (based on profile time step in minutes)

#interpolated Lat,Long and time
#High resoltution: USA
InterLong, InterLat, InterTime = LinearInter(smallerTrackdata[9].astype(np.float),smallerTrackdata[8].astype(np.float),num=numToInterp,timeArray = smallerTrackdataTime,deltaTime = 1) 
#HKO
InterLongHKO, InterLatHKO, InterTimeHKO = LinearInter(smallerTrackdata[60].astype(np.float),smallerTrackdata[59].astype(np.float),num=numToInterp,timeArray = smallerTrackdataTime,deltaTime = 1) 

#matching interpoated track time with profile time

if len(singleStormProfile) > 1:
    profileDataSingleArray = np.concatenate(singleStormProfile)
else:
    profileDataSingleArray = singleStormProfile[0]

profileTimeArray = [datetime.datetime.strptime(turnToDateTimeFormat(profileDataSingleArray[p][-1]),"%d/%m/%Y %H:%M") for p in range(len(profileDataSingleArray))]
        
# matchingStartIndex = InterTime.index(profileTimeArray[0])
# matchingStopIndex = InterTime.index(profileTimeArray[-1])
    

for g in range(len(profileTimeArray)):
    matchingIndex = InterTime.index(profileTimeArray[g]) #index of interpolated data that matches profiletime
    profileDataSingleArray[g][-1] = np.append(profileDataSingleArray[g][-1],[InterLat[matchingIndex],InterLong[matchingIndex],InterLatHKO[matchingIndex],InterLongHKO[matchingIndex]])
    
#%%
''' Eg. Plotting
USALat = np.array([profileDataSingleArray[g][-1][8] for g in range(len(profileDataSingleArray))]).astype(np.float)
USALong = np.array([profileDataSingleArray[g][-1][9] for g in range(len(profileDataSingleArray))]).astype(np.float)

plt.figure()
plt.scatter(USALat,USALong,c='b',marker='.',label="interp with profile")
plt.scatter(smallerTrackdata[59].astype(np.float),smallerTrackdata[60].astype(np.float),c='r',marker='x',label='data')
plt.xlabel('LAT')
plt.ylabel('LONG')
plt.title('HKO')
plt.legend()
plt.show()
'''

#%% Plotting track

counter = 0

plt.figure()
for file in os.listdir(cleanDataTrackPath):
    if counter < 5:
        filePathTrack = os.path.join(cleanDataTrackPath,file)
        storm = np.load(filePathTrack,allow_pickle = True)
        plt.plot(storm[8].astype(np.float),storm[9].astype(np.float),label=storm[5][0]+storm[1][0]  )
        plt.legend()
        counter += 1
        # plt.xticks(np.arange(min(storm[8]), max(storm[8])+1, 1.0))
        # plt.yticks(np.arange(min(storm[9]), max(storm[9])+1, 1.0))

plt.xlabel('LAT')
plt.ylabel('LONG')
plt.show()