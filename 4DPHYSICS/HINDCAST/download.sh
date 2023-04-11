#!/usr/bin/bash
#Script for downloading wave operational forecast
echo "---------------------------------------------------------------------------------------------"
printf '\nSTARTING DOWNLOAD OF MERCATOR FORECAST\n'
echo "---------------------------------------------------------------------------------------------"
cd /home/lucas/storage/FORECAST/MERCATOR/4DPHYSICS/HINDCAST
yrs="2021 2022"
months=$(seq -w 01 12)
for yr in ${yrs}; do 
    for m in ${months}; do
        if [ -f "${yr}-${m}.nc" ]; then
            echo "${yr}-${m}.nc already exists!"
        else
            var=zos
            product=cmems_mod_glo_phy_anfc_0.083deg_P1D-m
            name=${yr}-${m}_zos
            cat motuconfig.ini | sed "s/%TIME1%/${yr}-${m}-01/g" | sed "s/%TIME2%/${yr}-${m}-31/g"  > hindcast.ini
            sed -i "s/%PRODUCT%/$product/g" hindcast.ini
            sed -i "s/%VAR%/$var/g" hindcast.ini
            sed -i "s/%NAME%/$name/g" hindcast.ini
            cat hindcast.ini
            motuclient --config-file hindcast.ini
            
            var=uo,vo
            product=cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m
            name=${yr}-${m}_cur
            cat motuconfig.ini | sed "s/%TIME1%/${yr}-${m}-01/g" | sed "s/%TIME2%/${yr}-${m}-31/g"  > hindcast.ini
            sed -i "s/%PRODUCT%/$product/g" hindcast.ini
            sed -i "s/%VAR%/$var/g" hindcast.ini
            sed -i "s/%NAME%/$name/g" hindcast.ini
            cat hindcast.ini
            motuclient --config-file hindcast.ini

            var=so
            product=cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m
            name=${yr}-${m}_so
            cat motuconfig.ini | sed "s/%TIME1%/${yr}-${m}-01/g" | sed "s/%TIME2%/${yr}-${m}-31/g"  > hindcast.ini
            sed -i "s/%PRODUCT%/$product/g" hindcast.ini
            sed -i "s/%VAR%/$var/g" hindcast.ini
            sed -i "s/%NAME%/$name/g" hindcast.ini
            cat hindcast.ini
            motuclient --config-file hindcast.ini

            var=thetao
            product=cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m
            name=${yr}-${m}_thetao 
            cat motuconfig.ini | sed "s/%TIME1%/${yr}-${m}-01/g" | sed "s/%TIME2%/${yr}-${m}-31/g"  > hindcast.ini
            sed -i "s/%PRODUCT%/$product/g" hindcast.ini
            sed -i "s/%VAR%/$var/g" hindcast.ini
            sed -i "s/%NAME%/$name/g" hindcast.ini
            cat hindcast.ini
            motuclient --config-file hindcast.ini

            python3 merge.py ${yr} ${m}
            rm ${yr}-${m}_*
        fi

    done

done
