import xarray as xr
import xesmf as xe
import pandas as pd
import datetime
import os


years = range(2015,2016+1)
lonmin,lonmax = -90,-69
latmin,latmax = -40,-15

variables = [
    'surf_el',
    'water_temp',
    'salinity',
    'water_u',
    'water_v']

renamedict = {'surf_el':'zos',
              'water_temp':'thetao',
              'salinity':'so',
              'water_u':'uo',
              'water_v':'vo'}

def get_hycom_filename(ftype):
    if ftype=='hindcast':
        url  = 'https://<Lucas.Glasner:y4vkrp7lqcv>@tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0'
    if ftype=='reanalysis':
        url  = 'https://<Lucas.Glasner:y4vkrp7lqcv>@tds.hycom.org/thredds/dodsC/GLBv0.08/expt_53.X/data'
    return url


def get_hycom_reanalysis(year, lonmin, lonmax, latmin, latmax, variables):
    url  = get_hycom_filename('reanalysis')+'/{}'.format(year)
    data = xr.open_dataset(url, decode_times=False)
    data = data[variables]
    data = data.sel(lat=slice(latmin,latmax), lon=slice(lonmin,lonmax))
    units,reference_date =  data.time.attrs['units'].split('since')
    time = [pd.Timedelta(hours=t)+pd.to_datetime(reference_date) for t in data.time.values]
    data.coords['time'] = ('time',time,data.time.attrs)
    return data
    
    

if __name__=='__main__':
    for yr in years:
        data = get_hycom_reanalysis(year=yr,
                            lonmin=lonmin, lonmax=lonmax,
                            latmin=latmin, latmax=latmax,
                            variables=variables)
        data = data.rename(renamedict)
        data = data.sel(time=str(yr))
        print(data)
        for m in range(1,12+1):
            try:
                print('Downloading data for ','Y{}M{}'.format(yr,str(m).zfill(2)),'please wait...')
                x = data.sel(time='{}-{}'.format(yr,str(m).zfill(2)))
                print('Resampling')
                x = x.resample({'time':'d'}).mean()
                x.coords['time'] = x.time+pd.Timedelta(hours=12)
                print('Saving...')
                x.to_netcdf('REANALYSIS/hycom_reanalysis_0p08_Y{}M{}.nc'.format(yr,str(m).zfill(2)),
                            encoding={
                                'time':{'units':'hours since 1950-01-01', 'dtype':float},
                                'zos':{'zlib':True, 'complevel':3},
                                'so':{'zlib':True, 'complevel':3},
                                'uo':{'zlib':True, 'complevel':3},
                                'vo':{'zlib':True, 'complevel':3},
                                'thetao':{'zlib':True, 'complevel':3}
                                    }
                                )
            except Exception as e:
                print('Download for ','Y{}M{}'.format(yr,str(m).zfill(2)),' failed:',e)
