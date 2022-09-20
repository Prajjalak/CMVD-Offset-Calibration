#!/bin/bash

echo "**** DRS CALIBRATION ****"
echo "*************************"
rm *.csv
echo Extracting data...
echo "********************"
python3 extract.py -a
echo
echo "********************"
echo Analysing data...
echo "********************"
python3 analyse.py -a
echo
echo "********************"
echo Plotting data...
echo "********************"
python3 plot.py -a
echo
echo "********************"
GLOBIGNORE=calibration_data.csv
while true; do
    read -r -p "Clean temporary csv files? [y/N]: " cln
    case $cln in
        [Yy]* ) rm -v *.csv; break;;
        [Nn]* ) exit;;
        * ) echo "Input not accepted";;
    esac
done
unset GLOBIGNORE
echo "********************"
echo "Done!"
echo "********************"
