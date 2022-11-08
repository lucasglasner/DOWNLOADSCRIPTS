#!/usr/bin/bash
#Script for downloading wave operational forecast
echo "---------------------------------------------------------------------------------------------"
printf '\nSTARTING DOWNLOAD OF MERCATOR FORECAST\n'
echo "---------------------------------------------------------------------------------------------"
cd /home/lucas/storage/FORECAST/MERCATOR/FULLPHYSICS/HINDCAST
yrs="2020 2021 2022"
months=$(seq -w 01 12)
for yr in ${yrs}; do 
    for m in ${months}; do
        if [ -f "${yr}-${m}.nc" ]; then
            echo "exit"
        else
            cat motuconfig.ini | sed "s/%TIME1%/${yr}-${m}-01/g" | sed "s/%TIME2%/${yr}-${m}-31/g" | sed "s/%NAME%/${yr}-${m}/g" > hindcast.ini
            cat hindcast.ini
            motuclient --config-file hindcast.ini
        fi
    done
done
