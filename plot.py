#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

#### File opening function ####
def fileopen(filename):
    print("####################")
    print("Input file: ",filename)

    data_temp,vcal_temp = np.loadtxt(fin,delimiter=',',usecols=(3,5),skiprows=1,unpack=True)
    return data_temp,vcal_temp


#### Plotting function ####
def plotter(x,y):
    condition = 'y'
    while condition == 'y' or condition == 'Y':
        c = int(input("Enter DRS cell no. [0-1023]: "))
        if (c < 0) and (c > 1023):
            print("Invalid channel no.")
        else:
            plt.figure()
            plt.plot(x[:,c],y[:,c])
            plt.plot(x[:,c],y[:,c],"r*")
            plt.xlim(0,1.5)
            plt.ylim(0,1.5)
            plt.title("Input vs output voltage for DRS cell no. "+str(c))
            plt.show()
        condition = input("Continue? [y/n]:")



#### Main function ####

counter = 0
n = len(sys.argv)
path = os.getcwd() # get the current working directory

if n < 2:
    print("Error: no arguements given")
    exit()

if sys.argv[1] == '-a' or sys.argv[1] == '--all':
    print("Opening all files...")
    for fin in os.listdir(path):
        if fin.endswith('.csv') and fin != 'calibration_data.csv': # check if file is csv and not the output file
            data_temp,vcal_temp = fileopen(fin)
            try:
                data_array = np.concatenate((data_array,data_temp),axis=None) # if variable 'array' exists, append the temporary variable to it
                vcal_array = np.concatenate((vcal_array,vcal_temp),axis=None)
            except NameError:
                data_array = data_temp # if 'array' doesn't exist (NameError), create it
                vcal_array = vcal_temp
            datasize = data_temp.size # get the data size (assuming same data size for all files)
            counter += 1

    voltage = np.reshape(data_array, (counter, datasize)) # creating the voltage matrix, which is a MxN matrix, M= no. of data files, N= data size
    vcal = np.reshape(vcal_array, (counter, datasize))

    plotter(vcal,voltage)


elif sys.argv[1] == '-f' or sys.argv[1] == '--file':
    print("Opening selected files...")
    for i in range(2, n):
        fin = sys.argv[i] # Take file name as input argument
        if fin.endswith('.csv'): # check if file is binary
            data_temp,vcal_temp = fileopen(fin)
            try:
                data_array = np.concatenate((data_array,data_temp),axis=None) # if variable 'array' exists, append the temporary variable to it
                vcal_array = np.concatenate((vcal_array,vcal_temp),axis=None)
            except NameError:
                data_array = data_temp # if 'array' doesn't exist (NameError), create it
                vcal_array = vcal_temp
            datasize = data_temp.size # get the data size (assuming same data size for all files)
            counter += 1

    voltage = np.reshape(data_array, (counter, datasize)) # creating the voltage matrix, which is a MxN matrix, M= no. of data files, N= data size
    vcal = np.reshape(vcal_array, (counter, datasize))

    plotter(vcal,voltage)



else:
    print("Wrong arguement")
    exit()

