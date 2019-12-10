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
import time

'''
get_2D_data_from_h5_filtered
'''
def get_2D_data_from_h5_filtered(h5_path, part_name, Slice_name, mode):
    #Step 1: getting the data from the h5
    start_time = time.time()
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
        df_raw = pd.DataFrame(help_arr, columns=['x','y','area','intensity'])

    #Step 2: change floats to ints and remove duplicates
    df_int = df_raw.astype(int).drop_duplicates()

    #remove all rows with 0 for area and intensity
    df_int = df_int.loc[(df_int['area'] != 0) & (df_int['intensity'] != 0)]


    #Step 3: Get a df with all the rows where a certain x,y combination occurs multiple times
    df_multi_xy = df_int[df_int.duplicated(['x','y'], keep = False)].reset_index()

    #Step 4: get a new df out of df_multi_xy with x,y and mean/max of area and intensity for all x,y occurences
    df_compact = pd.DataFrame(columns=['x','y','area','intensity']) #initialize df_compact

    print("till iterating from {} {} seconds ---".format (Slice_name,time.time() - start_time))
    for ind in range (df_multi_xy.shape[0]):
        if mode == 'mean':
            area_mean = df_multi_xy.loc[(df_multi_xy['x']== df_multi_xy.iloc[ind]['x']) & (df_multi_xy['y'] == df_multi_xy.iloc[ind]['y'])]['area'].mean().astype(int)
            intensity_mean = df_multi_xy.loc[(df_multi_xy['x']== df_multi_xy.iloc[ind]['x']) & (df_multi_xy['y'] == df_multi_xy.iloc[ind]['y'])]['intensity'].mean().astype(int)
            df_compact = df_compact.append({'x': df_multi_xy.iloc[ind]['x'], 'y':df_multi_xy.iloc[ind]['y'], 'area':area_mean , 'intensity':intensity_mean}, ignore_index=True)
        if mode == 'max':
            area_max = df_multi_xy.loc[(df_multi_xy['x']== df_multi_xy.iloc[ind]['x']) & (df_multi_xy['y'] == df_multi_xy.iloc[ind]['y'])]['area'].max().astype(int)
            intensity_max = df_multi_xy.loc[(df_multi_xy['x']== df_multi_xy.iloc[ind]['x']) & (df_multi_xy['y'] == df_multi_xy.iloc[ind]['y'])]['intensity'].max().astype(int)
            df_compact = df_compact.append({'x': df_multi_xy.iloc[ind]['x'], 'y':df_multi_xy.iloc[ind]['y'], 'area':area_max , 'intensity':intensity_max}, ignore_index=True)
    df_compact = df_compact.drop_duplicates()

    #Step 5: remove df_multi_xy from df_int and append df_compact
    df_multi_xy_removed = df_int.drop(df_int[df_int.duplicated(['x','y'], keep = False)].index)

    df_final = df_multi_xy_removed.append(df_compact)
    print("df creation for {} took {} seconds ---".format (Slice_name,time.time() - start_time))
    return (df_final)


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
<<<<<<< HEAD

=======
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
>>>>>>> d1c7d5505b6478892656ed192077e5d2f820ea7d
output: np array with area values for voxel
'''

def fill_2D_voxel_area (voxel_size, num_voxels_x, num_voxels_y, df, filling_method):
    array_area = np.zeros([voxel_size,voxel_size]) #creating an empty array of dimensions voxel_size*voxel_size
    for i in range(voxel_size*num_voxels_x, voxel_size*(num_voxels_x+1)): #iterating over x
        for j in range(voxel_size*num_voxels_y,voxel_size*(num_voxels_y+1)): #iterating over y

            print('i: '+str(i))
            print('j: '+str(j))

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


            elif df[(df['x'] == i) & (df['y'] == j)].shape[0] == 0 and filling_method == 'Zeros':
                array_intensity[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = 0

            #elif filling_method == 'Mean': #with this method all the missing datapoints are getting filled with the mean of the non-missing datapoints
             #   array_area[i][j] =

    return array_intensity

'''
-------------------------------------------------------------------------------
fill_2D_voxel_area_v2:
Second version of fill_2D_voxel_area

inputs:
voxel_size = int of voxel x and y dimensions
num_voxels_x = int of current number of voxel in x-direction
num_voxels_y =                                   y
df = Dataframe of data of interest
filling_method = 'Zeros' (area data of missing data points is set to zero), further methods to come

output: np array with area values for voxel
'''

def fill_2D_voxel_area_v2 (voxel_size, num_voxels_x, num_voxels_y, df):
    array_area = np.zeros([voxel_size,voxel_size]) #creating an empty array of dimensions voxel_size*voxel_size
    for i in range(voxel_size*num_voxels_x, voxel_size*(num_voxels_x+1)): #iterating over x
        for j in range(voxel_size*num_voxels_y,voxel_size*(num_voxels_y+1)): #iterating over y

            if ((df['x'] == i) & (df['y'] == j)).any(): #here subset of the original dataframe is created an filtrered --> shape[0] returns the number of rows of this df subset
                #finding the area value for a certain point in the part-data-dataframe and allocating it to a position in the array
                area_i = df.loc[(df['x'] == i) & (df['y'] == j)]
                array_area[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = area_i['area']

            else:
                array_area[i-num_voxels_x*voxel_size][j-num_voxels_y*voxel_size] = 0


    return array_area

'''
----------------------------------------------------------------------------
create_voxel_df
function that creates a dataframe filled with 0s for every voxel and adds
all the values for area and intensity that are located inside the voxel

inputs:
current_n_vox_x: int of current voxel number in x-dimension
current_n_vox_y: int of current voxel number in y-dimension
voxel_size: int of voxel dimension
df: docked and filtered dataframe with values for area and intensity for x,y


output:
df of each voxel with added values for area and intensity if they occur within
the voxel
'''

def create_single_voxel_df (current_n_vox_x, current_n_vox_y, voxel_size, df):
    x_min_voxel = current_n_vox_x * voxel_size
    x_max_voxel = (current_n_vox_x + 1)*voxel_size
    y_min_voxel = current_n_vox_y * voxel_size
    y_max_voxel = (current_n_vox_y + 1)*voxel_size

    x_axis_voxel_df =  np.repeat(np.arange(x_min_voxel,x_max_voxel,1),voxel_size)
    y_axis_voxel_df =  np.tile(np.arange(y_min_voxel,y_max_voxel,1),voxel_size)
    Zero_array = np.zeros(voxel_size*voxel_size, dtype=int)

    help_arr = np.column_stack((x_axis_voxel_df, y_axis_voxel_df, Zero_array, Zero_array))
    df_voxel = pd.DataFrame(help_arr, columns=['x','y','area','intensity'])


    if df[(df['x'] > x_min_voxel ) & (df['x'] < x_max_voxel ) & (df['y'] > y_min_voxel) & (df['y'] < y_max_voxel)].shape[0] != 0:
        df_voxel_added = df_voxel.append(df[(df['x'] > x_min_voxel ) & (df['x'] < x_max_voxel ) & (df['y'] > y_min_voxel) & (df['y'] < y_max_voxel)])
        df_voxel_wo_dupl = df_voxel_added.drop_duplicates(['x','y'], keep = 'last')
        df_voxel_final = df_voxel_wo_dupl.sort_values(by=['x','y'])

    else:
        df_voxel_final = df_voxel

    return df_voxel_final


'''
-------------------------------------------------------------------------------
fill_voxel_per_slice
function that fills
'''
#for num_slice in range(num_voxel_layers*num_z, num_voxel_layers*(num_z+1)):
#    print('num_slice: ' + str(num_slice))
#    start_time = time.time()
def fill_voxel_per_slice(num_slice):
    num_voxels_x = 20
    num_voxels_y = 20
    voxel_size = 100
    num_z = 1
    path_buildjob_h5 = '/home/jan/Documents/CodeTDMStoHDF/Ausgangsdaten/examplerRun.h5'
    part_name = '0_00003_Canti3_cls'
    minX_part = minX
    minY_part = minY

    # getting the data of the part_hdf5
    df_not_docked = get_2D_data_from_h5_filtered(path_buildjob_h5, part_name, 'Slice' + str("{:05d}".format(num_slice+1)), 'mean') #"{:05d}" -> 1 becomes 00001 for accessibility in h5 file
    df = dock_df_to_zero(df_not_docked, minX_part, minY_part) #docking the values of the dataframe to 0
    for n_vox_y_init in range(num_voxels_y): #iterating over number of voxels in y-direction
        for n_vox_x_init in range(num_voxels_x):#iterating over number of voxels in x-direction
            #print('n_vox_x_init: '+ str(n_vox_x_init))
            start_time = time.time()
            #set the initial df to a dataframe with the real x and y values - append the dataframe with the values
            #for the particular reach and remove duplicates based on x and y
            df_voxel_final = create_voxel_df(n_vox_x_init, n_vox_y_init, voxel_size, df)

            #print(df_voxel_final)
            with h5py.File('/home/jan/Documents/Voxel_Erstellung/HDFs/voxel_new_filling_method_multiprocessing.hdf5', "a") as voxel_hdf:
                #creating a voxel with the numbers of voxels in both direction in its name and filling it with data
                #if group is already existing don't create a new group
                if 'voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init, num_z) not in voxel_hdf:
                    voxel_hdf.create_group('voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z))
                voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)].create_group('slice_{}'.format(num_slice))
                voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice)].create_dataset('X-Axis',data = np.repeat(np.arange(0,voxel_size,1),voxel_size))
                voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice)].create_dataset('Y-Axis',data = np.tile(np.arange(0,voxel_size,1),voxel_size))
                voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice)].create_dataset('Area', data = df_voxel_final['area'].values.astype(int))
                voxel_hdf['voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init,num_z)]['slice_{}'.format(num_slice)].create_dataset('Intensity', data = df_voxel_final['intensity'].values.astype(int))

            #print('filling voxel_{}_{}_{}'.format(n_vox_x_init,n_vox_y_init, num_z))
    #print("voxel filling took %s seconds ---" % (time.time() - start_time))
    return

'''
--------------------------------------------------------------------------------

'''
def get_2D_data_from_h5_filtered_np(h5_path, part_name, Slice_name):
    #opening h5 and getting the data
    start_time = time.time()

    with h5py.File(h5_path,'r') as h5:
        #check whether slice exists -> if not: empty array returned
        if Slice_name in h5[part_name]:
            Y_Axis = np.array(h5[part_name][Slice_name]['Y-Axis'][:]).astype(int)
            Area = np.array(h5[part_name][Slice_name]['Area'][:]).astype(int)
            Intensity = np.array(h5[part_name][Slice_name]['Intensity'][:]).astype(int)
            X_Axis = np.array(h5[part_name][Slice_name]['X-Axis'][:]).astype(int)

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
            print(str(X_Axis_size)+ ' datapoints found')
            combos = np.stack((X_Axis, Y_Axis, Area, Intensity), axis=-1)

            #filtering out the datapoints where area and intensity are =0
            area_zeros = np.where(combos[:,2]== 0)
            intensity_zeros = np.where(combos[:,3]==0)
            zero_area_intensity_indices = np.intersect1d(area_zeros, intensity_zeros) #array of indices where area AND intensity are = 0

            #deleting all the datapoints where area AND intensity are = 0
            combos_wo_only_zeros = np.delete(combos, zero_area_intensity_indices, axis=0)
            print(str(combos_wo_only_zeros.shape[0]) + ' datapoints where area != 0 AND intensity != 0')

            combos_wo_only_zeros_unique, unique_indices = np.unique(combos_wo_only_zeros[:,[0,1]],axis=0, return_index = True)
            combos_unique = combos_wo_only_zeros[unique_indices]
            print(str(combos_unique.shape[0]) + ' unique datapoints where area != 0 AND intensity != 0')

            Index_range = np.arange(combos_wo_only_zeros.shape[0])
            indices_of_interest = np.setdiff1d(Index_range, unique_indices) #all the indices belonging to non unique x,y-combinations

            combo_processed_array = np.empty([0,4],dtype= int)
            start_time = time.time()
            combos_wo_only_zeros_copy = np.copy(combos_wo_only_zeros)
            index_counter = 0
            shape_counter = 0
            indices_list = []

            print("vor iterieren %s seconds ---" % (time.time() - start_time))
            for index in indices_of_interest:
                xy_combo = combos_wo_only_zeros[:,[0,1]][index]
                if np.where((combo_processed_array[:,0] == xy_combo[0])*(combo_processed_array[:,1] == xy_combo[1]))[0].size == 0:
                    index_counter += 1
                    xy_combo = combos_wo_only_zeros[:,[0,1]][index]
                    indices_relevant = np.where((combos_wo_only_zeros[:,0] == xy_combo[0])*(combos_wo_only_zeros[:,1] == xy_combo[1]))[0]
                    max_area_of_combo = np.amax(combos_wo_only_zeros[:,2][indices_relevant])
                    max_intensity_of_combo = np.amax(combos_wo_only_zeros[:,3][indices_relevant])

                    max_combos = np.stack((xy_combo[0], xy_combo[1], max_area_of_combo, max_intensity_of_combo), axis=-1)

                    combos_wo_only_zeros_copy = np.vstack((combos_wo_only_zeros_copy, max_combos))
                    shape_counter += indices_relevant.shape[0]
                    indices_list.append(list(indices_relevant))

                    combo_processed_array =  np.vstack((combo_processed_array, max_combos))

            indices_relevant = np.hstack(indices_list)
            combos_wo_only_zeros_copy = np.delete(combos_wo_only_zeros_copy, indices_relevant, axis = 0)
        else:
            combos_wo_only_zeros_copy = np.empty([0,4],dtype= int)
            print('{} is not existing -> empty array created'.format(Slice_name))

        #df = pd.DataFrame(combos_wo_only_zeros_copy, columns=['x','y','area','intensity'])
        print("array creation took %s seconds ---" % (time.time() - start_time))
        return(combos_wo_only_zeros_copy)

'''
-------------------------------------------------------------------------------

'''
def dock_array_to_zero(array, minX, minY):
    if minX >= 0 and minY >=0:
        array[:,0] = array[:,0] - minX
        array[:,1] = array[:,1] - minY
    elif minX < 0 and minY <0:
        array[:,0] = array[:,0] + abs(minX)
        array[:,1] = array[:,1] + abs(minY)
    elif minX >= 0 and minY <0:
        array[:,0] = array[:,0] - minX
        array[:,1] = array[:,1] + abs(minY)
    elif minX < 0 and min >= 0:
        array[:,0] = array[:,0] + abs(minX)
        array[:,1] = array[:,1] - minY
    return array

'''
-------------------------------------------------------------------------------
'''
def create_single_voxel_array (current_n_vox_x, current_n_vox_y, voxel_size, array):
    x_min_voxel = current_n_vox_x * voxel_size
    x_max_voxel = (current_n_vox_x + 1)*voxel_size
    y_min_voxel = current_n_vox_y * voxel_size
    y_max_voxel = (current_n_vox_y + 1)*voxel_size

    x_axis_voxel =  np.repeat(np.arange(x_min_voxel,x_max_voxel,1),voxel_size)
    y_axis_voxel =  np.tile(np.arange(y_min_voxel,y_max_voxel,1),voxel_size)
    Zero_array = np.zeros(voxel_size*voxel_size, dtype=int)

    voxel_array = np.stack((x_axis_voxel, y_axis_voxel, Zero_array, Zero_array), axis=-1)

    #check if datapoints in array are in the region of the voxel
    indices_relevant = np.where((array[:,0] >= x_min_voxel)*(array[:,0] < x_max_voxel)*(array[:,1] >= y_min_voxel)*(array[:,1] < y_max_voxel))[0]

    if indices_relevant.size != 0:
        relevant_array = array[indices_relevant]
        stacked_array = np.vstack((relevant_array, voxel_array))
        stacked_unique_xy, unique_indices = np.unique(stacked_array[:,[0,1]],axis=0, return_index = True)
        final_voxel_array = stacked_array[unique_indices]

    else:
        final_voxel_array = voxel_array

    return final_voxel_array
