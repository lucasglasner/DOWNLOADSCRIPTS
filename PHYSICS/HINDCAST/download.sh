#!/usr/bin/bash
#Script for downloading wave operational forecast
echo "---------------------------------------------------------------------------------------------"
printf '\nSTARTING DOWNLOAD OF MERCATOR FORECAST\n'
echo "---------------------------------------------------------------------------------------------"
cd /home/lucas/storage/FORECAST/MERCATOR/PHYSICS/HINDCAST
yr=2022
for i in $(seq -w 10 10); do
idate="$yr-$i-01"
fdate="$yr-$i-11"
echo "Creating config file for today..."
echo "Configs:{ "
printf '\n'
cat motuconfig.ini | sed "s/%NAME%/${idate}/g" | sed "s/%TIME1%/${idate}\ 00:00/g" | sed "s/%TIME2%/${fdate}\ 23:59/g" > tmp.ini
cat tmp.ini
printf '\n\n}\n'
if [ -f "${idate}.nc" ]; then
    echo "Data for today already exists!"
    echo "Checking file integrity..."
else
    echo "Data for today doesnt exists"
    echo "Downloading forecast..."
    motuclient --config-file tmp.ini
fi
rm tmp.ini
done
