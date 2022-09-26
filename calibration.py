#!/usr/bin/env python

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

bsize = 20

#### Array search function ####
get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]

#### Extraction function ####
def extract(data):
    calib_data = []
    volt_calib_data = []
    if (data[0] == 0xAAAA and data[data.size-1] == 0xD6D6 and data[data.size-2] == data.size):  #
        print("Data Packet OK")

        daq_id = data[3] # Extracting metadata
        evt_cnt = (data[5] << 16) + data[4]
        vcal16 = data[6]
        vcal = vcal16 >> 2
        volt_vcal = vcal16/26214
        channel_id = data[7]
        payload_size = (data[23] << 16) + data[22]

        print("DAQ ID: ",daq_id)
        print("Channel No.: ",channel_id)
        print("Event Number: ",evt_cnt)
        print("Data payload size: ",payload_size)
        print("Calibration voltage: ",volt_vcal)

        volt_data = ((data*2)/16383) # Actual voltage value from the raw ADC reading

        path = os.path.join(os.getcwd(), ".temp")
        if not os.path.exists(path):
            os.makedirs(path)

        #Exporting extracted data to a CSV file named 'calibration_vcal=*.csv', * is VCAL value
        try:
            with open(os.path.join(path, 'ADCdata_channelNo-'+str(channel_id)+'_evtNo-'+str(evt_cnt)+'_vcal-'+str(volt_vcal)+'.csv'),'w') as fout:
                fout.write("Channel no.,Cell no.,ADC Reading,ADC Offset,Voltage Reading,Voltage Offset,VCAL\n")
                for j in range (24,payload_size+24):
                    calib_data.append([data[j]-vcal])
                    volt_calib_data.append([volt_data[j]-volt_vcal])
                    fout.write(str(channel_id))
                    fout.write(",")
                    fout.write(str(j-24))
                    fout.write(",")
                    fout.write(str(data[j]))
                    fout.write(",")
                    fout.write(str(vcal-data[j]))
                    fout.write(",")
                    fout.write(str(volt_data[j]))
                    fout.write(",")
                    fout.write(str(volt_vcal-volt_data[j]))
                    fout.write(",")
                    fout.write(str(volt_vcal))
                    fout.write("\n")
                print("Temporary file written successfully")
        except IOError:
            print("Error creating the file")

    else:
        print("Data packet error")
        exit()

#### Splitting function ####
def split(data):
    end_markers = get_indexes(0xD6D6,data)
    count = len(end_markers)
    output = np.array_split(data,count)
    return output, count

#### Binary file opening function ####
def fileopen(filename):
    print("####################")
    print("Input binary file: ",filename)

    try:
        with open(filename,'rb') as f:
            data = np.fromfile(f, dtype = '<H') # '<' represents little endian, 'H' represents unsigned short (16 bits)
            print("File opened successfully")
    except IOError:
        print("Error opening the file")
        exit()
    return data

#### CSV file opening function ####
def csvfileopen(filename):
    filename = os.path.join(".temp",filename)
#    print("####################")
#    print("Input file: ",filename)

    col0,col3,col4,col5,col6 = np.loadtxt(filename,delimiter=',',usecols=(0,3,4,5,6),skiprows=1,unpack=True) #load the contents in a temporary variable
    return col0,col3,col4,col5,col6


#### Analysis and plotting function ####
def analyse(matrix,vmatrix,dsize,channel_no,filename):
    av = np.mean(matrix,axis=0) # calculating mean
    sd = np.std(matrix,axis=0)  # calculating standard deviation
    vav = np.mean(vmatrix,axis=0)
    vav_mod = np.delete(vav,[0,1,2])
    vsd = np.std(vmatrix,axis=0)
    fname = 'calibration_'+filename+'.csv'

    if not os.path.exists(fname):
        open(fname,'w')
        pass

    try:
        with open(fname,'a+') as fout:      # writing mean and s.d. values in a file named 'calibration_data.csv'
            fout.write("Chennel No.,Cell no.,Mean Offset,Offset S.D.,Mean Offset (V),Offset S.D. (V)\n")
            for i in range (dsize):
                fout.write(str(channel_no))
                fout.write(",")
                fout.write(str(i))
                fout.write(",")
                fout.write(str(av[i]))
                fout.write(",")
                fout.write(str(sd[i]))
                fout.write(",")
                fout.write(str(vav[i]))
                fout.write(",")
                fout.write(str(vsd[i]))
                fout.write("\n")
            print("####################")
    except IOError:
        print("Error creating the file")
        # plotting mean offset for each cell, and s.d. as error bar

    c = [8,16,32,64,128,256,512,1023]
    plt.figure(figsize=(8.25,11.75))
    plt.clf()
    plt.subplot(2,1,1)
    plt.plot(range(dsize),vav*1000)
    plt.title("Channel no.: "+str(channel_no)+"\n\nMean offset for each cell")
    plt.xlabel("DRS cell no.")
    plt.ylabel("Offset (mV)")

    plt.subplot(2,1,2)
    plt.plot(range(3,dsize),vav_mod*1000)
    plt.title("Mean offset for each cell (without cell no. 0,1,2)")
    plt.xlabel("DRS cell no.")
    plt.ylabel("Offset (mV)")

    plt.tight_layout()
    pp.savefig()

    # plotting histograms in 4x2 subplots
    # for 8th cell
    plt.figure(figsize=(8.25,11.75))
    plt.clf()
    for i in range(8):
        plt.subplot(4,2,i+1)
        plt.hist(1000*vmatrix[:,c[i]],histtype='step',bins=bsize)
        plt.title("Offset for "+str(c[i])+"th Cell")
        plt.xlabel("Offset voltage (mV)")
        plt.ylabel("Count")
    plt.tight_layout()

#### Linear fitting and plotting function ####
def fitter(x,y):
    c = [8,16,32,64,128,256,512,1023]
    plt.figure(figsize=(8.25,11.75))
    plt.clf()
    x0 = np.arange(0,1.5,0.01)
    for i in range(8):
        p = np.polyfit(x[:,c[i]],y[:,c[i]],1)
        plt.subplot(4,2,i+1)
        plt.plot(x[:,c[i]],y[:,c[i]],"r*")
        plt.plot(x0,p[0]*x0+p[1],'b--')
        plt.xlim(0,1.5)
        plt.ylim(0,1.5)
        plt.title("Input vs output voltage\nDRS cell no. "+str(c[i]))
        plt.xticks(np.arange(0, 1.5, step=0.1),rotation=20)
        plt.yticks(np.arange(0, 1.5, step=0.1),rotation=20)
        plt.xlabel("Input calibration voltage (V)")
        plt.ylabel("Output (V)")
        plt.grid(True)
    plt.tight_layout()
    pp.savefig()
    plt.figure(figsize=(8.25,11.75))
    plt.clf()
    for i in range(8):
        plt.subplot(4,2,i+1)
        plt.plot(x[:,c[i]],x[:,c[i]]-y[:,c[i]],"r*")
        plt.xlim(0,1.5)
        plt.ylim(0,1.5)
        plt.title("Input voltage vs offset\nDRS cell no. "+str(c[i]))
        plt.xticks(np.arange(0, 1.5, step=0.1),rotation=20)
        plt.yticks(np.arange(0, 1.5, step=0.1),rotation=20)
        plt.xlabel("Input calibration voltage (V)")
        plt.ylabel("Output (V)")
        plt.grid(True)
    plt.tight_layout()
    pp.savefig()


#### Main function ####
n = len(sys.argv)
if n != 2:
    print("Error in arguement number. Precisely 1 input file is supported.")
    exit()
path = os.path.join(os.getcwd(), ".temp")
if os.path.isdir(path):
    for fdel in os.listdir(path):
        f = os.path.join(path,fdel)
        if os.path.isfile(f):
            os.remove(f)

fin = sys.argv[1] # Take file name as input argument
bindata = fileopen(fin)
packet,count = split(bindata)
for i in range(count):
    extract(packet[i])

fout = fin.split(".")



counter = 0
ch=[]

for fin in os.listdir(path):
    if fin.endswith('.csv'): # check if file is csv
        c,off,v,voff,vcal = csvfileopen(fin)
        try:
            offarray = np.concatenate((offarray,off),axis=None) # if variable 'array' exists, append the temporary variable to it
            voffarray = np.concatenate((voffarray,voff),axis=None)
            varray = np.concatenate((varray,v),axis=None)
            vcalarray = np.concatenate((vcalarray,vcal),axis=None)
        except NameError:
            offarray = off # if 'array' doesn't exist (NameError), create it
            voffarray = voff
            varray = v
            vcalarray = vcal
        counter += 1
    ch.append(int(c[0]))
    datasize = off.size # get the data size (assuming same data size for all files)

ch = np.sort(np.unique(ch))
no_ch = len(ch)

if (counter == 1):
    sz = 1
elif (counter == 0):
    print("Error: Temporary file(s) not found")
    exit()
else:
    sz = int(counter/no_ch)

offset = np.reshape(offarray, (sz, datasize, no_ch)) # creating the voltage matrix, which is a MxN matrix, M= no. of data files, N= data size
voffset = np.reshape(voffarray, (sz, datasize, no_ch))
voltage = np.reshape(varray, (sz, datasize, no_ch))
vcalib = np.reshape(vcalarray, (sz, datasize, no_ch))

pp = PdfPages(fout[0]+'.pdf')

if os.path.isfile('calibration_'+fout[0]+'.csv'):
    os.remove('calibration_'+fout[0]+'.csv')

for i in range(no_ch):
    text = 'Channel no.: '+str(ch[i])
    pp.attach_note(text, positionRect=[0, 0, 0, 0])
    analyse(offset[:,:,i],voffset[:,:,i],datasize,ch[i],fout[0])
    pp.savefig()
    fitter(vcalib[:,:,i],voltage[:,:,i])
    pp.savefig()

pp.close()
print("Output file written successfully")

for fdel in os.listdir(path):
    # construct full file path
    f = os.path.join(path,fdel)
    if os.path.isfile(f):
#        print('Deleting file:', f)
        os.remove(f)
os.rmdir(".temp")
print("done!")
