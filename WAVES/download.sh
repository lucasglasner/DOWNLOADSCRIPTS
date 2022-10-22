#!/usr/bin/bash
#Script for downloading wave operational forecast
echo "---------------------------------------------------------------------------------------------"
printf '\nSTARTING DOWNLOAD OF MERCATOR FORECAST\n'
echo "---------------------------------------------------------------------------------------------"
cd /home/lucas/storage/FORECAST/MERCATOR/WAVES/
idate=$(date +%F)
fdate=$(date +%F -d '+9 day')
echo "Creating config file for today..."
echo "Configs:{ "
printf '\n'
cat motuconfig.ini | sed "s/%NAME%/${idate}/g" | sed "s/%TIME1%/${idate}\ 00:00/g" | sed "s/%TIME2%/${fdate}\ 23:59/g" > tmp.ini
cat tmp.ini
printf '\n\n}\n'
if [ -f "${idate}.nc" ]; then
    echo "Data for today already exists!"
    echo "Checking file integrity..."
    statement=$(ncdump -h ${idate}.nc | head | grep -oP '(?<=time =).*?(?=;)')
    if [ $statement = 80 ]; then
        echo 'All good'
    else
        echo 'File isnt complete, downloading again...'
        motuclient --config-file tmp.ini
    fi
else
    echo "Data for today doesnt exists"
    echo "Downloading forecast..."
    motuclient --config-file tmp.ini
fi
rm tmp.ini
printf "Done\n"
printf "\n\n"
echo "---------------------------------------------------------------------------------------------"
echo "Checking data for the last 10 days..."
for i in {1..10}; do
    printf '\n'
    echo "-------------------------------------------------------------------------------------------"
    printf "\nChecking forecast for $i days ago...\n"
    idate=$(date +%F -d "-$i day")
    n=$(( 9-$i ))
    fdate=$(date +%F -d "+$n day")
    echo "Creating config file for $i days ago..."
    echo "Configs:{ "
    printf '\n'
    cat motuconfig.ini | sed "s/%NAME%/${idate}/g" | sed "s/%TIME1%/${idate}\ 00:00/g" | sed "s/%TIME2%/${fdate}\ 23:59/g" > tmp.ini
    cat tmp.ini
    printf '\n\n}\n'
    if [ -f "${idate}.nc" ]; then
        echo "Data for $i days ago already exists!"
        echo "Checking file integrity..."
        statement=$(ncdump -h ${idate}.nc | head | grep -oP '(?<=time =).*?(?=;)')
        if [ $statement = 80 ]; then
            echo 'All good'
        else
            echo 'File isnt complete, downloading again...'
            motuclient --config-file tmp.ini
        fi
    else
        echo "Data for $i days ago doesnt exists"
        echo "Downloading forecast..."
        motuclient --config-file tmp.ini
    fi
    rm tmp.ini
    printf "Done\n"
done
