import numpy as np
from scipy.ndimage import binary_dilation
import matplotlib.pyplot as plt

# NODOS
nodos_mask = np.load('Environment/maps/AlamilloAccess11x15mask.npy')
nodos_lat_lon = np.load('Environment/maps/AlamilloAccess11x15latlon.npy')

# "REALES"
real_mask = np.genfromtxt('Environment/maps/rawfiles/Alamillo95x216plantilla.csv', dtype=int, delimiter=' ')
raw_grid_csv = np.genfromtxt('Environment/maps/rawfiles/Alamillo95x216grid.csv', delimiter=';', dtype=str)
real_lat_long = np.zeros((*real_mask.shape, 2))
# Transform the map to a float for long and lat
for i in range(real_mask.shape[0]):
	for j in range(real_mask.shape[1]):
		real_lat_long[i, j, 0] = float(raw_grid_csv[i, j].split(',')[0])
		real_lat_long[i, j, 1] = float(raw_grid_csv[i, j].split(',')[1])

latitudes = real_lat_long[:,:, 0]
longitudes = real_lat_long[:,:, 1]

navigables_latitudes = latitudes[real_mask == 1]
navigables_longitudes = longitudes[real_mask == 1]

# Comprobar si los puntos de navegación en el mapa real están en el mapa de nodos
# Para cada punto navegable (1) en base_matrix, obtener su latitud y longitud. Y comprobar si todos son alcanzables.
cont_unreach = 0
cont_reach = 0
non_reachable_points = []
reachable_points = []
for i in range(nodos_mask.shape[0]):
	for j in range(nodos_mask.shape[1]):
		if nodos_mask[i, j] == 1:
			# Comprobar si está como navegable en el mapa de navegación
			if nodos_lat_lon[i, j, 0] in navigables_latitudes and nodos_lat_lon[i, j, 1] in navigables_longitudes:
				# Obtener los índices de la latitud y longitud en el mapa de navegación
				lat_indexs = np.where(navigables_latitudes == nodos_lat_lon[i, j, 0])[0]
				lon_indexs = np.where(navigables_longitudes == nodos_lat_lon[i, j, 1])[0]

				# Comprobar si hay algún índice en común
				if len(set(lat_indexs).intersection(set(lon_indexs))) == 0:
					print(f'No alcanzable (no común): {nodos_lat_lon[i, j, 0]}, {nodos_lat_lon[i, j, 1]}')
					cont_unreach += 1
					non_reachable_points.append((i, j))
				else:
					cont_reach += 1
					reachable_points.append((i, j))
			else:
				print(f'No alcanzable: {nodos_lat_lon[i, j, 0]}, {nodos_lat_lon[i, j, 1]}')
				cont_unreach += 1
				non_reachable_points.append((i, j))


if cont_unreach == 0:
	print(f'Todos los puntos son alcanzables: {cont_reach}')
else:
	print(f'{cont_unreach} puntos no son alcanzables de un total de {np.sum(nodos_mask)}')

# Pintar los puntos no alcanzables
plt.imshow(nodos_mask)
for point in non_reachable_points:
	plt.scatter(point[1], point[0], c='r', s=10)
for point in reachable_points:
	plt.scatter(point[1], point[0], c='g', s=10)
plt.show()