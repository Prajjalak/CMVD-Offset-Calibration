#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
        
#### File opening function ####
def fileopen(filename):
    print("####################")
    print("Input file: ",filename)

    temp = np.loadtxt(filename,delimiter=',',usecols=2,skiprows=1) #load the contents in a temporary variable
    return temp

#### Analysis function ####
def analyse(matrix,dsize):
    av = np.mean(matrix,axis=0) # calculating mean
    sd = np.std(matrix,axis=0)  # calculating standard deviation

    try:
        with open('calibration_data.csv','w') as fout:      # writing mean and s.d. values in a file named 'calibration_data.csv'
            fout.write("Cell no.,Mean Offset,Offset S.D.\n")
            for i in range (dsize):
                fout.write(str(i))
                fout.write(",")
                fout.write(str(av[i]))
                fout.write(",")
                fout.write(str(sd[i]))
                fout.write("\n")
            print("####################")
            print("Output file written successfully")
    except IOError:
        print("Error creating the file")

    show = input("Show graphs? [y/N]: ")
    if show == 'y' or show == 'Y':
        # plotting mean offset for each cell, and s.d. as error bar
        plt.figure(1,figsize=(8,6))
        plt.errorbar(range(dsize),av,yerr=sd)
        plt.ylim(0,16383)
        plt.xlim(0,1023)
        plt.title("Mean offset for each cell")
        plt.show()

        # plotting histograms in 2x2 subplots
        plt.figure(2,figsize=(8,6))

        # for 0th cell
        plt.subplot(2,2,1)
        plt.hist(matrix[:,0],histtype='step',bins=10)
        plt.title("Offset for 0th Cell")

        # for 256th cell
        plt.subplot(2,2,2)
        plt.hist(matrix[:,256],histtype='step',bins=10)
        plt.title("Offset for 256th Cell")

        # for 512th cell
        plt.subplot(2,2,3)
        plt.hist(matrix[:,512],histtype='step',bins=10)
        plt.title("Offset for 512th Cell")

        # for 1023th cell
        plt.subplot(2,2,4)
        plt.hist(matrix[:,1023],histtype='step',bins=10)
        plt.title("Offset for 1023th Cell")

        plt.tight_layout()
        plt.show()

        h = input("Want to get any other histogram? [y/N]: ")
        if h == 'y' or h == 'Y':
            c = int(input("Enter DRS cell no. [0-1023]: "))
            b = int(input("Enter bin size [e.g. 10]: "))
            if (c < 0) and (c > 1023):
                print("Invalid channel no.")
            else:
                plt.figure(3,figsize=(8,6))
                plt.hist(matrix[:,c],histtype='step',bins=b)
                plt.title("Offset distribution for DRS cell no. "+str(c))
                plt.show()


#### Main function ####

counter = 0
n = len(sys.argv)
path = os.getcwd() # get the current working directory

if n < 2:
    print("Error: no arguements given")
    exit()

if sys.argv[1] == '-a' or sys.argv[1] == '--all':
    if os.path.isfile("calibration_data.csv"):
        os.rename(path+"/calibration_data.csv",path+"/calibration_data.csv.bak") # if the file 'calibration_data.csv' exists beforhand, rename as backup
        print("old 'calibration_data.csv' backed up as 'calibration_data.csv.bak'")
    print("Opening all files...")
    for fin in os.listdir(path):
        if fin.endswith('.csv'): # check if file is csv
            data = fileopen(fin)
            try:
                array = np.concatenate((array,data),axis=None) # if variable 'array' exists, append the temporary variable to it
            except NameError:
                array = data # if 'array' doesn't exist (NameError), create it
            datasize = data.size # get the data size (assuming same data size for all files)
            counter += 1

    offset = np.reshape(array, (counter, datasize)) # creating the voltage matrix, which is a MxN matrix, M= no. of data files, N= data size
    analyse(offset,datasize)


elif sys.argv[1] == '-f' or sys.argv[1] == '--file':
    if os.path.isfile("calibration_data.csv"):
        os.rename(path+"/calibration_data.csv",path+"/calibration_data.csv.bak") # if the file 'calibration_data.csv' exists beforhand, rename as backup
        print("old 'calibration_data.csv' backed up as 'calibration_data.csv.bak'")
    print("Opening selected files...")
    for i in range(2, n):
        fin = sys.argv[i] # Take file name as input argument
        if fin.endswith('.csv'): # check if file is binary
            data = fileopen(fin)
            try:
                array = np.concatenate((array,data),axis=None) # if variable 'array' exists, append the temporary variable to it
            except NameError:
                array = data # if 'array' doesn't exist (NameError), create it
            datasize = data.size # get the data size (assuming same data size for all files)
            counter += 1

    offset = np.reshape(array, (counter, datasize)) # creating the voltage matrix, which is a MxN matrix, M= no. of data files, N= data size
    analyse(offset,datasize)



else:
    print("Wrong arguement")
    exit()



