'''
@ coop: Fraunhofer IWU
@ author: Jan Klein
@ date: 11-12-2019

The function is used to delete voxels that are completely empty
'''

import h5py
import numpy as np
import os


def delete_empty_voxels(voxel_folder, num_layers_per_voxel):
    h5_list = os.listdir(voxel_folder)

    for h5_file in h5_list:
        with h5py.File(voxel_folder + '/' + h5_file,'a') as h5:
            key_list = h5.keys()
            for key in key_list:
                size_slice_cnt = 0
                for num_slice in range(num_layers_per_voxel):
                    size_slice = h5[key]['slice_{}'.format(num_slice)]['Area'].size #could be any other data column instead of 'Area' as well
                    size_slice_cnt += size_slice
                if size_slice_cnt == 0:
                    del h5[key]








if __name__ == '__main__':
    delete_empty_voxels('/home/jan/Documents/Trainingsdaten/Voxel', 10)
