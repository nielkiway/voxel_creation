'''
@ coop: Fraunhofer IWU
@ author: Jan Klein
@ date: 20-11-2019

These functions are used as helper functions in create_voxel.py to create a 3D-Voxel-structure of the
hdf5 data of a certain part
'''
import h5py
import numpy as np
import math
import pandas as pd


'''
-------------------------------------------------------------------------------
get_2D_data_from_h5:
This function reads the hdf5 data (no Intensity configured here) of a certain
part and a certain Slice and returns a pandas dataframe of the data

inputs:
h5_path = str of path of the hdf5 of the relevant buildjob
part_name = str of the name of the part of interest
Slice_name = str of the slice of interest

outputs:
pandas dataframe of the selected data
'''
def get_2D_data_from_h5(h5_path, part_name, Slice_name):
    with h5py.File(h5_path,'r') as h5:
        X_Axis = h5[part_name][Slice_name]['X_Axis']
        Y_Axis = h5[part_name][Slice_name]['Y_Axis']
        Area = h5[part_name][Slice_name]['Area']

        help_arr = np.column_stack((X_Axis, Y_Axis, Area))
        df = pd.DataFrame(help_arr, columns=['x','y','area'])
        return df



'''
-------------------------------------------------------------------------------
get_attributes_from_hdf_5:
This function returns the attributes of a part

inputs:
h5_path = str of path to hdf5 of buildjob of the part of interest
part_name = str of the name of the part of interest

outputs:
dictionary with all the stored attributes. This dictionary can be used to get
the dimensions of the part by selecting the required key (e.g. dict['maxX'])
'''

def get_attributes_from_hdf_5 (h5_path, part_name):
    attrs_dict = {}
    with h5py.File(h5_path,'r') as h5:
        for item in h5[part_name].attrs.keys():
            attrs_dict[item] = h5[part_name].attrs[item]
        return attrs_dict



'''
-------------------------------------------------------------------------------
calculate_part_dimensions:
function that calculates the dimensions of a part using its attributes

inputs:
h5_path: str of h5 path
part_name: str of the name of the desired part

outputs:
dict with lengthX, lengthY, height and number of layers

'''
def calculate_part_dimensions(h5_path, part_name):
    #here one should additionally check whether all the required keys are in the dictionary
    dict = {}
    attrs_dict = get_attributes_from_hdf_5(h5_path, part_name)
    maxX = attrs_dict.get('maxX')
    maxY = attrs_dict.get('maxY')
    maxZ = attrs_dict.get('maxZ')

    minX = attrs_dict.get('minX')
    minY = attrs_dict.get('minY')
    minZ = attrs_dict.get('minZ')

    layerThickness = attrs_dict.get('layerThickness')
    height = abs(maxZ-minZ)

    dict['lengthX'] = abs(maxX-minX)
    dict['lengthY'] = abs(maxY-minY)
    dict['height'] = abs(maxZ-minZ)

    dict['number_of_layers'] = int(height/layerThickness)

    return dict

'''
-------------------------------------------------------------------------------
get_number_voxel:
This function takes the dimensions of the part of interest and returns the
number of voxels in x and y dimension. If the voxel size doesn't perfectly fit
in the part dimensions the number of voxels is rounded up

### hier muss noch der Link zu den Part Dimensions mit rein, dass max x und länge x zwei paar Stiefel sind

inputs:
length_x_part = float or int of maximum x value of part_name
length_y_part =                         y
voxel_size = int of x and y dimension of voxel
num_voxel_layers_part = int of number of layers of the part
num_voxel_layers = int of number of layers per each voxel

outputs:
tuple of number of x voxels and y voxels
'''

#Berechnung der Anzahl an Voxeln (hier simpler Fall)
def get_number_voxel (length_x_part, length_y_part, number_of_layers_part, voxel_size, num_voxel_layers):
    n_voxels_x = math.ceil(int(length_x_part)/voxel_size)
    n_voxels_y = math.ceil(int(length_y_part)/voxel_size)
    n_voxels_z = math.ceil(int(number_of_layers_part)/num_voxel_layers)
    return n_voxels_x, n_voxels_y, n_voxels_z #tuple is returned


'''
-------------------------------------------------------------------------------
fill_2D_voxel_area:
This function takes a dataframe with x,y, Intensity and area values as input data and
iterates over voxel-grid to fill up each grid

inputs:
voxel_size = int of voxel x and y dimensions
num_voxels_x = int of current number of voxel in x-direction
num_voxels_y =                                   y
df = Dataframe of data of interest
filling_method = Zeros (area data of missing data points is set to zero), further methods to come

output: np array with area values for voxel
'''

def fill_2D_voxel_area (voxel_size, num_voxels_x, num_voxels_y, df, filling_method):
    array_area = np.zeros([voxel_size,voxel_size]) #creating an empty array of dimensions voxel_size*voxel_size
    for i in range(voxel_size*num_voxels_x, voxel_size*(num_voxels_x+1)): #iterating over x
        for j in range(voxel_size*num_voxels_y,voxel_size*(num_voxels_y+1)): #iterating over y

            if df[(df['x'] == i) & (df['y'] == j)].shape[0] == 1: #here subset of the original dataframe is created an filtrered --> shape[0] returns the number of rows of this df subset
                #finding the area value for a certain point in the part-data-dataframe and allocating it to a position in the array
                area_i = df.loc[(df['x'] == i) & (df['y'] == j)]
                array_area[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = area_i['Area']

            elif df[(df['x'] == i) & (df['y'] == j)].shape[0] > 1:
                #if there are more values than just one the maximum value is used for the voxel-datapoint; other methods of dealing with multiple values need to be considered
                array_area[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = df[(df['x'] == i) & (df['y'] == j)]['area'].max()


            elif df[(df['x'] == i) & (df['y'] == j)].shape[0] == 0 and filling_method == 'Zeros':
                array_area[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = 0

            #elif filling_method == 'Mean': #with this method all the missing datapoints are getting filled with the mean of the non-missing datapoints
             #   array_area[i][j] =

    return array_area

'''
-------------------------------------------------------------------------------
fill_2D_voxel_intensity:
This function takes a dataframe with x,y, Intensity and area values as input data and
iterates over voxel-grid to fill up each grid

inputs:
voxel_size = int of voxel x and y dimensions
num_voxels_x = int of current number of voxel in x-direction
num_voxels_y =                                   y
df = Dataframe of data of interest
filling_method = Zeros (intensity data of missing data points is set to zero), further methods to come

output: np array with intensity values for voxel
'''

def fill_2D_voxel_intensity (voxel_size, num_voxels_x, num_voxels_y, df, filling_method):
    array_intensity = np.zeros([voxel_size,voxel_size]) #creating an empty array of dimensions voxel_size*voxel_size
    for i in range(voxel_size*num_voxels_x, voxel_size*(num_voxels_x+1)): #iterating over x
        for j in range(voxel_size*num_voxels_y,voxel_size*(num_voxels_y+1)): #iterating over y

            if df[(df['x'] == i) & (df['y'] == j)].shape[0] == 1: #here subset of the original dataframe is created an filtrered --> shape[0] returns the number of rows of this df subset
                #finding the area value for a certain point in the part-data-dataframe and allocating it to a position in the array
                area_i = df.loc[(df['x'] == i) & (df['y'] == j)]
                array_intensity[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = area_i['intensity']

            elif df[(df['x'] == i) & (df['y'] == j)].shape[0] > 1:
                #if there are more values than just one the maximum value is used for the voxel-datapoint; other methods of dealing with multiple values need to be considered
                array_intensity[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = df[(df['x'] == i) & (df['y'] == j)]['intensity'].max()


            elif df[(df['x'] == i) & (df['y'] == j)].shape[0] == 0 and filling_method == 'intensity':
                array_intensity[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = 0

            #elif filling_method == 'Mean': #with this method all the missing datapoints are getting filled with the mean of the non-missing datapoints
             #   array_area[i][j] =

    return array_intensity
