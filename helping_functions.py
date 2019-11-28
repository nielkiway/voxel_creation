'''
@ coop: Fraunhofer IWU
@ author: Jan Klein
@ date: 20-11-2019

These functions are used as helper functions in create_voxel.py to create a
3D-Voxel-structure of the hdf5 data of a certain part
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
        X_Axis = h5[part_name][Slice_name]['X-Axis']
        Y_Axis = h5[part_name][Slice_name]['Y-Axis']
        Area = h5[part_name][Slice_name]['Area']
        Intensity = h5[part_name][Slice_name]['Intensity']

        help_arr = np.column_stack((X_Axis, Y_Axis, Area, Intensity))
        df = pd.DataFrame(help_arr, columns=['x','y','area','intensity'])
        return df


'''
------------------------------------------------------------------------------
get_2D_data_from_h5_with_dimension_check:
This function reads in the hdf5 data like the function get_2D_data_from_h5
but it also performs a check whether all the dimensions of the value arrays
in the hdf5 file are equal - if that's not the case, the last values of the arrays
which exceed the minimal array length are deleted. This process is repeated till
all the dimensions are equal

inputs:
h5_path = str of path of the hdf5 of the relevant buildjob
part_name = str of the name of the part of interest
Slice_name = str of the slice of interest

outputs:
pandas dataframe of the selected data with checked Dimensions

'''
def get_2D_data_from_h5_with_dimension_check(h5_path, part_name, Slice_name):
    with h5py.File(h5_path,'r') as h5:
        X_Axis = h5[part_name][Slice_name]['X-Axis']
        Y_Axis = h5[part_name][Slice_name]['Y-Axis']
        Area = h5[part_name][Slice_name]['Area']
        Intensity = h5[part_name][Slice_name]['Intensity']

        X_Axis_size = X_Axis.size
        Y_Axis_size = Y_Axis.size
        Area_size = Area.size
        Intensity_size = Intensity.size

        #if dimensions aren't equal the following code block is entered
        if not X_Axis_size == Y_Axis_size == Area_size == Intensity_size:

            #determine the lowest value among the different sizes
            size_arr = np.array([X_Axis_size, Y_Axis_size, Area_size, Intensity_size])
            min_size = size_arr.min()

            if X_Axis_size != min_size:
                diff_size_x = X_Axis_size - min_size #calculating the difference between the actual value and the minimum and substracting it from the array
                X_Axis_new = np.delete(X_Axis, -diff_size_x)
                X_Axis = X_Axis_new
                X_Axis_size = X_Axis.size

            if Y_Axis_size != min_size:
                diff_size_y = Y_Axis_size - min_size
                Y_Axis_new = np.delete(Y_Axis, -diff_size_y)
                Y_Axis = Y_Axis_new
                Y_Axis_size = Y_Axis.size

            if Area_size != min_size:
                diff_size_area = Area_size - min_size
                Area_new = np.delete(Area, -diff_size_area)
                Area = Area_new
                Area_size = Area.size

            if Intensity_size != min_size:
                diff_size_intensity = Intensity_size - min_size
                Intensity_new = np.delete(Intensity, -diff_size_intensity)
                Intensity = Intensity_new
                Intensity_size = Intensity.size


        #by reducing all the dimensions to the minimum equal dimensions are guaranteed
        #there is a risk of deleting more than just one datapoint without noticing -> maybe add an alert after more than 5(?) while iterations
        help_arr = np.column_stack((X_Axis, Y_Axis, Area, Intensity))
        df = pd.DataFrame(help_arr, columns=['x','y','area','intensity'])
        return df

'''
------------------------------------------------------------------------------
dock_df_to_zero:
This function shifts all the x- and y-values in the dataframe, so the smallest
value is equal to 0. Therefore it is checked whether the minX/minY value is greater
or smaller than 0 or equal to 0. The whole dataframe is substracted or added the
minimum value

inputs:
df = DataFrame of interest
minX = Minimum x-value
minY = Minimum y-value

outputs:
df = DataFrame with smallest x- and y-values equal to 0
'''
def dock_df_to_zero(df, minX, minY):
    if minX >= 0 and minY >=0:
        df['x'] = df['x'] - minX
        df['y'] = df['y'] - minY
    elif minX < 0 and minY <0:
        df['x'] = df['x'] + abs(minX)
        df['y'] = df['y'] + abs(minY)
    elif minX >= 0 and minY <0:
        df['x'] = df['x'] - minX
        df['y'] = df['y'] + abs(minY)
    elif minX < 0 and min >= 0:
        df['x'] = df['x'] + abs(minX)
        df['y'] = df['y'] - minY
    return df


'''
-------------------------------------------------------------------------------
get_true_min_maxX:
function that goes through all the slices and finds the minimum and maximal
x-value

input:
h5_path = str of path to the buildjob hdf5
part_name = str of name of the part
max_slice_number = greatest number of slices of the part of interest

output:
tuple with minimal x-value in position [0] and maximal x-value in position [1]
'''
def get_true_min_maxX (h5_path, part_name, max_slice_number):

    minX = []
    maxX = []
    for num_slice in range(max_slice_number):
        with h5py.File(h5_path,'r') as h5:
            X_Axis = h5[part_name]['Slice'+str("{:05d}".format(num_slice+1))]['X-Axis']
            x_axis_array = np.array(X_Axis)
            minX.append(x_axis_array.min())
            maxX.append(x_axis_array.max())
    minX_array = np.asarray(minX)
    maxX_array = np.asarray(maxX)
    return minX_array.min(), maxX_array.max()

'''
-------------------------------------------------------------------------------
get_true_min_maxY:
function that goes through all the slices and finds the minimum and maximal
y-value

input:
h5_path = str of path to the buildjob hdf5
part_name = str of name of the part
max_slice_number = greatest number of slices of the part of interest

output:
tuple with minimal y-value in position [0] and maximal y-value in position [1]
'''
def get_true_min_maxY (h5_path, part_name, max_slice_number):

    minY = []
    maxY = []
    for num_slice in range(max_slice_number):
        with h5py.File(h5_path,'r') as h5:
            Y_Axis = h5[part_name]['Slice'+str("{:05d}".format(num_slice+1))]['Y-Axis']
            y_axis_array = np.array(Y_Axis)
            minY.append(y_axis_array.min())
            maxY.append(y_axis_array.max())
    minY_array = np.asarray(minY)
    maxY_array = np.asarray(maxY)
    return minY_array.min(), maxY_array.max()


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

inputs:and github tutorial
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
    dict['minX'] = minX
    dict['minY'] = minY

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
length_y_part =                         yand github tutorial
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
iterates over voxel-grid to fill up each gridand github tutorial

inputs:
voxel_size = int of voxel x and y dimensions
num_voxels_x = int of current number of voxel in x-direction
num_voxels_y =                                   y
df = Dataframe of data of interest
filling_method = 'Zeros' (area data of missing data points is set to zero), further methods to come
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
