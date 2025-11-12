import numpy as np
import os
import sys
from matplotlib import pyplot as plt


if sys.version_info < (3, 9):
    # importlib.resources either doesn't exist or lacks the files() function, so use the PyPI version:
    import importlib_resources
else:
    # importlib.resources has files(), so use that:
    import importlib.resources as importlib_resources
pkg = importlib_resources.files("aceti")

def import_map(map_name: str):
    """
    Import a map from a file and return the base matrix and lat/lon map.
    Args:
        map_name (str): The name of the map to import.
    Returns:
        tuple: A tuple containing the base matrix and lat/lon map.
    """
    map_name = find_map(map_name)

    try:
        base_matrix =  np.load(f"{map_name}mask.npy")
    except FileNotFoundError:
        raise ValueError(f"No binnary mask found in package directory {map_name}mask.npy")
    # Load the lat/lon map
    try:
        lat_lon_map = np.load(f"{map_name}latlon.npy", allow_pickle=True)
    except FileNotFoundError:
        raise ValueError(f"No latlon mask found in package directory {map_name}latlon.npy")
    
    base_matrix = base_matrix.astype(int)
    return base_matrix, lat_lon_map


def plot_map(map_name):
    ''' Convert a CSV file to a binary image. '''
    map_name = find_map(map_name)
    binary_image = np.load(pkg.joinpath("maps", f"{map_name}mask.npy"))

    # Convert the binary image to 0s and 255s
    binary_image = np.where(binary_image > 0, 255, 0)

    plt.imshow(binary_image, cmap='gray')
    plt.axis('off')
    plt.show()

def map_downsize(map_name, factor=2):
    ''' Downsize a map. '''
    map_name = find_map(map_name)
    binary_image = np.load(pkg.joinpath("maps", f"{map_name}mask.npy"))
    return binary_image[::factor, ::factor]

def map_shrink(map_name, init_column=0, final_column=None, init_row=0, final_row=None):
    ''' Shrink a map. '''
    map_name = find_map(map_name)
    binary_image = np.load(pkg.joinpath("maps", f"{map_name}mask.npy"))

    # Set the final column and row if they are None
    if final_column is None:
        final_column = binary_image.shape[1]
    if final_row is None:
        final_row = binary_image.shape[0]

    # Shrink the binary image
    return binary_image[init_row:final_row, init_column:final_column]

def plot_grid(map):
    ''' Plot a grid on top of a map. '''
    base_matrix, lat_lon_map  = import_map(map)

    # if isinstance(base_matrix, np.ndarray) and isinstance(lat_lon_map, np.ndarray):
    #     if not np.all(np.isin(base_matrix, [0, 1])):
    #         raise ValueError("base_matrix must be a numpy array of 0s and 1s")
    #     if base_matrix.shape != lat_lon_map.shape:
    #         raise ValueError("base_matrix and lat_lon_map must have the same shape")
    #     if not np.all(np.apply_along_axis(lambda x: isinstance(x, tuple) and len(x) == 2 and all(isinstance(i, float) for i in x), 1, lat_lon_map)):
    #         raise ValueError("lat_lon_map must be a numpy array of tuples of 2 coordinates, [lat, lon]")
    # else:
    #     raise ValueError("map must be a string or a tuple of [base_matrix, lat_lon_map]")
    # Plot the map
    from aceti import MapDownloader
    map=MapDownloader(lat_lon_map[0, 0], lat_lon_map[-1, -1], zoom=19, layer="s", server ="arcgis")  #TODO: assign zoom depending on size
    map.show_grid(lat_lon_map, base_matrix)


def find_map(map_name):
    ''' Find a map in the package directory. '''
    map_name = map_name.lower()
    if os.path.exists(f'{map_name}mask.npy') and os.path.exists(f'{map_name}latlon.npy'):
        print(f"Map {map_name} found ")
        return map_name
    elif os.path.exists(pkg.joinpath("maps", f"{map_name}mask.npy")) and os.path.exists(pkg.joinpath("maps", f"{map_name}latlon.npy")):
        print(f"Map {map_name} found in package directory")
        return pkg.joinpath(f"maps/{map_name}")
    else:
        #check for path
        if os.path.exists(f'{map_name}mask.csv'):
            binary_image = np.loadtxt(f'{map_name}mask.csv', delimiter=" ")
        elif os.path.exists(f'{map_name}plantilla.csv'):
            binary_image = np.loadtxt(f'{map_name}plantilla.csv', delimiter=" ")
        else:
            raise ValueError('map binnary not found')

        if os.path.exists(f'{map_name}latlon.csv'):
            latlon_image = np.loadtxt(f'{map_name}latlon.csv', delimiter=";", dtype=str)
        elif os.path.exists(f'{map_name}grid.csv'):
            latlon_image = np.loadtxt(f'{map_name}grid.csv', delimiter=";", dtype=str)
        else:
            raise ValueError('map latlon not found')
        # Convert to npy
        print("maps found, converting to npy")
        np.save(f'{map_name}mask.npy', binary_image)


        lat_lon_map = np.zeros((binary_image.shape[0], binary_image.shape[1], 2), dtype=np.float64)
        # Convert the strings to tuples
        for i in range(binary_image.shape[0]):
            for j in range(binary_image.shape[1]):
                lat = latlon_image[i, j].split(',')[0]
                lon = latlon_image[i, j].split(',')[1]
                lat_lon_map[i, j] = [float(lat), float(lon)]
        # Save the binary image as a NumPy file
        np.save(f'{map_name}latlon.npy', lat_lon_map)
        return map_name

