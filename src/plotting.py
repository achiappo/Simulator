
__author__ = "Andrea Chiappo"
__email__ = "chiappo.andrea@gmail.com"

import numpy as np

import matplotlib.path as mpath
import matplotlib.pyplot as mplt
import matplotlib.patches as mpatch
import matplotlib.animation as manim
import matplotlib.collections as mcl

from shapely.geometry.polygon import Polygon


def get_lawn_region_plot(lawn_points, region_points):

    fig, ax = mplt.subplots(figsize=(12,8))

    pp = mcl.LineCollection(region_points, linewidths=1, colors='r')
    lp = mcl.LineCollection(lawn_points, linewidths=2, colors='k')

    ax.add_collection(pp)
    ax.add_collection(lp)

    lawn_perimeter = np.array(lawn_points).reshape(-1,2)[::2]
    lawn_perimeter = np.vstack((lawn_perimeter, lawn_perimeter[0]))

    path = mpath.Path(lawn_perimeter, closed=True)
    patch = mpatch.PathPatch(path, facecolor='green', alpha=0.3)
    ax.add_patch(patch);

    region_perimeter = np.array(region_points).reshape(-1,2)[::2]
    region_perimeter = np.vstack((region_perimeter, region_perimeter[0]))

    lawn_polygon = Polygon(lawn_perimeter)
    region_polygon = Polygon(region_perimeter)
    excluded_polygon = region_polygon.difference(lawn_polygon)
    excluded_perimeter = np.array(excluded_polygon.exterior.coords)

    path = mpath.Path(excluded_perimeter, closed=True)
    patch = mpatch.PathPatch(path, facecolor='black', alpha=0.3)
    ax.add_patch(patch);

    ax.set_xlabel('n', fontsize=14);
    ax.set_ylabel('n', fontsize=14);
    ax.set_xlim(-1, 16);
    ax.set_ylim(-1, 11);
    ax.autoscale();
    ax.margins(0.1);
    ax.axis('off');

    return fig, ax

def get_mowers_animation(ax, fig, path0, path1, interval=2):

    ax.plot(*path0[0], 'C3o', ms=8, zorder=10);
    ax.plot(*path1[0], 'C2o', ms=8, zorder=10);

    line0, = ax.plot([], [], 'C4.')
    line1, = ax.plot([], [], 'C8.')
    
    def init():
        line0.set_data([], [])
        line1.set_data([], [])
        return line0, line1

    def animate(i):
        line0.set_data(path0[:i,0], path0[:i,1])
        line1.set_data(path1[:i,0], path1[:i,1])
        return line0, line1
        
    maxl = max(len(path0), len(path1))

    animation = manim.FuncAnimation(fig,
                                    animate,
                                    init_func=init,
                                    frames=maxl,
                                    interval=interval,
                                    repeat=False,
                                    blit=True,
                                    cache_frame_data=True)

    return animation
