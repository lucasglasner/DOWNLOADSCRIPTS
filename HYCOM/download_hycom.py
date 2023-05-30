import xarray as xr
import xesmf as xe
import pandas as pd
import datetime
import os


first_date = '2021-01-01'
last_date  = '2022-12-31'

lonmin,lonmax = 360-90,360-69
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
    return url


def get_hycom_hindcast(first_date, last_date, lonmin, lonmax, latmin, latmax, variables):
    url  = get_hycom_filename('hindcast')
    data = xr.open_dataset(url, decode_times=False)
    data = data[variables]
    data = data.sel(lat=slice(latmin,latmax), lon=slice(lonmin, lonmax))
    attrs = data.time.attrs
    units,reference_date =  data.time.attrs['units'].split('since')
    time = [pd.Timedelta(hours=t)+pd.to_datetime(reference_date) for t in data.time.values]
    data.coords['time'] = ('time',time, {'long_name':attrs['long_name'],
                                         'axis':attrs['axis'],
                                         'NAVO_code':attrs['NAVO_code']})
    data = data.sel(time=slice(first_date, last_date))
    return data
    
    

if __name__=='__main__':
    data = get_hycom_hindcast(first_date=first_date,
                        last_date=last_date,
                        lonmin=lonmin, lonmax=lonmax,
                        latmin=latmin, latmax=latmax,
                        variables=variables)
    data = data.rename(renamedict)
    daterange = pd.date_range(first_date, last_date, freq='d')
    for date in daterange:
        datestr = date.strftime('%Y-%m-%d')
        try:
            print('Downloading data for ',datestr,'please wait...')
            x = data.sel(time=datestr).resample({'time':'d'}).mean()
            x.coords['time'] = x.time+pd.Timedelta(hours=12)
            x.to_netcdf(
                        'HINDCAST/hycom_hindcast_0p08_{}.nc'.format(date.strftime('%Y%m%d')),
                        encoding={
                            'time':{'units':'hours since 2000-01-01', 'dtype':float},
                            'zos':{'zlib':True, 'complevel':3},
                            'so':{'zlib':True, 'complevel':3},
                            'uo':{'zlib':True, 'complevel':3},
                            'vo':{'zlib':True, 'complevel':3},
                            'thetao':{'zlib':True, 'complevel':3}
                                }
                        )
        except Exception as e:
            print('Download for ',datestr,' failed:',e)
    
