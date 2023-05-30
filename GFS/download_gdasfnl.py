'''
 # @ Author: Your name
 # @ Create Time: 2023-04-10 16:49:24
 # @ Modified by: Your name
 # @ Modified time: 2023-04-10 16:49:29
 # @ Description:
 '''

# ---------------------------------------------------------------------------- #
import xarray as xr
import xesmf as xe
import pandas as pd
import os

# ---------------------------------------------------------------------------- #
first_date = '2021-01-01'
last_date  = '2022-12-31'

lonmin,lonmax = 360-90,360-69
latmin,latmax = -40,-15

fnlgfs_dictionary = {
    'Downward_Short-Wave_Radiation_Flux_surface':'dswrfsfc',
    'Downward_Long-Wave_Radp_Flux_surface':'dlwrfsfc',
    'Upward_Long-Wave_Radp_Flux_surface':'ulwrfsfc',
    'Upward_Short-Wave_Radiation_Flux_surface':'uswrfsfc',
    'u-component_of_wind_height_above_ground':'ugrd10m',
    'v-component_of_wind_height_above_ground':'vgrd10m',
    'Precipitation_rate_surface':'pratesfc',
    'Relative_humidity_height_above_ground':'rh2m',
    'Temperature_height_above_ground':'tmp2m',
}

flux_variables = [
    'Downward_Short-Wave_Radiation_Flux_surface',
    'Downward_Long-Wave_Radp_Flux_surface',
    'Upward_Short-Wave_Radiation_Flux_surface',
    'Upward_Long-Wave_Radp_Flux_surface'
    ]
    
bulk_variables   = [
    'u-component_of_wind_height_above_ground',
    'v-component_of_wind_height_above_ground',
    'Precipitation_rate_surface',
    'Relative_humidity_height_above_ground',
    'Temperature_height_above_ground',
    ]

gfs_variables = [
    'vgrd10m',
    'ugrd10m',
    'tmp2m',
    'rh2m',
    'pratesfc',
    'dswrfsfc',
    'dlwrfsfc',
    'uswrfsfc',
    'ulwrfsfc'
]

def get_GDASFNL_filename(idate, ftype):
    """
    This function builds the url for the openDAP webservice of
    the GDAS/FNL GFS archive dataset.

    Args:
        idate (str): date string as (%Y-%m-%d %H:%M:%S) format
        ftype (str): flux or bulk dataset

    Raises:
        ValueError: if ftype not flux or bulk

    Returns:
        str: opendap url
    """
    date    = pd.to_datetime(idate)
    year    = date.strftime('%Y')
    yrmonth = date.strftime('%Y%m')
    ftime   = date.strftime('%Y%m%d%H')
    if ftype == 'flux':
        url     = 'https://rda.ucar.edu/thredds/dodsC/files/g/ds084.4/'+year+'/'+yrmonth+'/gdas1.sflux.'+ftime+'.f00.grib2'
    elif ftype == 'bulk':
        url     = 'https://rda.ucar.edu/thredds/dodsC/files/g/ds083.3/'+year+'/'+yrmonth+'/gdas1.fnl0p25.'+ftime+'.f00.grib2'
    else:
        raise ValueError('ftype can only be "flux" or "bulk"')
    return url


def get_GDASFNL_bulks(idate, lonmin, lonmax, latmin, latmax, variables):
    """
    Given a date and a collection of variables this function grabs
    the GFS/FNL data from the opendap service

    Args:
        idate (_type_): _description_
        variables (_type_, optional): _description_. Defaults to bulk_variables.

    Returns:
        _type_: _description_
    """
    # NCEP GDAS/FNL 0.25 Degree Global Tropospheric Analyses and Forecast Grids
    bulkfiles = [get_GDASFNL_filename(idate+hour, 'bulk')
                 for hour in [' 00:00:00', ' 06:00:00', ' 12:00:00', ' 18:00:00']]
    bulks     = []
    for p in bulkfiles:
        data_bulk = xr.open_dataset(p)[variables]
        for height in range(4):
            try:
                data_bulk = data_bulk.isel({'height_above_ground'+str(height+1):0})
                data_bulk = data_bulk.drop('height_above_ground'+str(height+1))
            except:
                pass
            
        data_bulk = data_bulk.sortby('lat').sortby('lon').sel(
            lat=slice(latmin,latmax), lon=slice(lonmin,lonmax)).squeeze()
        data_bulk['time']    = pd.to_datetime(p.split('.')[-3], format='%Y%m%d%H')
        try:
            data_bulk = data_bulk.drop('reftime')
        except:
            pass
        try:
            data_bulk = data_bulk.drop_vars('reftime')
        except:
            pass
        bulks.append(data_bulk)
    data_bulk = xr.concat(bulks,'time')
    return data_bulk

def get_GDASFNL_flux(idate, lonmin, lonmax, latmin, latmax, variables):
    """
    Given a date and a collection of variables this function grabs
    the GFS/FNL data from the opendap service

    Args:
        idate (_type_): _description_
        variables (_type_, optional): _description_. Defaults to bulk_variables.

    Returns:
        _type_: _description_
    """
    # NCEP GDAS/FNL Global Surface Flux Grids
    fluxfiles = [get_GDASFNL_filename(idate+hour, 'flux')
                 for hour in [' 00:00:00', ' 06:00:00', ' 12:00:00', ' 18:00:00']]
    fluxes    = []
    for p in fluxfiles:
        data_flux = xr.open_dataset(p)[variables]
        data_flux = data_flux.squeeze()
        data_flux = data_flux.sortby('lat').sortby('lon').sel(lat=slice(latmin,latmax),
                                                              lon=slice(lonmin,lonmax))
        data_flux['time'] = pd.to_datetime(p.split('.')[-3], format='%Y%m%d%H')
        try:
            data_flux = data_flux.drop('reftime')
        except:
            pass
        try:
            data_flux = data_flux.drop_vars('reftime')
        except:
            pass
        fluxes.append(data_flux)
    data_flux = xr.concat(fluxes,'time')
    return data_flux


def get_GDASFNL_data(idate,
                     lonmin=lonmin, lonmax=lonmax,
                     latmin=latmin, latmax=latmax,
                     bulk_variables=bulk_variables,
                     flux_variables=flux_variables,
                     rename_dict=fnlgfs_dictionary,
                     outdir='./', save=False, mode='w'):
    """_summary_

    Args:
        idate (_type_): _description_
        bulk_variables (_type_, optional): _description_. Defaults to bulk_variables.
        flux_variables (_type_, optional): _description_. Defaults to flux_variables.
        rename_dict (_type_, optional): _description_. Defaults to fnlgfs_dictionary.
        outdir (str, optional): _description_. Defaults to './'.
        save (bool, optional): _description_. Defaults to False.
        mode (str, optional): _description_. Defaults to 'w'.

    Returns:
        _type_: _description_
    """
    fname = outdir+'/gdas1.fnl0p25.'+idate.replace('-','').replace(' ','')+'.f00.nc'
    if os.path.isfile(fname):
        return xr.open_dataset(fname)
        
    # ---------------------------------------------------------------------------- #
    # NCEP GDAS/FNL 0.25 Degree Global Tropospheric Analyses and Forecast Grids
    data_bulk = get_GDASFNL_bulks(idate,
                                  lonmin=lonmin, lonmax=lonmax,
                                  latmin=latmin, latmax=latmax,
                                  variables=bulk_variables)
    # ---------------------------------------------------------------------------- #
    # NCEP GDAS/FNL Global Surface Flux Grids
    data_flux = get_GDASFNL_flux(idate,
                                 lonmin=lonmin, lonmax=lonmax,
                                 latmin=latmin, latmax=latmax,
                                 variables=flux_variables)
    # ---------------------------------------------------------------------------- #
    # Regrid gaussian grid to regular and merge datasets
    regridder = xe.Regridder(data_flux, data_bulk, 'bilinear')
    data_flux = regridder(data_flux, keep_attrs=True)

    data = xr.merge([data_flux, data_bulk])
    data = data.rename(rename_dict)
    if save:
        data.to_netcdf(fname, mode=mode)
    return data

if __name__=='__main__':
    daterange = pd.date_range(first_date, last_date, freq='d')
    for date in daterange:
        try:
            print('Downloading data for ',date.strftime('%Y-%m-%d'))
            get_GDASFNL_data(date.strftime('%Y-%m-%d'), save=True, outdir='./gdasfnl/')
        except Exception as e:
            print('Download for ',date.strftime('%Y-%m-%d'),' failed:',e)
    