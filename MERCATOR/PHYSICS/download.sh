#!/usr/bin/bash
#Script for downloading wave operational forecast
echo "---------------------------------------------------------------------------------------------"
printf '\nSTARTING DOWNLOAD OF MERCATOR FORECAST\n'
echo "---------------------------------------------------------------------------------------------"
cd /home/lucas/storage/FORECAST/MERCATOR/PHYSICS/
idate=$(date +%F)
ydate=$(date +%F -d '-1 day')
fdate=$(date +%F -d '+9 day')
echo "Creating config file for today..."
echo "Configs:{ "
printf '\n'
cat motuconfig.ini | sed "s/%NAME%/${idate}/g" | sed "s/%TIME1%/${idate}\ 00:00/g" | sed "s/%TIME2%/${fdate}\ 23:59/g" > forecast.ini
cat motuconfig.ini | sed "s/%NAME%/HINDCAST\/${ydate}/g" | sed "s/%TIME1%/${ydate}\ 00:00/g" | sed "s/%TIME2%/${ydate}\ 23:59/g" > hindcast.ini
cat forecast.ini
printf '\n\n}\n'
if [ -f "${idate}.nc" ]; then
    echo "Forecast for today already exists!"
    echo "Checking forecast file integrity..."
    #statement=$(ncdump -h ${idate}.nc | head | grep -oP '(?<=time =).*?(?=;)')
    statement=$(ncdump -h ${idate}.nc | head | grep -oP '(?<=time =).*?(?=;)')
    if [ $statement = 240 ]; then
        echo 'All good'
    else
        echo 'Forecast file isnt complete, downloading again...'
        motuclient --config-file forecast.ini
        echo 'Changing FillValue and compressing with nco'
        ncatted -a _FillValue,,m,f,-32767 ${idate}.nc
        ncpdq -L 5 -7 ${idate}.nc tmp.nc
        rm ${idate}.nc
        mv tmp.nc ${idate}.nc
    fi
else
    echo "Forecast data for today doesnt exists"
    echo "Downloading forecast..."
    motuclient --config-file forecast.ini
    echo 'Changing FillValue and compressing with nco'
    ncatted -a _FillValue,,m,f,-32767 ${idate}.nc
    ncpdq -L 5 -7 ${idate}.nc tmp.nc
    rm ${idate}.nc
    mv tmp.nc ${idate}.nc
fi
printf '\n'
if [ -f "HINDCAST/${ydate}.nc" ]; then
	echo "Hindcast for today already exists!"
else
	echo "Hindcast data for today doesnt exists!"
	echo "Downloading hindcast..."
	motuclient --config-file hindcast.ini
   echo 'Changing FillValue and compressing with nco'
   ncatted -a _FillValue,,m,f,-32767 HINDCAST/${ydate}.nc
   ncpdq -L 5 -7 HINDCAST/${ydate}.nc HINDCAST/tmp.nc
   rm HINDCAST/${ydate}.nc
   mv HINDCAST/tmp.nc HINDCAST/${ydate}.nc
fi

rm hindcast.ini
rm forecast.ini
printf "Done\n"
printf "\n\n"
echo "---------------------------------------------------------------------------------------------"
echo "Checking data for the last 3 days..."
for i in {1..20}; do
    printf '\n'
    echo "---------------------------------------------------------------------------------------------"
    printf "\nChecking forecast for $i days ago...\n"
    idate=$(date +%F -d "-$i day")
    ydate=$(date +%F -d "-$(( $i+1 )) day")
    n=$(( 9-$i ))
    fdate=$(date +%F -d "+$n day")
    echo "Creating config file for $i days ago..."
    echo "Configs:{ "
    printf '\n'
    cat motuconfig.ini | sed "s/%NAME%/${idate}/g" | sed "s/%TIME1%/${idate}\ 00:00/g" | sed "s/%TIME2%/${fdate}\ 23:59/g" > forecast.ini
    cat motuconfig.ini | sed "s/%NAME%/HINDCAST\/${ydate}/g" | sed "s/%TIME1%/${ydate}\ 00:00/g" | sed "s/%TIME2%/${ydate}\ 23:59/g" > hindcast.ini
    cat forecast.ini
    printf '\n\n}\n'
    if [ -f "${idate}.nc" ]; then
        echo "Forecast data for $i days ago already exists!"
        echo "Checking file integrity..."
        statement=$(ncdump -h ${idate}.nc | head | grep -oP '(?<=time =).*?(?=;)')
        if [ $statement = 240 ]; then
            echo 'All good'
        else
            echo 'Forecast file isnt complete, downloading again...'
            motuclient --config-file forecast.ini
           echo 'Changing FillValue and compressing with nco'
           ncatted -a _FillValue,,m,f,-32767 ${idate}.nc
           ncpdq -L 5 -7 ${idate}.nc tmp.nc
           rm ${idate}.nc
           mv tmp.nc ${idate}.nc
        fi
    else
        echo "Forecast data for $i days ago doesnt exists"
        echo "Downloading forecast..."
        motuclient --config-file forecast.ini 
       echo 'Changing FillValue to -9999 and compressing with nco'
       ncatted -a _FillValue,,m,f,-9999 ${idate}.nc
       ncpdq -L 5 -7 ${idate}.nc tmp.nc
       rm ${idate}.nc
       mv tmp.nc ${idate}.nc
    fi
    if [ -f "HINDCAST/${ydate}.nc" ]; then
	    echo "Hindcast data for $(( $i+1 )) days ago already exists!"
    else
	    echo "Hindcast data for $(( $i+1 )) days ago doesnt exists"
	    echo "Downloading hindcast..."
	    motuclient --config-file hindcast.ini
       echo 'Changing FillValue and compressing with nco'
       ncatted -a _FillValue,,m,f,-32767 HINDCAST/${ydate}.nc
       ncpdq -L 5 -7 HINDCAST/${ydate}.nc HINDCAST/tmp.nc
       rm HINDCAST/${ydate}.nc
       mv HINDCAST/tmp.nc HINDCAST/${ydate}.nc
    fi
    rm forecast.ini
    rm hindcast.ini
    printf "Done\n"
done
