
__author__ = "Andrea Chiappo"
__email__ = "chiappo.andrea@gmail.com"

import numpy as np


def find_random_point_on_polygon(obj_x_loc, obj_y_loc):
    #get number of vertices
    n = len(obj_x_loc)
    
    #get edges connecting the vertices
    vi = [[obj_x_loc[(i+1)%n] - obj_x_loc[i],
           obj_y_loc[(i+1)%n] - obj_y_loc[i]] for i in range(n)]
    
    #get length of edges
    si = [np.linalg.norm(v) for v in vi]
    
    #get polygon length
    length = sum(si)
    
    #get point in the range [0, length)
    D = np.random.rand() * length

    #find coordinates of new point along the polygon
    for i,s in enumerate(si):
        if D>s: 
            D -= s
        else: 
            break
    l = D/s

    new_point = [obj_x_loc[i] + l*vi[i][0], 
                 obj_y_loc[i] + l*vi[i][1]]

    return new_point

