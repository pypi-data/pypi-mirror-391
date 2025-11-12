from aceti.common_maps import import_map, MapDownloader
import numpy as np
import matplotlib.pyplot as plt
import PIL

def plot_grid(map):
    ''' Plot a grid on top of a map. '''

    #check map properties
    if isinstance(map, str):
        base_matrix, lat_lon_map  = import_map(map)
    elif isinstance(map, tuple):
        base_matrix, lat_lon_map  = map
        if isinstance(base_matrix, np.ndarray) and isinstance(lat_lon_map, np.ndarray):
            if not np.all(np.isin(base_matrix, [0, 1])):
                raise ValueError("base_matrix must be a numpy array of 0s and 1s")
            if base_matrix.shape != lat_lon_map.shape:
                raise ValueError("base_matrix and lat_lon_map must have the same shape")
            if not np.all(np.apply_along_axis(lambda x: isinstance(x, tuple) and len(x) == 2 and all(isinstance(i, float) for i in x), 1, lat_lon_map)):
                raise ValueError("lat_lon_map must be a numpy array of tuples of 2 coordinates, [lat, lon]")
        else:
            raise ValueError("map must be a string or a tuple of [base_matrix, lat_lon_map]")
    else:
        raise ValueError("map must be a string or a tuple of [base_matrix, lat_lon_map]")
    # Plot the map
    print("lat_lon_map shape: ", lat_lon_map.shape)
    print("base_matrix shape: ", base_matrix.shape)
    print("lat_lon_map: ", lat_lon_map[0, 0])
    print("lat_lon_map: ", lat_lon_map[-1, -1])
    #to tuple
    northwest = [float(lat_lon_map[0, 0][0]), float(lat_lon_map[0, 0][1])]
    southeast = [float(lat_lon_map[-1, -1][0]), float(lat_lon_map[-1, -1][1])]
    map=MapDownloader(northwest, southeast, zoom=19, layer="s", server ="arcgis") 
    map.generateImage()
    # map.raw_map_img = PIL.Image.open("AlamilloPlantilla.png")
    # plt.imshow(map.map_img)
    # plt.savefig("alamillo95x216.png", dpi=600)
    map.show_grid(lat_lon_map, base_matrix)

    # plt.figure()
    # plt.imshow(base_matrix, cmap='gray', interpolation='nearest')
    # plt.show()

    


# csv_to_npy("alamillo95x216")
# csv_to_png("alamillo95x216plantilla")

# plot_grid("alamilloaccess11x15")
# plot_grid("alamillo95x216")
plot_grid("/home/aloepacci/guadaira")
# plot_grid("alamillo30x49")
# map=MapDownloader([37.191611287951396, -4.399097018031518], [37.188098777474906, -4.394347328263865], zoom=19, layer="s", server ="arcgis")
# map=MapDownloader([37.341664356846564, -5.858012026866486], [37.33741741302848, -5.855613536856963], zoom=19, layer="s", server ="arcgis")
# map.save_navigation_waters(name="guadaira")

# plt.imshow(map.map_img)
# plt.axis('off')
# plt.savefig("guadaira.png", dpi=600)


