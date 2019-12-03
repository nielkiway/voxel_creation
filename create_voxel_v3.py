'''
@ coop: Fraunhofer IWU
@ author: Jan Klein
@ date: 20-11-2019

The function is used to create voxels
'''

import h5py
import numpy as np
import math
import pandas as pd
import time

from helping_functions import get_2D_data_from_h5_filtered
from helping_functions import dock_df_to_zero
from helping_functions import get_true_min_maxX
from helping_functions import get_true_min_maxY
from helping_functions import get_number_voxel
from helping_functions import create_single_voxel_df


'''
path_voxel_h5: enter the path for the resulting voxel hdf5 here
path_buildjob_h5: str of path of the hdf5 of the part
part_name: str of name of part
voxel_size:  int of x and y dimension of a voxel
num_voxel_layers: int of number of layers per voxel
max_slice_number_part: number of the highest slice of the part <- wird noch automatisiert
mode_df: 'mean' or 'max' - if there are more area/intensity values for a certain x,y-position either the mean of the values or the max of the values is stored in the dataframe
'''

def create_voxel_h5 (path_buildjob_h5, path_voxel_h5, part_name, max_slice_number_part, voxel_size, num_voxel_layers, mode_df):
    #1.Step: getting the the dimensions of the part

    minX = int(get_true_min_maxX(path_buildjob_h5, part_name, max_slice_number_part)[0])
    maxX = int(get_true_min_maxX(path_buildjob_h5, part_name, max_slice_number_part)[1])
    minY = int(get_true_min_maxY(path_buildjob_h5, part_name, max_slice_number_part)[0])
    maxY = int(get_true_min_maxY(path_buildjob_h5, part_name, max_slice_number_part)[1])

    minX_part = minX
    minY_part = minY

    length_x_part = abs(maxX-minX)
    length_y_part = abs(maxY-minY)

    print('length_x_part: ' + str(length_x_part))
    print('length_y_part: ' + str(length_y_part))

    num_voxels = get_number_voxel(length_x_part, length_y_part, max_slice_number_part, voxel_size, num_voxel_layers) #number_of_layers_part was changed to max_slice_number_part
    num_voxels_x = int(num_voxels[0])
    num_voxels_y = int(num_voxels[1])
    num_voxels_z = int(num_voxels[2])

    print('num_voxels_x: ' + str(num_voxels_x))
    print('num_voxels_y: ' + str(num_voxels_y))
    print('num_voxels_z: ' + str(num_voxels_z))

    #2.Step: create empty hdf-file for voxel
    voxel_hdf = h5py.File(path_voxel_h5, "w")
    voxel_hdf.close()

    #3.Step: filling the hdf-file

    for num_z in range(0, num_voxels_z):
        #print('num_z: ' + str(num_z))

        for num_slice in range(num_voxel_layers*num_z, num_voxel_layers*(num_z+1)):
            print('num_slice: ' + str(num_slice))
            start_time = time.time()

            # getting the data of the part_hdf5
            df_not_docked = get_2D_data_from_h5_filtered(path_buildjob_h5, part_name, 'Slice' + str("{:05d}".format(num_slice+1)), mode_df) #"{:05d}" -> 1 becomes 00001 for accessibility in h5 file
            df = dock_df_to_zero(df_not_docked, minX_part, minY_part) #docking the values of the dataframe to 0

            for n_vox_y_init in range(num_voxels_y): #iterating over number of voxels in y-direction
                #print('n_vox_y_init: ' + str(n_vox_y_init))
                for n_vox_x_init in range(num_voxels_x):#iterating over number of voxels in x-direction
                    #print('n_vox_x_init: '+ str(n_vox_x_init))
                    df_voxel_final = create_single_voxel_df(n_vox_x_init, n_vox_y_init, voxel_size, df)

                    with h5py.File(path_voxel_h5, "a") as voxel_hdf:
                        #creating a voxel with the numbers of voxels in both direction in its name and filling it with data
                        #if group is already existing don't create a new group
                        if 'voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init, num_z) not in voxel_hdf:
                            voxel_hdf.create_group('voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z))
                        voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)].create_group('slice_{}'.format(num_slice-num_z*num_voxel_layers)) #-num_z*num_slices_vox wegen
                        voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('X-Axis',data = np.repeat(np.arange(0,voxel_size,1),voxel_size))
                        voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Y-Axis',data = np.tile(np.arange(0,voxel_size,1),voxel_size))
                        voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Area', data = df_voxel_final['area'].values.astype(int))
                        voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Intensity', data = df_voxel_final['intensity'].values.astype(int))
                    print('filling voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init, num_z))
            print("slice filling took %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
    create_voxel_h5('/home/jan/Documents/CodeTDMStoHDF/Ausgangsdaten/examplerRun.h5', '/home/jan/Documents/Voxel_Erstellung/voxels_test_big_v3.hdf5', '0_00003_Canti3_cls', 142, 100, 10, 'mean')
