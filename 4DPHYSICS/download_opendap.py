#!/home/lucas/miniconda3/envs/forecast/bin/python3
"""
/**
 * @ Author: Your name
 * @ Create Time: 2023-04-26 08:35:47
 # @ Modified by: Your name
 # @ Modified time: 2023-04-26 14:40:29
 * @ Description:
 */
 
 Script for downloading 4D mercator operational forecast and hindcast
"""

# ---------------------------------------------------------------------------- #
import xarray as xr
import datetime
import pandas as pd
import os
import sys


# ---------------------------------------------------------------------------- #
rundir        = '/home/lucas/storage/FORECAST/MERCATOR/4DPHYSICS/'
start         = datetime.datetime.utcnow()
utcnow        = start.date()
date_min      = utcnow-datetime.timedelta(days=3)
date_max      = utcnow+datetime.timedelta(days=10)
latitude_min  = -40  
latitude_max  = -15  
longitude_min = -80  
longitude_max = -70    

os.chdir(rundir)

# ---------------------------------------------------------------------------- #
encoding_opts = {'vo': {"zlib":True,"complevel":4,
                        'original_shape': (4, 50, 301, 121),
                        'dtype': float,
                        '_FillValue': -32767,
                        'scale_factor': 1.0,
                        'add_offset': 0.0},
                'thetao': {"zlib":True,"complevel":4,
                        'original_shape': (4, 50, 301, 121),
                        'dtype': float,
                        '_FillValue': -32767,
                        'scale_factor': 1.0,
                        'add_offset': 0.0},
                'uo': {"zlib":True,"complevel":4,
                        'original_shape': (4, 50, 301, 121),
                        'dtype': float,
                        '_FillValue': -32767,
                        'scale_factor': 1.0,
                        'add_offset': 0.0},
                'so': {"zlib":True,"complevel":4,
                        'original_shape': (4, 50, 301, 121),
                        'dtype': float,
                        '_FillValue': -32767,
                        'scale_factor': 1.0,
                        'add_offset': 0.0},
                'zos': {"zlib":True,"complevel":4,
                        'original_shape': (4, 301, 121),
                        'dtype': float,
                        '_FillValue': -32767,
                        'scale_factor': 1.0,
                        'add_offset': 0.0}
                }
# ---------------------------------------------------------------------------- #
def download_hindcast():
    print('%'*100)
    print(datetime.datetime.utcnow())
    print('DOWNLOADING MERCATOR 6H INSTANTANEOUS HINDCAST: Global Ocean Physics Analysis and Forecast')
    print('Service id: GLOBAL_ANALYSISFORECAST_PHY_001_024-TDS')
    print('Time range: {}  -  {}'.format(date_min,utcnow-datetime.timedelta(days=1)))
    print('Spatial extent: ','{}°W-{}°W ; {}°S-{}°S'.format(abs(longitude_min),abs(longitude_max),abs(latitude_min),abs(latitude_max)))
    print('%'*100)
    urls = {'https://lglasner:kpt6yrnsRvVm@nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i':['uo','vo'],
            'https://lglasner:kpt6yrnsRvVm@nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-so_anfc_0.083deg_PT6H-i':['so'],
            'https://lglasner:kpt6yrnsRvVm@nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-thetao_anfc_0.083deg_PT6H-i':['thetao'],
            'https://lglasner:kpt6yrnsRvVm@nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy_anfc_0.083deg_PT1H-m':['zos']}
    
    exists = []
    for day in pd.date_range(date_min,utcnow, freq='d')[:-1]:
        fname = rundir+'/HINDCAST/'+day.strftime('%F')+'.nc'
        if os.path.isfile(fname):
            try:
                data = xr.open_dataset(fname)
                if len(data.time)!=4:
                    exists.append(False)
                else:
                    exists.append(True)
            except:
                exists.append(False)
        else:
            exists.append(False)
    if sum(exists)!=len(pd.date_range(date_min,utcnow, freq='d')[:-1]):
        pass
    else:
        print('\nFiles for requested dates are already on disk !!\n')
        return

    try:
        DATA = []
        for url,variables in zip(urls.keys(),urls.values()):
            print('Loading '+'-'.join(variables)+' from opendap service:',url.split("@")[-1])
            data = xr.open_dataset(url)[variables]
            data = data.sel(time=slice(date_min,utcnow)).isel(time=slice(0,-1))
            data = data.sel(longitude=slice(longitude_min,longitude_max),latitude=slice(latitude_min,latitude_max))
            if variables==['zos']:
                data=data.reindex({'time':DATA[0].time}, method='nearest')
            DATA.append(data.squeeze())
            del data
        print('Joining datasets...')
        DATA = xr.merge(DATA).drop_duplicates('time')
    except Exception as e:
        print('Something failed:',e)
    print('Saving to disk:')
    for day in pd.date_range(date_min,utcnow, freq='d')[:-1]:
        fname = rundir+'/HINDCAST/'+day.strftime('%F')+'.nc'
        if os.path.isfile(fname):
            print('\tFile:',day.strftime('%F')+'.nc already exists!!!','\n\tChecking consistency...')
            try:
                data = xr.open_dataset(fname)
                if len(data.time)!=4:
                    print('\tData is incomplete downloading again...')
                    try:
                        os.remove(fname)
                        print('\tFile:',day.strftime('%F')+'.nc')
                        DATA.sel(time=day.strftime('%F')).to_netcdf(fname, format='NETCDF4',
                                                                engine='netcdf4',
                                                                encoding=encoding_opts)
                    except Exception as e:
                        print('\tDownload failed: ',e)
                else:
                        print('\tAll good')
            except:
                print('\tData is corrupt downloading again...')
                try:
                    os.remove(fname)
                    print('\tFile:',day.strftime('%F')+'.nc')
                    DATA.sel(time=day.strftime('%F')).to_netcdf(fname, format='NETCDF4',
                                                            engine='netcdf4',
                                                            encoding=encoding_opts)
                except Exception as e:
                    print('\tDownload failed: ',e)
        else:   
            try:
                print('\tFile:',day.strftime('%F')+'.nc')
                DATA.sel(time=day.strftime('%F')).to_netcdf(fname, format='NETCDF4',
                                                        engine='netcdf4',
                                                        encoding=encoding_opts)
            except Exception as e:
                print('\tDownload failed: ',e)
        print('\n')
    print('Elapsed time: ',datetime.datetime.utcnow()-start)
    print('All good\n\n\n')
    return

# ---------------------------------------------------------------------------- #
def download_forecast():
    print('%'*100)
    print(datetime.datetime.utcnow())
    print('DOWNLOADING MERCATOR DAILY FORECAST: Global Ocean Physics Analysis and Forecast')
    print('Service id: GLOBAL_ANALYSISFORECAST_PHY_001_024-TDS')
    print('Spatial extent: ','{}°W-{}°W ; {}°S-{}°S'.format(abs(longitude_min),abs(longitude_max),abs(latitude_min),abs(latitude_max)))
    print('%'*100)
    urls = {'https://lglasner:kpt6yrnsRvVm@nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m':['uo','vo'],
            'https://lglasner:kpt6yrnsRvVm@nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m':['so'],
            'https://lglasner:kpt6yrnsRvVm@nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m':['thetao'],
            'https://lglasner:kpt6yrnsRvVm@nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy_anfc_0.083deg_P1D-m':['zos']}

    for i in range((utcnow-date_min).days):
        fname = rundir+(utcnow-datetime.timedelta(days=i)).strftime('%F')+'.nc'
        print('Downloading: ',fname)
        if os.path.isfile(fname):
            print('\tFile:',fname,'already exists!!!','\n\tChecking consistency...')
            try:
                data = xr.open_dataset(fname)
                if len(data.time)!=10:
                    print('\tData is incomplete downloading again...')
                    try:
                        DATA = []
                        for url,variables in zip(urls.keys(),urls.values()):
                            print('\tLoading '+'-'.join(variables)+' from opendap service:',url.split("@")[-1])
                            data = xr.open_dataset(url)[variables]
                            data = data.sel(time=slice(utcnow-datetime.timedelta(days=i),date_max-datetime.timedelta(days=i)))
                            data = data.sel(longitude=slice(longitude_min,longitude_max),latitude=slice(latitude_min,latitude_max))
                            DATA.append(data.squeeze())
                            del data
                        print('\tJoining datasets...')
                        DATA = xr.merge(DATA).drop_duplicates('time')
                        print('\tSaving to disk...')
                        DATA.to_netcdf(fname, format='NETCDF4',engine='netcdf4',encoding=encoding_opts)
                    except Exception as e:
                        print('\tSomething failed:',e)
                    print('\tDone')
                else:
                    print('\tAll good')   
            except:
                print('\tData is corrupt downloading again...')
                try:
                    DATA = []
                    for url,variables in zip(urls.keys(),urls.values()):
                        print('\tLoading '+'-'.join(variables)+' from opendap service:',url.split("@")[-1])
                        data = xr.open_dataset(url)[variables]
                        data = data.sel(time=slice(utcnow-datetime.timedelta(days=i),date_max-datetime.timedelta(days=i)))
                        data = data.sel(longitude=slice(longitude_min,longitude_max),latitude=slice(latitude_min,latitude_max))
                        DATA.append(data.squeeze())
                        del data
                    print('\tJoining datasets...')
                    DATA = xr.merge(DATA)
                    print('\tSaving to disk...')
                    DATA.to_netcdf(fname, format='NETCDF4',engine='netcdf4',encoding=encoding_opts)
                except Exception as e:
                    print('\tSomething failed:',e)
                print('\tDone') 
        else:     
            try:
                DATA = []
                for url,variables in zip(urls.keys(),urls.values()):
                    print('\tLoading '+'-'.join(variables)+' from opendap service:',url.split("@")[-1])
                    data = xr.open_dataset(url)[variables]
                    data = data.sel(time=slice(utcnow-datetime.timedelta(days=i),date_max-datetime.timedelta(days=i)))
                    data = data.sel(longitude=slice(longitude_min,longitude_max),latitude=slice(latitude_min,latitude_max))
                    DATA.append(data.squeeze())
                    del data
                print('\tJoining datasets...')
                DATA = xr.merge(DATA)
                print('\tSaving to disk...')
                DATA.to_netcdf(fname, format='NETCDF4',engine='netcdf4',encoding=encoding_opts)
            except Exception as e:
                print('\tSomething failed:',e)
            print('\tDone')
        print('\n')
    print('Elapsed time: ',datetime.datetime.utcnow()-start)
    print('All good')
    return

if __name__=='__main__':
    download_hindcast()
    download_forecast()
    sys.exit()
