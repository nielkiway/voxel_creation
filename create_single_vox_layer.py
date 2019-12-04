'''
@ coop: Fraunhofer IWU
@ author: Jan Klein
@ date: 04-12-2019

The function is used to create voxels
'''
import h5py
import numpy as np
import time
from Definitions import path_voxel_h5, minX, minY, num_voxels_x, num_voxels_y, path_buildjob_h5, num_layers_per_voxel, part_name, mode_df, voxel_size, num_z_list
from helping_functions import get_2D_data_from_h5_filtered, dock_df_to_zero, create_single_voxel_df
import concurrent.futures


def create_single_vox_layer (num_z):
    start_time_1 = time.time()
    for num_slice in range(num_layers_per_voxel*num_z, num_layers_per_voxel*(num_z+1)):
        start_time_2 = time.time()
        #print('num_slice: ' + str(num_slice))
        #start_time = time.time()
        # getting the data of the part_hdf5
        df_not_docked = get_2D_data_from_h5_filtered(path_buildjob_h5, part_name, 'Slice' + str("{:05d}".format(num_slice+1)), mode_df) #"{:05d}" -> 1 becomes 00001 for accessibility in h5 file
        df = dock_df_to_zero(df_not_docked, minX, minY) #docking the values of the dataframe to 0

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
                    voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)].create_group('slice_{}'.format(num_slice-num_z*num_layers_per_voxel)) #-num_z*num_slices_vox wegen
                    voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_layers_per_voxel)].create_dataset('X-Axis',data = np.repeat(np.arange(0,voxel_size,1),voxel_size))
                    voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_layers_per_voxel)].create_dataset('Y-Axis',data = np.tile(np.arange(0,voxel_size,1),voxel_size))
                    voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_layers_per_voxel)].create_dataset('Area', data = df_voxel_final['area'].values.astype(int))
                    voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice-num_z*num_layers_per_voxel)].create_dataset('Intensity', data = df_voxel_final['intensity'].values.astype(int))
            print('filling voxel_{}_{}_{} took {} s'.format(n_vox_x_init,n_vox_y_init, num_z, time.time() - start_time_2))
    print("layer filling took %s seconds ---" % (time.time() - start_time_1))
    return

if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(create_single_vox_layer, num_z_list)
