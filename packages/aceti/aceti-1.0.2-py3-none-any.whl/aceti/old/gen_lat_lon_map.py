import sys
sys.path.append('.')

from Environment.generate_map import img2pixels

import numpy as np

# Esquina inferior izquierda
lat = np.float64(37.41856004857407)
lon = np.float64(-6.001322282719345)

# Esquina superior derecha
lat2 = np.float64(37.41953493274117)
lon2 = np.float64(-5.9987915127912)

path = 'Environment/maps/alamillo.png'

pixels = img2pixels(path, threshold=128, height=40)

pixels = 1 - pixels

# Sabiendo que lat,lon hace referencia a la esquina inferior izquierda y lat2,lon2 a la esquina superior derecha,
# calculamos, para cada pixel, su latitud y longitud
latitudes = np.linspace(lat2, lat, pixels.shape[0], dtype=np.float64)
longitudes = np.linspace(lon, lon2, pixels.shape[1], dtype=np.float64)

# Creamos un array de MxNx2 dimensiones con las latitudes y longitudes
lat_lon_map = np.zeros((pixels.shape[0], pixels.shape[1], 2), dtype=np.float64)

for i in range(pixels.shape[0]):
    for j in range(pixels.shape[1]):
        lat_lon_map[i,j] = [latitudes[i], longitudes[j]]
        
np.save('Environment/maps/lat_lon_alamillo_big.npy', lat_lon_map)
np.save('Environment/maps/alamillo_big.npy', pixels)



