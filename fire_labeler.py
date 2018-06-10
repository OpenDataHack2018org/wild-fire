import cartopy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import datetime
import glob
import matplotlib.pyplot as plt
import netCDF4
import numpy as np
import os
import pyproj
import sys

plt.rcParams['animation.ffmpeg_path'] = 'C:/ffmpeg-20180608-2bd26de-win64-static/bin/ffmpeg.exe'

import matplotlib.animation as animation

class UnsupportedVersion(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

if sys.version_info < (2, 7) or sys.version_info >= (2, 8):
    raise UnsupportedVersion('requires Python 2.7.x')

__version__ = '0.0.0'

# Create WGS84 geod used in distance measurement
wgs84 = pyproj.Geod(ellps='WGS84')

# Define bounding boxes
country_bbox = [32.5343, (-124.4096 + 360.0) % 360.0, 42.0095, (-114.1308 + 360.0) % 360.0] # California
country_bbox = [32.5343 - 10, (-124.4096 + 360.0) % 360.0 - 10, 42.0095 + 10, (-114.1308 + 360.0) % 360.0 + 10] # California + 10 degrees

# Define fire parameters
min_fire_radiative_power = 0.1
max_fire_spread_radius = 60000.0
max_fire_persistence_seconds = 60 * 60 * 24 * 3

# Glob .nc paths (do not mix files with different spatial resolution)
nc_pattern = './cams_fire/*.nc'
nc_paths = glob.glob(nc_pattern)

# Open all .nc files
datasets = sorted([netCDF4.Dataset(path) for path in nc_paths], key=lambda ds: ds['time'][0])

# Get lat/lons from the first file
lat = datasets[0]['latitude'][:]
lon = datasets[0]['longitude'][:]

# Get lat/lon step
lat_step = np.abs(np.diff(lat)[0])
lon_step = np.abs(np.diff(lon)[0])

# Determine which lat/lons to use
use_lat = np.logical_and(lat + lat_step * 0.5 > country_bbox[0], lat - lat_step * 1.5 < country_bbox[2])
use_lon = np.logical_and(lon + lon_step * 0.5 > country_bbox[1], lon - lon_step * 1.5 < country_bbox[3])

lat = lat[use_lat]
lon = lon[use_lon]

# Combine and subset time and fire radiative power
times = [datetime.datetime(1900, 1, 1) + datetime.timedelta(hours=hours) for hours in np.concatenate([ds['time'][:] for ds in datasets])]
frp = np.vstack([ds['frpfire'][:, use_lat][:, :, use_lon] for ds in datasets])

# Use plateCarree projection for lat/lon data
cproj = ccrs.PlateCarree()

# Create matplotlib figure and axes
fig = plt.gcf()
fig.set_size_inches(18.5, 10.5)
fig.subplots_adjust(left=0, right=1, bottom=0.02, top=0.95)

stamen_terrain = cimgt.StamenTerrain()

ax_1 = plt.subplot(1, 2, 1, projection=stamen_terrain.crs)
ax_2 = plt.subplot(1, 2, 2, projection=stamen_terrain.crs)

ax_1.add_image(stamen_terrain, 6)
ax_2.add_image(stamen_terrain, 6)

map_extent = [country_bbox[1] - 2, country_bbox[3] + 2, country_bbox[0] - 2, country_bbox[2] + 2]

ax_1.set_extent(map_extent, cproj)
ax_2.set_extent(map_extent, cproj)

ax_1.add_feature(cartopy.feature.COASTLINE)
ax_2.add_feature(cartopy.feature.COASTLINE)

ax_1.add_feature(cartopy.feature.BORDERS, linestyle='-')
ax_2.add_feature(cartopy.feature.BORDERS, linestyle='-')

# Define two pcolormesh grids for dynamic data
pcm_1 = ax_1.pcolormesh(lon - lon_step * 0.5, lat - lat_step * 0.5, frp[0], transform=cproj, vmin=0.0, vmax=min_fire_radiative_power, alpha=0.8)
pcm_2 = ax_2.pcolormesh(lon - lon_step * 0.5, lat - lat_step * 0.5, frp[0], transform=cproj, vmin=0.0, vmax=1.0, cmap='rainbow', alpha=0.8)

fires = []

def plot_frame(t_i):
    print('Processing time %i out of %i' % (t_i + 1, frp.shape[0]))

    # Update fires
    doused_fires = []
    for fire in fires:
        fire_doused = True
        for tile in fire['tiles']:
            tile['time_since_fire'] += 60 * 60 * 24
            if tile['time_since_fire'] <= max_fire_persistence_seconds:
                fire_doused = False
        if fire_doused:
            doused_fires.append(fire)

    for fire in doused_fires:
        fires.remove(fire)

        age = (fire['last_update_at'] - fire['started_at'] + 1) * 60 * 60 * 24

        area = 0.0
        for tile in fire['tiles']:
            _, _, length_x = wgs84.inv(lon[tile['lon_i']], lat[tile['lat_i']], lon[tile['lon_i']] + lon_step, lat[tile['lat_i']])
            _, _, length_y = wgs84.inv(lon[tile['lon_i']], lat[tile['lat_i']], lon[tile['lon_i']], lat[tile['lat_i']] + lat_step)
            area += length_x * length_y

        print('Fire doused (area: %f m, radiative power sum: %f W m**-2, age: %i seconds)' % (area, fire['frp_sum'], age))

    fire_indices = np.where(frp[t_i] >= min_fire_radiative_power)

    for ti_i in range(fire_indices[0].shape[0]):
        lat_i = fire_indices[0][ti_i]
        lon_i = fire_indices[1][ti_i]

        tile_frp = frp[t_i, lat_i, lon_i]

        found = False
        for fire in fires:
            for tile in fire['tiles']:
                if tile['lat_i'] == lat_i and tile['lon_i'] == lon_i:
                    fire['frp_sum'] += tile_frp
                    fire['last_update_at'] = t_i
                    tile['time_since_fire'] = 0.0
                    found = True
                    break

        if not found:
            fire_tile = { 'lat_i': lat_i, 'lon_i': lon_i, 'time_since_fire': 0.0, 'added_at': t_i }

            for fire in fires:
                for tile in fire['tiles']:
                    if tile['time_since_fire'] <= max_fire_persistence_seconds and tile['added_at'] < t_i:
                        _, _, dist = wgs84.inv(lon[lon_i], lat[lat_i], lon[tile['lon_i']], lat[tile['lat_i']])
                        if dist <= max_fire_spread_radius:
                            fire['tiles'].append(fire_tile)
                            fire['frp_sum'] += tile_frp
                            fire['last_update_at'] = t_i
                            found = True
                            break

            if not found:
                fires.append({ 'tiles': [fire_tile], 'color': np.random.rand(1)[0], 'frp_sum': tile_frp, 'started_at': t_i, 'last_update_at': t_i })

    # Update pcolormesh data
    fire_color = np.zeros(frp[0].shape)
    for fire in fires:
        for tile in fire['tiles']:
            fire_color[tile['lat_i'], tile['lon_i']] = fire['color']

    pcm_1.set_array(frp[t_i, :-1, :-1].ravel())
    pcm_2.set_array(fire_color[:-1, :-1].ravel())

    # Update titles
    ax_1.set_title('Fire radiative power at %s\nMap tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL' % times[t_i].isoformat(), fontsize=10)
    ax_2.set_title('Connected fires by color\nFRP threshold: %f, spread radius: %.2f m, persistence seconds: %i, unique fires: %i' % (min_fire_radiative_power, max_fire_spread_radius, max_fire_persistence_seconds, len(fires)), fontsize=10)

    # Save frame as image
    fig.savefig('frames/frame_%i.png' % t_i, dpi=100)

    # Return the edited artists
    return [pcm_1, pcm_2]

ani = animation.FuncAnimation(fig, plot_frame, frames=len(times), interval=200, repeat=True, blit=False)

# Create movie
Writer = animation.writers['ffmpeg']
writer = Writer(fps=10, bitrate=1800)
ani.save('fire_labels.mp4', writer=writer)
