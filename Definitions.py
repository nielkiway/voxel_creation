'''
@ coop: Fraunhofer IWU
@ author: Jan Klein
@ date: 04-12-2019
'''
'''
--------------------------------------------------------------------------------
Input data
'''
import h5py
import os
from helping_functions import get_true_min_maxX
from helping_functions import get_true_min_maxY
from helping_functions import get_number_voxel


path_buildjob_h5 = '/home/jan/Documents/CodeTDMStoHDF/Ausgangsdaten/examplerRun.h5'
path_voxel_h5_folder = '/home/jan/Documents/Voxel_Erstellung/HDFs/0_00003_Canti3_cls'
#name_voxel_h5_file = 'asdasd_2.hdf5'
part_name = '0_00003_Canti3_cls'
mode_df = 'mean' #way how to deal with data points which occur multiple times
voxel_size = 100
num_layers_per_voxel = 20
max_slice_number_part = 142 # doesn't need to be manually added
#a funtion needs to be built in which checks whether a Slice data is there or not (for topmost voxel)
'''
-------------------------------------------------------------------------------
Basic operations and calculations
'''
os.mkdir(path_voxel_h5_folder)

#path_voxel_h5 = path_voxel_h5_folder+name_voxel_h5_file

minX = int(get_true_min_maxX(path_buildjob_h5, part_name, max_slice_number_part)[0])
maxX = int(get_true_min_maxX(path_buildjob_h5, part_name, max_slice_number_part)[1])
minY = int(get_true_min_maxY(path_buildjob_h5, part_name, max_slice_number_part)[0])
maxY = int(get_true_min_maxY(path_buildjob_h5, part_name, max_slice_number_part)[1])

length_x_part = abs(maxX-minX)
length_y_part = abs(maxY-minY)

num_voxels = get_number_voxel(length_x_part, length_y_part, max_slice_number_part, voxel_size, num_layers_per_voxel) #number_of_layers_part was changed to max_slice_number_part
num_voxels_x = int(num_voxels[0])
num_voxels_y = int(num_voxels[1])
num_voxels_z = 3#int(num_voxels[2])

num_z_list = [i for i in range(num_voxels_z)]
