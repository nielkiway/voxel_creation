'''
@ coop: Fraunhofer IWU
@ author: Jan Klein
@ date: 11-12-2019

The function is used to delete voxels that are completely empty
'''

import h5py
import numpy as np


def delete_empty_voxels(voxel_layer_path, num_layers_per_voxel):

    with h5py.File('/home/jan/Documents/Voxel_Erstellung/HDFs/0_00003_Canti3_cls/Voxel_layer:_5.hdf5','a') as h5:
        key_list = h5.keys()

        for key in key_list:
            size_slice_cnt = 0
            for num_slice in range(num_layers_per_voxel):
                size_slice = h5[key]['slice_{}'.format(num_slice)]['Area'].size #could be any other data column instead of 'Area' as well
                size_slice_cnt += size_slice
            if size_slice_cnt == 0:
                del h5[key] 
