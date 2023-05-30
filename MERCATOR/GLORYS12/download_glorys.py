import xarray as xr
import pandas as pd
import datetime
import os


first_date = '1993-01-01'
last_date  = '2022-12-31'

lonmin,lonmax = -90,-69
latmin,latmax = -40,-15

variables = [
    'zos',
    'thetao',
    'so',
    'uo',
    'vo']

encoding_opts = {
    'zos':{'zlib':True, 'complevel':5},
    'thetao':{'zlib':True, 'complevel':5},
    'so':{'zlib':True, 'complevel':5},
    'uo':{'zlib':True, 'complevel':5},
    'vo':{'zlib':True, 'complevel':5}
}

url  = 'https://lglasner:kpt6yrnsRvVm@my.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy_my_0.083_P1D-m'
data = xr.open_dataset(url)
data = data[variables]
data = data.sel(longitude=slice(lonmin,lonmax), latitude=slice(latmin,latmax))
data = data.sel(time=slice(first_date,last_date))

if __name__=='__main__':
    dates = pd.date_range(first_date, last_date, freq='m')
    for d in dates:
        try:
            print('Downloading data for ',d.strftime('%Y-%m'),'please wait...')
            x = data.sel(time=d.strftime('%Y-%m'))
            x.to_netcdf('glorys12v1_reanalysis_0p08_Y{}M{}.nc'.format(d.strftime('%Y'),d.strftime('%m')))
        except Exception as e:
            print('Download for ',d.strftime('%Y-%m'),' failed:',e)