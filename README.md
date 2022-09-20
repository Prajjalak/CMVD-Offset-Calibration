# CMVD-Offset-Calibration
Code for CMVD DDB board's DRS chip cell wise offset calibration

####################
# DRS Offset Calibration Code
Author: Prajjalak C
Language: Python 3

# To run all:

            ./runall.sh

# To run individual codes:

    1. extract.py: Extracts binary data from *.bin files and puts into *.csv files
        Arguements:
            -a, --all: considers all *.bin files in the current working directory
            -f, --file: considers only the file(s) followed by
        Usage:
            python3 extract.py -a
                    OR
            python3 extract.py -f file1.bin file2.bin file3.bin

    2. analyse.py: Analyses individual *.csv files to calculate mean and standard deviation of offset values, optionally (user input from terminal: y/N) plots mean offset vs cell no. with s.d. as error bars, and writes the final mean and s.d. values in 'calibration_data.csv' file. If any 'calibration_data.csv' exists beforehand, it creates backup by renaming 'calibration_data.csv.bak'
        Arguements:
            -a, --all: considers all *.csv files in the current working directory (except 'calibration_data.csv')
            -f, --file: considers only the file(s) followed by (not checked for 'calibration_data.csv', user must be careful)
        Usage:
            python3 analyse.py -a
                    OR
            python3 analyse.py -f file1.csv file2.csv file3.csv

    3. plot.py: Plots calibration voltage vs output voltage for a specific DRS cell no. (user input from terminal).
        Arguements:
            -a, --all: considers all *.csv files in the current working directory (except 'calibration_data.csv')
            -f, --file: considers only the file(s) followed by (not checked for 'calibration_data.csv', user must be careful)
        Usage:
            python3 plot.py -a
                    OR
            python3 plot.py -f file1.csv file2.csv file3.csv

# Final output: 

              1. 'calibration_data.csv' which contains mean and standard deviation data of offset values for each individual DRS cells.
              2. graphs
