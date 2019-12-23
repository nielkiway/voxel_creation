import numpy as np
import os

list_name  = ["Lukas",'lisa','detlef','jan']

for name in list_name:
    print('hallo ' + name)
    os.mkdir('/home/jan/Desktop/' + name)
