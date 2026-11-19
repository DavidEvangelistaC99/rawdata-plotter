
#from logging.config import fileConfig
import numpy as np

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import os
#from scipy import signal
#import time
#import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def convertTime(date, hour):

    # Combine date and time
    fecha_hora = f"{date} {hour}"

    # Convert to UTC datetime
    fecha_utc = datetime.strptime(fecha_hora, '%d/%m/%Y %H:%M:%S').replace(tzinfo=timezone.utc)

    # Convert to Unix timestamp
    timestamp = int(fecha_utc.timestamp())

    #print(timestamp)
    return timestamp



VARIABLE_PATH = '/media/cportilla/HDD/mnt/share-1/Faraday/main_radar/rawdata/d2026230/'
VARIABLE_FECHA = '18/08/2026'
#HOURS IN LT
VARIABLE_HORA = '20:12:05'
VARIABLE_NUMERO_DE_BLOQUES = 214

utc_defined = convertTime(VARIABLE_FECHA, VARIABLE_HORA)
#add 5 hours for local time
lt_defined = utc_defined+18000

#print('lt_defined',lt_defined)

dirr = VARIABLE_PATH

nprofiles= 128 #200
nsamp=800 #980
nreceivers=2
osamp=4
navg=5 #nb block averages
filepath=os.listdir(dirr) #Get the list of all files in directory
#print('filepath', filepath)


filepath=sorted(filepath) #Sort the files in ascending numerical order

#for file in filepath:
#    print(file)

#print('filepath[0]', filepath[0])

# one file reading
filepath = [filepath[135]]

blockcount=0

fileread=True
#dirr_ = 'D2021301'

for file1 in filepath:
 print(file1)
 #print(True)

 #filecount=filecount+1
 
 
 if fileread==True and file1[-1]=='r': #and file1[:8]==dirr_:
    #print("HOLAAAA")
    #print("file1")
    #print(file1)
    inputfile = open(dirr+file1,"rb")
    #print('inputfile',inputfile)
    fsize=os.stat(dirr+file1).st_size

    #from the manual nblocks per file. Crucial for the moment
    nblocks=VARIABLE_NUMERO_DE_BLOQUES

    #print('nblocks', nblocks)
    for k in range(nblocks):#nblocks): #only read one block, acording time step
        #iavg=iavg+1
        if k==0:
            blockcount=blockcount+1
            print('blockcount',blockcount)
            #hdr=hsize# 244 #492 #First header???
            nSize = np.fromfile(inputfile,np.int32,1,"") # int32 4 bytes
            #print(nSize)
            version = np.fromfile(inputfile,np.int16,1,"") # int16 2 bytes version
            dataBlock = np.fromfile(inputfile,np.int32,1,"")
            utc = np.fromfile(inputfile,np.int32,1,"")
            

            
            #print('utc', utc[0])

            #print("UTC:", utc_time)
            #print("Perú:", peru_time)
            
            #CONDICIONAL PARA LECTURA DE DATOS A PARTIR DE, PODEMOS USAR "pass"
            
            #print('utc',utc)
            miliSecond = np.fromfile(inputfile,np.int16,1,"")
            timeZone = np.fromfile(inputfile,np.int16,1,"")
            dstFlag = np.fromfile(inputfile,np.int16,1,"")
            errorCount = np.fromfile(inputfile,np.int32,1,"")

            '''tempheader=np.fromfile(inputfile,np.int32,int(hdr/4)-6,"") #Skip header
            print("tempheader: ", tempheader)'''
            #print("utc: ",datetime.datetime.utcfromtimestamp(utc))

            #first skip of long header
            size1LongHeader = np.fromfile(inputfile,np.int32,1,"")

            nSamples = np.fromfile(inputfile,np.int32,1,"")[0]
            #print('nSamples',nSamples)
            nProfiles = np.fromfile(inputfile,np.int32,1,"")[0]
            #print('nProfiles',nProfiles)
            nChannels = np.fromfile(inputfile,np.int32,1,"")[0]
            #print('nChannels',nChannels)

            #print("size1LongHeader", size1LongHeader[0])
            tmpSkip1 = np.fromfile(inputfile,np.int32,int(size1LongHeader[0]/4)-3-1,"") #4 for 3 parameters

            #second skip of long header
            size2LongHeader = np.fromfile(inputfile,np.int32,1,"")
            #print("size2LongHeader", size2LongHeader[0])
            tmpSkip2 = np.fromfile(inputfile,np.int32,int(size2LongHeader[0]/4)-1,"")

            #n1 = np.fromfile(inputfile,np.int32,1,"")
            

            #third skip of long header
            size3LongHeader = np.fromfile(inputfile,np.int32,1,"")
            #print("size3LongHeader", size3LongHeader[0])
            n2 = np.fromfile(inputfile,np.int32,1,"")
            sizeBlock = np.fromfile(inputfile,np.int32,1,"")
            #print(n2)
            #print('nDataBlock', sizeBlock )

            tmpSkip3 = np.fromfile(inputfile,np.int32,int(size3LongHeader[0]/4)-2-1,"")

            if utc.size > 0:
                #print('utc', utc[0])
                utc_time = datetime.fromtimestamp(utc[0], timezone.utc)
                peru_time = utc_time.astimezone(ZoneInfo("America/Lima"))
                print("UTC:", utc_time)
                print("Perú:", peru_time)
        
        
        else:
            blockcount=blockcount+1
            print('blockcount',blockcount)
            #print("hola else hdr")
            #hdr=24  #Short header
            nSize = np.fromfile(inputfile,np.int32,1,"")
            version = np.fromfile(inputfile,np.int16,1,"")
            dataBlock = np.fromfile(inputfile,np.int32,1,"")
            utc = np.fromfile(inputfile,np.int32,1,"")
            miliSecond = np.fromfile(inputfile,np.int16,1,"")
            timeZone = np.fromfile(inputfile,np.int16,1,"")
            dstFlag = np.fromfile(inputfile,np.int16,1,"")
            errorCount = np.fromfile(inputfile,np.int32,1,"")

            #print("utc: ",datetime.datetime.utcfromtimestamp(utc[0]))

            #print(utc.shape)
            #print(utc)
            if utc.size > 0:
                #print('utc', utc[0])
                utc_time = datetime.fromtimestamp(utc[0], timezone.utc)
                peru_time = utc_time.astimezone(ZoneInfo("America/Lima"))
                print("UTC:", utc_time)
                print("Perú:", peru_time)

        blockdata=np.fromfile(inputfile,np.int16, 2*nSamples*nProfiles*nChannels,"") # *2 components I/Q and int16 for complete entire block

        #if utc is not None:
        if utc.size > 0:
            if utc[0]-lt_defined>=0:
                print("Pass")
                #print("HOLAAAAA")
            
                #blockdata=np.fromfile(inputfile,np.int16,2*nsamp*nprofiles*nreceivers,"")
                
                #print(blockdata.shape)
                #blockdata = np.fromfile(inputfile,np.int16,int(sizeBlock[0]/2),"")
                #print('blockdata.shape', blockdata.shape)

                r=blockdata[0::2]#real
                #print('r.shape',r.shape)
                #print(r)
                #print('r.shape',r.shape)
                i=blockdata[1::2]#imag
                #print('i.shape',i.shape)
                complex_samp=r+1j*i #complex
                channelList = np.arange(0,nChannels,1)
                #print('channelList',channelList)

                complex_samp1=complex_samp[0::nChannels] #nreceivers] #Channel 0
                complex_samp2=complex_samp[1::nChannels] #nreceivers] #Channel 1
                #complex_samp3=complex_samp[2::nChannels]
                #complex_samp4=complex_samp[3::nChannels]

                #print(complex_samp1.shape)
                #print(complex_samp2.shape)

                #tempsamp1=np.reshape(complex_samp1,(nprofiles,nsamp))
                #tempsamp2=np.reshape(complex_samp2,(nprofiles,nsamp))

                #ch0
                tempsamp1=np.reshape(complex_samp1,(nProfiles,nSamples))
                #ch1
                tempsamp2=np.reshape(complex_samp2,(nProfiles,nSamples))
                #ch2
                #tempsamp3=np.reshape(complex_samp3,(nProfiles,nSamples))
                #ch3
                #tempsamp4=np.reshape(complex_samp4,(nProfiles,nSamples))

                # Combinar los canales
                #temp = np.stack([tempsamp1, tempsamp2, tempsamp3, tempsamp4], axis=0)
                temp = np.stack([tempsamp1, tempsamp2], axis=0)
                #print('temp.shape',temp.shape)

                
                for j in range(nProfiles):
                    #j=j+1
                    print("Profile: ",j+1)
                    #print("HIIII")
                    #print('temp.shape', temp.shape)
                    
                    t = [i for i in range(nSamples)]
                    plt.plot(t,np.real(temp[0,j,:]))
                    plt.plot(t,np.imag(temp[0,j,:]))
                    plt.show()
                    plt.close()


    #x=x+1
    inputfile.close()

