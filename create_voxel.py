'''
@ coop: Fraunhofer IWU
@ author: Jan Klein
@ date: 25-11-2019

This script can be used to transfer the layerwise hdf5 data into voxelwise hdf5 data
'''

import h5py
import numpy as np
import math
import pandas as pd
from helping_functions import calculate_part_dimensions, get_number_voxel, fill_2D_voxel_area, fill_2D_voxel_intensity

path_voxel_h5 = '' #enter the path for the resulting voxel hdf5 here
path_buildjob_h5 = ''
part_name = ''
voxel_size = 1  #int of x and y dimension of a voxel
num_voxel_layers = 1#int of number of layers per voxel

def create_h5(path_buildjob_h5, part_name, voxel_size, num_voxel_layers):
    #1. Step: calculating the number of needed voxels
    dimension_dict = calculate_part_dimensions(path_buildjob_h5, part_name)
    length_x_part = dimension_dict['lengthX']
    length_y_part = dimension_dict['lengthY']
    number_of_layers_part = dimension_dict['number_of_layers']

    num_voxels = get_number_voxel(length_x_part, length_y_part, number_of_layers_part,voxel_size, num_voxel_layers)
    num_voxels_x = num_voxels[0]
    num_voxels_y = num_voxels[1]
    num_voxels_z = num_voxels[2]
