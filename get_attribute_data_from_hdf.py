import h5py

'''
get_attributes_from_hdf_5:
function that creates a dictionary of attributes of a hdf5 part_name

inputs:
h5_path: str of h5 path
part_name: str of the name of the desired part

output:
dictionary with key, value pairs
'''
def get_attributes_from_hdf_5 (h5_path, part_name):
    dict = {}
    with h5py.File(h5_path,'r') as h5:
        for item in h5[part_name].attrs.keys():
            dict[item] = h5[part_name].attrs[item]
        return dict


'''
calculate_part_dimensions:
function that calculates the dimensions of a part using its attributes

inputs:
h5_path: str of h5 path
part_name: str of the name of the desired part

outputs:
dict with lengthX, lengthY and height

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







if __name__ == "__main__":
    attrs = calculate_part_dimensions('/home/jan/Documents/CodeTDMStoHDF/Ausgangsdaten/examplerRun.h5', '0_00003_Canti3_cls')
    print(attrs)
