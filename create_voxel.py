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
from helping_functions import calculate_part_dimensions, get_number_voxel, fill_2D_voxel_area, fill_2D_voxel_intensity, get_2D_data_from_h5, dock_df_to_zero

'''
path_voxel_h5 = '' #enter the path for the resulting voxel hdf5 here
path_buildjob_h5 = ''
part_name = ''
voxel_size = 1  #int of x and y dimension of a voxel
num_voxel_layers = 1#int of number of layers per voxel
'''
#Modus: Area+Intensity, Area_only, Intensity_only
def create_voxel_h5(path_buildjob_h5, path_voxel_h5, part_name, voxel_size, num_voxel_layers, mode):
    #1. Step: calculating the number of needed voxels
    dimension_dict = calculate_part_dimensions(path_buildjob_h5, part_name)
    length_x_part = dimension_dict['lengthX']
    length_y_part = dimension_dict['lengthY']
    number_of_layers_part = dimension_dict['number_of_layers']
    minX_part = dimension_dict['minX']
    minY_part = dimension_dict['minY']

    num_voxels = get_number_voxel(length_x_part, length_y_part, number_of_layers_part, voxel_size, num_voxel_layers)
    num_voxels_x = num_voxels[0]
    num_voxels_y = num_voxels[1]
    num_voxels_z = num_voxels[2]

    print(num_voxels)
    #2. Step: create empty hdf-file for voxel
    voxel_hdf = h5py.File(path_voxel_h5, "w")
    voxel_hdf.close()

    #num_slices_vox = neu num_voxel_layers

    for num_z in range(0, num_voxels_z):
        print(num_z)

        for num_slice in range(num_voxel_layers*num_z, num_voxel_layers*(num_z+1)):
            print(num_slice)
            #here it's checked whether the Slice number is in within the hdf5-file. If yes, the data of the slice is loaded. If not, an empty dataframe is created and processed
            #try:
            df_not_docked = get_2D_data_from_h5(path_buildjob_h5, part_name, 'Slice' + str("{:05d}".format(num_slice+1))) #"{:05d}" -> 1 becomes 00001 for accessibility in h5 file
            df = dock_df_to_zero(df_not_docked, minX_part, minY_part)
            '''
            Problem: minX und minY stimmen nicht mit den Werten in den Slices überein
            -> eventuell muss minX und minY nochmal selbst berechnet werden
            '''

            #except: #an empty dataframe is created which is handled in the way set earlier ('Zeros') etc.
            #    columns = ['x', 'y', 'area', 'intensity']
            #    df = pd.DataFrame(columns=columns)

            print(df)
            for n_vox_y_init in range(num_voxels_y): #iterating over number of voxels in y-direction
                for n_vox_x_init in range(num_voxels_x):#iterating over number of voxels in x-direction

                    if mode == 'Area+Intensity':
                        array_area = fill_2D_voxel_area(voxel_size, n_vox_x_init, n_vox_y_init, df,'Zeros')
                        array_intensity = fill_2D_voxel_intensity(voxel_size, n_vox_x_init, n_vox_y_init, df,'Zeros')

                        with h5py.File(path_voxel_h5, "a") as voxel_hdf:
                            #creating a voxel with the numbers of voxels in both direction in its name and filling it with data
                            #if group is already existing don't create a new group
                            if 'voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init, num_z) not in voxel_hdf:
                                voxel_hdf.create_group('voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z))
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)].create_group('slice_{}'.format(num_slice-num_z*num_voxel_layers)) #-num_z*num_slices_vox wegen
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('X-Axis',data = np.repeat(np.arange(0,voxel_size,1),voxel_size))
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Y-Axis',data = np.tile(np.arange(0,voxel_size,1),voxel_size))
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Area', data = array_area.flatten())
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Intensity', data = array_intensity.flatten())


                    elif mode == 'Area_only':
                        array_area = fill_2D_voxel_area(voxel_size, n_vox_x_init, n_vox_y_init, df,'Zeros')
                        #array_intensity = fill_2D_voxel_intensity(voxel_size, n_vox_x_init, n_vox_y_init, df,'Zeros')

                        with h5py.File(path_voxel_h5, "a") as voxel_hdf:
                            #creating a voxel with the numbers of voxels in both direction in its name and filling it with data
                            #if group is already existing don't create a new group
                            if 'voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init, num_z) not in voxel_hdf:
                                voxel_hdf.create_group('voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z))
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)].create_group('slice_{}'.format(num_slice-num_z*num_voxel_layers)) #-num_z*num_slices_vox wegen
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('X-Axis',data = np.repeat(np.arange(0,voxel_size,1),voxel_size))
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Y-Axis',data = np.tile(np.arange(0,voxel_size,1),voxel_size))
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Area', data = array_area.flatten())
                            #voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Intensity', data = array_intensity.flatten())

                    elif mode == 'Intensity_only':
                        #array_area = fill_2D_voxel_area(voxel_size, n_vox_x_init, n_vox_y_init, df,'Zeros')
                        array_intensity = fill_2D_voxel_intensity(voxel_size, n_vox_x_init, n_vox_y_init, df,'Zeros')

                        with h5py.File(path_voxel_h5, "a") as voxel_hdf:
                            #creating a voxel with the numbers of voxels in both direction in its name and filling it with data
                            #if group is already existing don't create a new group
                            if 'voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init, num_z) not in voxel_hdf:
                                voxel_hdf.create_group('voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z))
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)].create_group('slice_{}'.format(num_slice-num_z*num_voxel_layers)) #-num_z*num_slices_vox wegen
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('X-Axis',data = np.repeat(np.arange(0,voxel_size,1),voxel_size))
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Y-Axis',data = np.tile(np.arange(0,voxel_size,1),voxel_size))
                            #voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Area', data = array_area.flatten())
                            voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_voxel_layers)].create_dataset('Intensity', data = array_intensity.flatten())

                    print('creating voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z))
        # y-Achse entspricht horizontal, x-Achse entspricht vertikal





if __name__ == '__main__':
    create_voxel_h5('/home/jan/Documents/CodeTDMStoHDF/Ausgangsdaten/examplerRun.h5', '/home/jan/Documents/Voxel_Erstellung/voxels_test_big.hdf5', '0_00003_Canti3_cls', 200, 10, 'Area_only')
