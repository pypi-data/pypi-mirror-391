# Programa para pasar de una imagen a una matriz de pixeles 0,1 con un umbral y un alto en pixeles
import sys
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt	
import argparse



def img2pixels(img_path, threshold=128, height=100):

	img = Image.open(img_path)
	img = img.convert('L')  # Convert to grayscale
	img = img.resize((int(img.width * height / img.height), height), Image.LANCZOS)
	img = np.array(img)

	# Threshold
	img = (img > threshold).astype(int)

	return img



if __name__ == "__main__":

	argparser = argparse.ArgumentParser(description='Convert image to pixel matrix')
	argparser.add_argument('--path', type=str, help='Path to image')
	argparser.add_argument('--threshold', type=int, default=128, help='Threshold for binarization')
	argparser.add_argument('--height', type=int, default=100, help='Height of the output image')
	argparser.add_argument('--output', type=str, help='Output file')

	args = argparser.parse_args()

	# Example
	pixels = img2pixels(args.path, threshold=args.threshold, height=args.height)


	# To numpy and save to file 

	np.save(args.output + '.npy', pixels)
