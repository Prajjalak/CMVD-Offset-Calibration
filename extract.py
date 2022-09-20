#!/usr/bin/env python

import numpy as np
import sys
import os
import matplotlib.pyplot as plt

#### Array search function ####
get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]

#### Extraction function ####
def extract(data):
    calib_data = []
    volt_calib_data = []
    if (data[0] == 0xAAAA and data[data.size-1] == 0xD6D6 and data[data.size-2] == data.size):
        print("Data Packet OK")

        daq_id = data[3] # Extracting metadata
        evt_cnt = (data[5] << 16) + data[4]
        vcal16 = data[6]
        vcal = vcal16 >> 2
        volt_vcal = vcal16/26214
        payload_size = (data[23] << 16) + data[22]

        print("DAQ ID: ",daq_id)
        print("Event Number: ",evt_cnt)
        print("Data payload size: ",payload_size)
        print("Calibration voltage: ",volt_vcal)

        volt_data = ((data*2)/16383) # Actual voltage value from the raw ADC reading

        #Exporting extracted data to a CSV file named 'calibration_vcal=*.csv', * is VCAL value
        try:
            with open('ADCdata_evtNo='+str(evt_cnt)+'_vcal='+str(volt_vcal)+'.csv','w') as fout:
                fout.write("Cell no.,ADC Reading,ADC Offset,Voltage Reading, Voltage Offset, VCAL\n")
                for j in range (24,payload_size+24):
                    calib_data.append([data[j]-vcal])
                    volt_calib_data.append([volt_data[j]-volt_vcal])
                    fout.write(str(j-24))
                    fout.write(",")
                    fout.write(str(data[j]))
                    fout.write(",")
                    fout.write(str(data[j]-vcal))
                    fout.write(",")
                    fout.write(str(volt_data[j]))
                    fout.write(",")
                    fout.write(str(volt_data[j]-volt_vcal))
                    fout.write(",")
                    fout.write(str(volt_vcal))
                    fout.write("\n")
                print("Output file written successfully")
        except IOError:
            print("Error creating the file")

    else:
        print("Data packet error")
        exit()

#### Splitting function ####
def split(data):
    end_markers = get_indexes(0xD6D6,bindata)
    count = len(end_markers)
    output = np.array_split(data,count)
    return output, count

#### File opening function ####
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

#### Main function ####
n = len(sys.argv)
path = os.getcwd() # get the current working directory

if n < 2:
    print("Error: no arguements given")
    exit()

if sys.argv[1] == '-a' or sys.argv[1] == '--all':
    print("Opening all files...")
    for fin in os.listdir(path):
        if fin.endswith('.bin'): # check if file is binary
            bindata = fileopen(fin)
            packet,count = split(bindata)
            for i in range(count):
                extract(packet[i])


elif sys.argv[1] == '-f' or sys.argv[1] == '--file':
    print("Opening selected files...")
    for i in range(2, n):
        fin = sys.argv[i] # Take file name as input argument
        bindata = fileopen(fin)
        packet,count = split(bindata)
        for i in range(count):
            extract(packet[i])

else:
    print("Wrong arguement")
    exit()


