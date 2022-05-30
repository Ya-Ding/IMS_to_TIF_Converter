import sys
import numpy as np
from tiffwrite import tiffwrite as TiffWriter
import h5py
import os
import skimage
from skimage.util import img_as_uint, img_as_float
import glob
import skimage.io as io
from PIL import Image
import tifffile as tiff

# info wrong
def get_h5_file_info(h5_dataset):
    # Get a list of all of the resolution options
    resolution_levels = list(h5_dataset)
    resolution_levels.sort(key = lambda x: int(x.split(' ')[-1]))

    # Get a list of the available time points
    time_points = list(h5_dataset[resolution_levels[0]])
    time_points.sort(key = lambda x: int(x.split(' ')[-1]))
    n_time_points = len(time_points)

    # Get a list of the channels
    channels = list(h5_dataset[resolution_levels[0]][time_points[0]])
    channels.sort(key = lambda x: int(x.split(' ')[-1]))
    n_channels = len(channels)

    # Get the number of z levels
    n_z_levels = h5_dataset[resolution_levels[0]][time_points[0]][channels[0]]['Data'].shape[0]
    z_levels = list(range(n_z_levels))

    # Get the plane dimensions
    n_rows, n_cols = h5_dataset[resolution_levels[0]][time_points[0]][channels[0]][
                   'Data'].shape[1:]

    return resolution_levels, time_points, n_time_points, channels, n_channels, n_z_levels, z_levels, n_rows, n_cols

def convert_to_tif(f_name, select_slice):
    read_file = h5py.File(f_name)
    base_data = read_file['DataSet']

    # THIS ASSUMES THAT YOU HAVE A MULTICOLOR Z STACK IN TIME
    resolution_levels, \
    time_points, n_time_points, \
    channels, n_channels, \
    n_z_levels, z_levels, \
    n_rows, n_cols = get_h5_file_info(base_data)
    # print(resolution_levels)
    # print(time_points)
    # print(n_time_points)
    print(description.tobytes().decode('utf-8'))
    print('channels: %s'%channels)
    #print(n_channels)
    # print(n_z_levels)
    # print(z_levels)
    # print(n_rows)
    # print(n_cols)

    # image
    raw_data = base_data[resolution_levels[0]][time_points[0]][channels[0]]['Data']
    channel = base_data[resolution_levels[0]][time_points[0]][channels[0]]
    imageSizeX = int(channel.attrs['ImageSizeX'].tobytes())
    imageSizeY = int(channel.attrs['ImageSizeY'].tobytes())
    imageSizeZ = int(channel.attrs['ImageSizeZ'].tobytes())
    print(raw_data)
    print('total slice: ',imageSizeZ)
    print(f'image size: ({imageSizeX},{imageSizeY})')
    print('channel:', channel)


    filename = f_name.split('\\')[-1].split('.')[0]
    foldername = f_name.split('\\')[-2]
    os.makedirs(f'outputs\\{foldername}', exist_ok=True)
    if select_slice == ['*']:
        for z_axis in range(imageSizeZ):
            image = raw_data[z_axis, :imageSizeY, :imageSizeX]
            tiff.imsave(f'outputs\\{foldername}\\{filename}_{str(z_axis).zfill(3)}.tif',image)
            # tiff.imsave(foldername + '/' + filename + '_' + str(z_axis).zfill(3) + '.tif',image)
            # tiff.imsave(f'output/{str(z_axis).zfill(3)}.tif',image)
    else:
        for z_axis in select_slice:
            image = raw_data[z_axis, :imageSizeY, :imageSizeX]
            tiff.imsave(f'outputs\\{foldername}\\{filename}_ch0_{str(z_axis).zfill(3)}.tif',image)

def driver(passed_files, select_slice):
    converter_func = convert_to_tif
    for f_name in passed_files:
        print('')
        print('Processing File: %s'%f_name)
        # progress bar and time
        scale = 100
        print("Start Processing".center(scale // 2, "-"))
        with alive_bar(100, title="running", bar="bubbles", spinner="fishes") as bar:
            for item in range(100):
                # wait a second
                time.sleep(.1)
                # update progress bar, progress +1
                bar()
            converter_func(f_name, select_slice)
            print("End Processing".center(scale // 2, "-"))


def main():
    select_slice = [20, 70]  #choice select =[150, 170, 180] #whole slices =['*']
    print('select_slice %s'%select_slice)
    os.makedirs('outputs\\', exist_ok=True)
    # Check for tif files in the directory
    tif_files = glob.glob('*.tif')
    if len(tif_files) > 0:
        raise SystemExit('Conversion has already been run in this directory. Exiting.')
    # Get all of the ims files
    folder= '4_3'
    ims_files = glob.glob(f'data\\{folder}\\*.ims')
    # Get the current working directory
    cwd = os.getcwd() + '\\'
    #print(cwd)
    #print(ims_files)
    # Prepend the cwd to all of the files
    ims_files = [cwd + f_name for f_name in ims_files]
    # Pass the filenames and the downsample factor to the driver
    driver(ims_files, select_slice)


if __name__ == '__main__':
    main()


# CUDA_VISBIBLE_DEVICES=0 python ims_to_tif.py