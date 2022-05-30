import os
import glob
import sys
import h5py
import numpy as np
import tifffile as tiff
from tiffwrite import tiffwrite as TiffWriter
import skimage
import skimage.io as io
from skimage.util import img_as_uint, img_as_float
import time
from alive_progress import alive_bar


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
    n_rows, n_cols = h5_dataset[resolution_levels[0]][time_points[0]][channels[0]]['Data'].shape[1:]

    return resolution_levels, time_points, n_time_points, channels, n_channels, n_z_levels, z_levels, n_rows, n_cols


def convert_to_tif(f_name, select_channel, select_slice):
    read_file = h5py.File(f_name)
    base_data = read_file['DataSet']

    # This assumes that you have a multicolor Z stack in time
    resolution_levels, \
    time_points, n_time_points, \
    channels, n_channels, \
    n_z_levels, z_levels, \
    n_rows, n_cols = get_h5_file_info(base_data)
    print('channels: %s' %channels)

    # read and get images
    if len(select_channel) == 0:
        for ch_number in range(len(channels)):
            raw_data = base_data[resolution_levels[0]][time_points[0]][channels[ch_number]]['Data']
            channel = base_data[resolution_levels[0]][time_points[0]][channels[ch_number]]

            imageSizeX = int(channel.attrs['ImageSizeX'].tobytes())
            imageSizeY = int(channel.attrs['ImageSizeY'].tobytes())
            imageSizeZ = int(channel.attrs['ImageSizeZ'].tobytes())
            print('channel:', channel)
            print('total slice: ', imageSizeZ)
            print(f'image size: ({imageSizeY},{imageSizeX})')

            filename = f_name.split('/')[-1].split('.')[0]
            foldername = f_name.split('/')[-2]
            os.makedirs(f'outputs/{foldername}', exist_ok=True)
            if len(select_slice) == 0:
                for z_axis in range(imageSizeZ):
                    image = raw_data[z_axis, :imageSizeY, :imageSizeX]
                    tiff.imsave(f'outputs/{foldername}/{filename}_ch{ch_number}_s{str(z_axis).zfill(3)}.tif', image)
            else:
                for z_axis in select_slice:
                    image = raw_data[z_axis, :imageSizeY, :imageSizeX]
                    tiff.imsave(f'outputs/{foldername}/{filename}_ch{ch_number}_s{str(z_axis).zfill(3)}.tif', image)
    else:
        for ch_number in select_channel:
            raw_data = base_data[resolution_levels[0]][time_points[0]][channels[ch_number]]['Data']
            channel = base_data[resolution_levels[0]][time_points[0]][channels[ch_number]]

            imageSizeX = int(channel.attrs['ImageSizeX'].tobytes())
            imageSizeY = int(channel.attrs['ImageSizeY'].tobytes())
            imageSizeZ = int(channel.attrs['ImageSizeZ'].tobytes())
            print('channel:', channel)
            print('total slice: ', imageSizeZ)
            print(f'image size: ({imageSizeY},{imageSizeX})')

            filename = f_name.split('/')[-1].split('.')[0]
            foldername = f_name.split('/')[-2]
            os.makedirs(f'outputs/{foldername}', exist_ok=True)
            if len(select_slice) == 0:
                for z_axis in range(imageSizeZ):
                    image = raw_data[z_axis, :imageSizeY, :imageSizeX]
                    tiff.imsave(f'outputs/{foldername}/{filename}_ch{ch_number}_s{str(z_axis).zfill(3)}.tif', image)
            else:
                for z_axis in select_slice:
                    image = raw_data[z_axis, :imageSizeY, :imageSizeX]
                    tiff.imsave(f'outputs/{foldername}/{filename}_ch{ch_number}_s{str(z_axis).zfill(3)}.tif', image)


def driver(passed_files, select_channel, select_slice):
    converter_func = convert_to_tif
    for f_name in passed_files:
        print('')
        print('Processing File: %s'%f_name)
        print('selected channel & slices:', (select_channel), select_slice)
        # progress bar and time
        scale = 100
        print("Start Processing".center(scale // 2, "-"))
        with alive_bar(100, title="running", bar="smooth", spinner="fishes") as bar:
            for item in range(100):
                # wait a second
                time.sleep(.1)
                # update progress bar, progress +1
                bar()
            converter_func(f_name, select_channel, select_slice)
            print("End Processing".center(scale // 2, "-"))


def main():
    select_channel = [0,1]
    select_slice = [50,70]  ##choice select[150, 170 180] ##whole slices =['*']
    os.makedirs('outputs/', exist_ok=True)
    # Check for tif files in the directory
    tif_files = glob.glob('*.tif')
    if len(tif_files) > 0:
        raise SystemExit('Exiting! Conversion has already been run in this directory.')
    # Get all of the ims files
    folder= '*'
    ims_files = glob.glob(f'data/{folder}/*.ims')
    # Get the current working directory
    cwd = os.getcwd() + '/'
    # Prepend the cwd to all of the files
    ims_files = [cwd + f_name for f_name in ims_files]
    # Pass the read file and condition to the driver
    driver(ims_files, select_channel, select_slice)




if __name__ == '__main__':
    main()

# CUDA_VISBIBLE_DEVICES=0 python ims_to_tif_myself.py