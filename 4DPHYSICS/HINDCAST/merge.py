import xarray as xr
import sys

yr = sys.argv[1]
month = sys.argv[2]

data = xr.open_mfdataset(str(yr)+'-'+str(month)+'*')
data.to_netcdf(str(yr)+'-'+str(month)+'.nc')