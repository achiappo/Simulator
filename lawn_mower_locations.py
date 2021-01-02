
import numpy as np
import multiprocessing as mp
from itertools import repeat
from time import time

import sys
sys.path.append('src/')

import matplotlib
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import src.utility as util
import src.coverage as cov
import src.plotting as plot
import src.simulator as sim


lawn_points = [[(0,10), (15,10)], 
               [(15,10), (15,0)], 
               [(15,0), (4,0)], 
               [(4,0), (4,3)], 
               [(4,3), (7,3)], 
               [(7,3), (7,2)], 
               [(7,2), (12,2)], 
               [(12,2), (12,6)], 
               [(12,6), (3,6)], 
               [(3,6), (3,3)], 
               [(3,3), (1,3)], 
               [(1,3), (1,5)], 
               [(1,5), (0,5)], 
               [(0,5), (0,10)]
              ]

region_points = [[(0,10), (15,10)], 
                 [(15,10), (15,0)], 
                 [(15,0), (2,0)], 
                 [(2,0), (0,5)],
                 [(0,5), (0,10)]
                ]


patch_size = 0.02
mower_size = 0.15
D = mower_size/2 - patch_size*np.sqrt(2)/2


kwargs = {'D': D,
          'theta_min': -3*np.pi/2, 
          'theta_max': 3*np.pi/2, 
          'unit_size': mower_size,
          'lawn_points': lawn_points,
          'region_points': region_points,
          'patch_size': patch_size
         }

CV = cov.Coverage(**kwargs)

CV()

mown_grid = CV.mown_grid
mown_area_ratio = CV.mown_area_ratio
path_unit0 = CV.path_unit0
path_unit1 = CV.path_unit1

_, ax = plot.get_lawn_region_plot(lawn_points, region_points)

ax.plot(*path_unit0[0], 'ro', ms=8, zorder=10);
ax.plot(*path_unit1[0], 'ro', ms=8, zorder=10);

x_mown, y_mown = mown_grid.ravel(order='F').reshape(2,-1)
ax.plot(x_mown, y_mown, 'w.', ms=1);

string = r"$\frac{\mathrm{mown\,\, area}}{\mathrm{lawn\,\, area}}$"
ax.text(6, 4, "{} = {:.2f}".format(string, mown_area_ratio), fontsize=22);

plt.show()
