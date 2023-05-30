#!/home/lucas/miniconda3/envs/forecast/bin/python3
'''
 # @ Author: lucas
 # @ Create Time: 2023-04-11 15:27:51
 # @ Modified by: lucas
 # @ Modified time: 2023-04-11 15:27:59
 # @ Description: Script for downloading ERA5 fields every day
                  Need cdo and nco installed on the machine for
                  some consistency checks.
                  Since 2m humidity only comes as dew point, 
                  this script also computes the specific humidity
                  using some cdo routines.
 '''
print('------------------------------------------------------------')
print('\nSTARTING DOWNLOAD OF ERA5 NEAR REAL TIME DATA\n           ')
print('------------------------------------------------------------')
# ---------------------------------- IMPORTS --------------------------------- #
import datetime
import cdsapi
import json
import os
os.chdir('/home/lucas/storage/FORECAST/ERA5/')
# ------------------------------- GLOBAL STUFF ------------------------------- #
outdir='/home/lucas/storage/FORECAST/ERA5/'

#Times and daterange
ERA5_delay  = 5
ERA5_offset = 30                                                         # N° past days
today  = datetime.datetime.utcnow()-datetime.timedelta(days=ERA5_delay)  # ERA5 NRT delay
times  = [today-datetime.timedelta(days=n) for n in range(ERA5_offset)]  # Time vector
hours  = [
        '00:00', '01:00', '02:00',
        '03:00', '04:00', '05:00',
        '06:00', '07:00', '08:00',
        '09:00', '10:00', '11:00',
        '12:00', '13:00', '14:00',
        '15:00', '16:00', '17:00',
        '18:00', '19:00', '20:00',
        '21:00', '22:00', '23:00',
        ]
#Variables metadata
with open('ERA5_variables.json') as json_file:
    vmetadata = json.load(json_file)
    variables = ['lsm', 'tp', 'e'   , 'd2m', 'u10', 'v10', 'ewss',
                 'nsss', 't2m','ssr', 'str', 'strd', 'slhf', 'sshf']
    vlevt     = [vmetadata[v][3] for v in variables]
    vnames    = [vmetadata[v][0] for v in variables]

#latmax, lonmin, latmin, lonmax
area  = [-10, -90, -45, -65]

# -------------------------------- SOME FUNCS -------------------------------- #
def checktimerecord(fname):
    command="ncdump -h "+fname+" | head | grep -oP '(?<=time =).*?(?=;)'"
    try1=os.popen(command).read().replace(' ','').replace('\n','')
    return try1

def checkexpver(fname):
    try2=round(os.stat(fname).st_size/(1024**2),0)
    print(try2)
    if try2!=9:
        print('Wrong file size, checking expver ...')
        try:
            command='cdo --reduce_dim sellevel,1 '+fname+' tmp.nc'
            os.system(command)
            os.system('ncks --fix_rec_dmn time tmp.nc tmp2.nc')
            os.remove('tmp.nc')
            os.remove(fname)
            os.rename('tmp2.nc',fname)
            print('expver = 1 written as the new file.')
        except Exception as e:
            print('Changing expver didnt work:',e)
    return 

# --------------------------------- DOWNLOAD --------------------------------- #
c = cdsapi.Client()
if __name__=="__main__":
    for t in times:
        fname=outdir+t.strftime('%Y-%m-%d')+'.nc'
        options={
                'product_type': 'reanalysis',
                'type':'an',
                'date':t.strftime('%Y-%m-%d'),
                'variable': vnames,
                'time': hours,
                'area': area,
                'levtype':vlevt,
                'format':'netcdf'
                }
        print('                                                            ')
        print('------------------------------------------------------------')
        print('',datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),'')
        print(' Performing ERA5 data request, please wait...               ')
        print(' Date [yyyy-mm-dd] =',t.strftime('%Y-%m-%d'),'              ')
        print('------------------------------------------------------------')
        print('Request options: ')
        print(options)
        print('\n')
        if os.path.isfile(fname):
            print('File',fname,'already exists !!')
            print('Checking file consistency...')
            if checktimerecord(fname)!=str(len(hours)):
                print('File isnt full, downloading again...')
                try:
                    c.retrieve(
                    'reanalysis-era5-single-levels',
                    options,
                    fname)
                    checkexpver(fname)
                except Exception as e:
                    print('Download failed:',e)
            else:
                print('All good')
        else:
            print('Downloading', fname)
            try:
                c.retrieve(
                    'reanalysis-era5-single-levels',
                    options,
                    fname)
                checkexpver(fname)
            except Exception as e:
                print('Download failed:',e)
        print('Done')
        print('------------------------------------------------------------',
              '\n\n')
