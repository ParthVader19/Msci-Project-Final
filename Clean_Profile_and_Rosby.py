"""
Rosby Number
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
cleanDataPath = r'D:\MSci2020\Current Version\MSci2020\Clean Data Rosby\Profiles'
cleanDataTrackPath = r'D:\MSci2020\Current Version\MSci2020\Clean Data Rosby\Track'
dataMainPath = r'D:\MSci2020\Current Version\MSci2020\2010-2019 TC Data'
trackDataPath = r'D:\MSci2020\Current Version\MSci2020\TrackData.csv'
#%% Functions
def extract_nums(text):
    for item in text.split(' '):
        try:
            yield float(item)
        except ValueError:
            pass

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
fileTypeArray = [ 'W1A', 'W1B', 'W3A', 'W3B', 'w1a', 'w1b','w3a', 'w3b']
#os.listdir(dataMainPath)
folder_array = [
 #    '20100715-0716 CONSON',
 # '20100720-0722 CHANTHU',
 # '20100829-0903 LIONROCK',
 # '20100919-0921 FANPI',
 # '20101020-1022 MEGI',
 # '20110610-0611 SARIKA',
 # '20110620-0623 HAIMA',
 # '20110728-0729 NOCK-TEN',
 # '20110927-0930 NESAT',
 # '20111002-1003 NALGAE',
 # '20120617-0619 TALIM',
 # '20120628-0630 DOKSURI',
 # '20120721-0724 VICENTE',
 # '20120815-0817 KAI-TAK',
 # '20120824-0826 TEMBIN',
 # '20130621-0622 BEBINCA',
 # '20130630-0702 RUMBIA',
 # '20130717-0718 CIMARON',
 # '20130801-0802 JEBI',
 # '20130812-0815 UTOR',
 # '20130921-0923 USAGI',
 # '20131101-1103 KROSA',
 # '20140614-0615 HAGIBIS',
 # '20140716-0719 RAMMASUN',
 # '20140907-0908 NONAME',
 # '20140914-0917 KALMAEGI',
 # '20150621-0623 KUJIRA',
 # '20150708-0710 LINFA',
 # '20151002-1005 MUJIGAE',
 # '20160526-0527 NONAME',
 # '20160726-0726 MIRINAE',
 '20160731-0802 NIDA',
 '20160817-0818 DIANMU',
 '20160914-0915 MERANTI',
 '20160928-0928 MEGI',
 '20161006-1009 AERE',
 '20161016-1018 SARIKA',
 '20161020-1021 HAIMA',
 '20170611-0613 MERBOK',
 '20170722-0723 ROKE',
 '20170822-0823 HATO',
 '20170826-0827 PAKHAR',
 '20170902-0904 MAWAR',
 '20170923-0924 NONAME',
 '20171014-1014 KHANUN',
 '20180605-0608 EWINIAR',
 '20180717-0724 SON-TINH',
 '20180809-0815 BEBINCA',
 '20180911-0913 BARIJAT',
 '20180914-0917 MANGKHUT',
 '20181031-1102 YUTU',
 '20190702-0703 MUN',
 '20190730-0802 WIPHA',
 '20190824-0825 BAILU',
 '20190828-0829 PODUL',
 '20190901-0902 KAJIKI']

for folder in os.listdir(dataMainPath):
    # if folder == "20100715-0716 CONSON": #currently only testing for 1 storm
    if folder in folder_array:
        print(folder)
        YYYY = folder[0:4]
        storm = folder.split()[1]
        subfolderPath = os.path.join(dataMainPath, folder)
        savefolderPath = os.path.join(cleanDataPath, storm+YYYY)
        if not os.path.exists(savefolderPath): #Creating folder for the export files for each storm
            os.makedirs(savefolderPath)
        for subfolder in os.listdir(subfolderPath):
            print(folder,subfolder)
            station = subfolder[3:6] #station name
            fileFolderPath = os.path.join(subfolderPath, subfolder)
            files = [filename for filename in os.listdir(fileFolderPath)] #generating an array of all files in the folder for the station 
            files.sort(key=lambda f: os.path.splitext(f)[1]) #sorting the above array based on the extention only (not name)
            
            allProfilesAllDays = [] #where all profiles for a given file extenstion (in order of date) is saved
            checkFileExtenstion = files[0][-3:] #Check for when the file extenstion changes
            
            for filename in files:
                
                fileExtension = filename[-3:]
                if fileExtension in fileTypeArray:
                    if fileExtension == checkFileExtenstion:
                        
                        print(filename)
                        DD = filename[6:8]
                        MM = filename[4:6]
                        data = pd.read_fwf(os.path.join(fileFolderPath, filename), skiprows=35,sep=" ", header=None)
                        data = np.array(data)

                            
                        heightDataLen = int(data[0,1]) #number of data in each profile/timeshot
                        
                        allProfiles = []
                        for i in range(0,np.shape(data)[0],heightDataLen+1):
                            
                            
                            t = '%04d' % float(data[i,0]) 
                            PofileTime = t[-4:]
                            
                            profile = [[ [] for y in range(heightDataLen)] for x in range(13+1)] #array of empty arrays where all the data for a given profile will be saved
                            
                            for j in range(heightDataLen):
                                for k in range(np.shape(profile)[0]): #first setting all values in the profile as Nan to avoid computation when rejecting invalid data
                                    profile[k][j] = np.nan
                                
                                profile[1][j] = data[i+j+1,1] #height
                                
                                if data[i+j+1,0] == 0: #check for QC Code
                                    bool_arr = data[i+j+1] > -500 #check for Data Code
                                    output = np.where(bool_arr)[0] #checking where Data Code check/data in the row is valid
                                    
                                    for index in output:
                                        profile[index][j] = data[i+j+1,index] #correcting values in saved profile from Nan to the data given when Data code check passed
                                              
                            metaData = [storm,DD,MM,YYYY,PofileTime,station] #meta data for each profile, eg. data, station name, storm, time for it profile
                            profile[-1] = metaData
                            
                            allProfiles.append(profile)
                            
                        # allProfilesType.append(allProfiles)
                        allProfilesAllDays.append(allProfiles)
                        
                        if fileExtension == files[-1][-3:] and checkFileExtenstion in fileTypeArray: #checking if the final file in array is reached: if so then save
                            file_Name = [storm,YYYY,station,checkFileExtenstion]
                            np.save(os.path.join(savefolderPath, " ".join(file_Name)), allProfilesAllDays)
                            
                    else: #Check for when the file extenstion type is changed: 1) save the data so far, 2) reset checkFileExtenstion to current and allProfilesAllDays to empty, 3) perform same computation as before..
                        if checkFileExtenstion in fileTypeArray:
                            file_Name = [storm,YYYY,station,checkFileExtenstion]
                            np.save(os.path.join(savefolderPath, " ".join(file_Name)), allProfilesAllDays)
                        
                        checkFileExtenstion = filename[-3:]
                        
                        allProfilesAllDays = []
                        
                        print(filename)
                        DD = filename[6:8]
                        MM = filename[4:6]
                        data = pd.read_fwf(os.path.join(fileFolderPath, filename), skiprows=35,sep=" ", header=None)
                        data = np.array(data)
                        heightDataLen = int(data[0,1]) #number of data in each profile/timeshoot
                        
                        allProfiles = []
                        for i in range(0,np.shape(data)[0],heightDataLen+1):
                            
                            t = '%04d' % float(data[i,0]) 
                            PofileTime = t[-4:]
                            
                            profile = [[ [] for y in range(heightDataLen)] for x in range(13+1)]
                            
                            
                            for j in range(heightDataLen):
                                for k in range(np.shape(profile)[0]): 
                                    profile[k][j] = np.nan
                                
                                profile[1][j] = data[i+j+1,1]
                                
                                if data[i+j+1,0] == 0:
                                    bool_arr = data[i+j+1] > -500
                                    output = np.where(bool_arr)[0]
                                    
                                    for index in output:
                                        profile[index][j] = data[i+j+1,index]
                                              
                            metaData = [storm,DD,MM,YYYY,PofileTime,station]
                            profile[-1] = metaData
                            
                            allProfiles.append(profile)
                            
                        # allProfilesType.append(allProfiles)
                        allProfilesAllDays.append(allProfiles)
                        
                        
                        
                else:
                    print("Invalid file exxtension:",fileExtension)
                        
                    
'''
np.concatenate() for data with multiple days
'''
                        
                        
