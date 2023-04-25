#!/usr/bin/bash
#Script for downloading 4D mercator operational forecast
echo "---------------------------------------------------------------------------------------------"
printf '\nSTARTING DOWNLOAD OF MERCATOR FORECAST\n'
echo "---------------------------------------------------------------------------------------------"
cd /home/lucas/storage/FORECAST/MERCATOR/4DPHYSICS/
idate=$(date +%F)
ydate=$(date +%F -d '-1 day')
fdate=$(date +%F -d '+10 day')
echo "Creating config file for today..."
echo "Configs:{ "
printf '\n'
cat motuconfig.ini | sed "s/%NAME%/${idate}/g" | sed "s/%TIME1%/${idate}/g" | sed "s/%TIME2%/${fdate}/g" > forecast.ini
cat motuconfig.ini | sed "s/%NAME%/HINDCAST\/${ydate}/g" | sed "s/%TIME1%/${ydate}/g" | sed "s/%TIME2%/${ydate}/g" > hindcast.ini
cat forecast.ini
printf '\n\n}\n'
if [ -f "${idate}.nc" ]; then
    echo "Forecast for today already exists!"
    echo "Checking forecast file integrity..."
    statement=$(ncdump -h ${idate}.nc | head | grep -oP '(?<=time =).*?(?=;)')
    if [ $statement = 10 ]; then
        echo 'All good'
    else
        echo 'Forecast file isnt complete, downloading again...'
        motuclient --config-file forecast.ini
    fi
else
    echo "Forecast data for today doesnt exists"
    echo "Downloading forecast..."
    motuclient --config-file forecast.ini
fi
printf '\n'
if [ -f "HINDCAST/${ydate}.nc" ]; then
	echo "Hindcast for today already exists!"
else
	echo "Hindcast data for today doesnt exists!"
	echo "Downloading hindcast..."
	motuclient --config-file hindcast.ini
fi

rm hindcast.ini
rm forecast.ini
printf "Done\n"
printf "\n\n"
echo "---------------------------------------------------------------------------------------------"
echo "Checking data for the last 15 days..."
for i in {1..15}; do
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
    cat motuconfig.ini | sed "s/%NAME%/${idate}/g" | sed "s/%TIME1%/${idate}/g" | sed "s/%TIME2%/${fdate}/g" > forecast.ini
    cat motuconfig.ini | sed "s/%NAME%/HINDCAST\/${ydate}/g" | sed "s/%TIME1%/${ydate}/g" | sed "s/%TIME2%/${ydate}/g" > hindcast.ini
    cat forecast.ini
    printf '\n\n}\n'
    if [ -f "${idate}.nc" ]; then
        echo "Forecast data for $i days ago already exists!"
        echo "Checking file integrity..."
        statement=$(ncdump -h ${idate}.nc | head | grep -oP '(?<=time =).*?(?=;)')
        if [ $statement = 10 ]; then
            echo 'All good'
        else
            echo 'Forecast file isnt complete, downloading again...'
            motuclient --config-file forecast.ini
        fi
    else
        echo "Forecast data for $i days ago doesnt exists"
        echo "Downloading forecast..."
        motuclient --config-file forecast.ini
    fi
    if [ -f "HINDCAST/${ydate}.nc" ]; then
	    echo "Hindcast data for $(( $i+1 )) days ago already exists!"
    else
	    echo "Hindcast data for $(( $i+1 )) days ago doesnt exists"
	    echo "Downloading hindcast..."
	    motuclient --config-file hindcast.ini
    fi
    rm forecast.ini
    rm hindcast.ini
    printf "Done\n"
done
