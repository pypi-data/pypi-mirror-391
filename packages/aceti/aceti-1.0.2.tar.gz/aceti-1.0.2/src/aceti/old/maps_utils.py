import cv2
import numpy as np
import os 

def png_to_csv(name, delim=' '):
    ''' Convert a binary image to a CSV file. '''
    # Load the image
    image = cv2.imread(f'Environment/maps/{name}.png', 0)

    # Binarize the image
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # Convert the binary image to 0s and 1s
    binary_image = np.where(binary_image > 0, 1, 0)

    # Save the binary image as a CSV file
    np.savetxt(f'Environment/maps/{name}.csv', binary_image, delimiter=delim, fmt='%d')

def csv_to_png(name, delim=' '):
    ''' Convert a CSV file to a binary image. '''
    # Load the CSV file
    binary_image = np.loadtxt(f'{name}.csv', delimiter=delim)

    # Convert the binary image to 0s and 255s
    binary_image = np.where(binary_image > 0, 255, 0)

    # Save the binary image as a PNG file
    cv2.imwrite(f'{name}.png', binary_image)

def csv_to_npy(name):
    ''' Convert a CSV file to a NumPy file. '''
    if os.path.exists(f'{name}mask.csv'):
        binary_image = np.loadtxt(f'{name}mask.csv', delimiter=" ")
    elif os.path.exists(f'{name}plantilla.csv'):
        binary_image = np.loadtxt(f'{name}plantilla.csv', delimiter=" ")
    else:
        raise ValueError('The file does not exist')

    # Save the binary image as a NumPy file
    np.save(f'{name}mask.npy', binary_image)

    if os.path.exists(f'{name}latlon.csv'):
        latlon_image = np.loadtxt(f'{name}latlon.csv', delimiter=";", dtype=str)
    elif os.path.exists(f'{name}grid.csv'):
        latlon_image = np.loadtxt(f'{name}grid.csv', delimiter=";", dtype=str)
    else:
        raise ValueError('The file does not exist')

    lat_lon_map = np.zeros((binary_image.shape[0], binary_image.shape[1], 2), dtype=np.float64)

    # Convert the strings to tuples
    for i in range(binary_image.shape[0]):
        for j in range(binary_image.shape[1]):
            try:
                lat = latlon_image[i, j].split(',')[0]
                lon = latlon_image[i, j].split(',')[1]
                lat_lon_map[i, j] = [float(lat), float(lon)]
            except:
                pass
    # Save the binary image as a NumPy file
    np.save(f'{name}latlon.npy', lat_lon_map)


def csv_downsize(name, delim=' ', factor=2, output_name=None):
    ''' Downsize a CSV file. '''
    # Load the CSV file
    binary_image = np.loadtxt(f'Environment/maps/{name}.csv', delimiter=delim, dtype=str)

    # Downsize the binary image
    binary_image = binary_image[::factor, ::factor]

    output_name1 = output_name.split('_')[0]
    output_name2 = output_name.split('_')[1]

    # Save the binary image as a CSV file
    np.savetxt(f'Environment/maps/{output_name1}{binary_image.shape[0]}x{binary_image.shape[1]}{output_name2}.csv', binary_image, delimiter=delim, fmt='%s')

def csv_shrink(name, delim=' ', init_column=0, final_column=None, init_row=0, final_row=None, output_name=None):
    ''' Shrink a CSV file. '''
    # Load the CSV file
    binary_image = np.loadtxt(f'Environment/maps/{name}.csv', delimiter=delim, dtype=str)

    # Set the final column and row if they are None
    if final_column is None:
        final_column = binary_image.shape[1]
    if final_row is None:
        final_row = binary_image.shape[0]

    # Shrink the binary image
    binary_image = binary_image[init_row:final_row, init_column:final_column]

    output_name1 = output_name.split('_')[0]
    output_name2 = output_name.split('_')[1]

    # Save the binary image as a CSV file
    np.savetxt(f'Environment/maps/{output_name1}{binary_image.shape[0]}x{binary_image.shape[1]}{output_name2}.csv', binary_image, delimiter=delim, fmt='%s')

def get_output_name(name):
    ''' Get the output name if the format is correct. '''
    output_name = name
    first_number_pos = None
    last_number_pos = None
    for i, c in enumerate(name):
        if c.isdigit():
            if first_number_pos is None:
                first_number_pos = i
            last_number_pos = i
    if first_number_pos is not None and last_number_pos is not None:
        output_name = name[:first_number_pos] + '_' + name[last_number_pos+1:]
    else:
        output_name = 'output_map'
    return output_name

def invert_map(name, delim=' '):
    ''' Invert a map. '''
    # Load the CSV file
    binary_image = np.loadtxt(f'Environment/maps/{name}.csv', delimiter=delim)

    # Invert the binary image
    binary_image = np.where(binary_image == 1, 0, 1)

    # Save the binary image as a CSV file
    np.savetxt(f'Environment/maps/{name}.csv', binary_image, delimiter=delim, fmt='%d')

if __name__ == '__main__':

    # name = 'rawfiles/Alamillo95x216grid'
    # delim = ';'
    
    name = 'rawfiles/Alamillo95x216plantilla'
    delim = ' '
    
    # invert_map(name, delim)
    # png_to_csv(name, delim) 
    # csv_to_png(name, delim)
    # csv_to_npy(name, delim)
    # csv_downsize(name, delim, factor=3, output_name=get_output_name(name))
    # csv_shrink(name, delim, init_column=0, final_column=145, init_row=0, final_row=90, output_name=get_output_name(name))
