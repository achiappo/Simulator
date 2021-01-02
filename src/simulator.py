__author__ = "Andrea Chiappo"
__email__ = "chiappo.andrea@gmail.com"

import numpy as np
from math import pi

import utility as util

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Base(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        self.theta_max = kwargs['theta_max']
        self.theta_min = kwargs['theta_min']
        self.lawn_points = kwargs['lawn_points']
        self.region_points = kwargs['region_points']

        self._build_polygons()
    
    def _build_polygons(self):
        region_perimeter = np.array(self.region_points).reshape(-1,2)[::2]
        region_perimeter = np.vstack((region_perimeter, region_perimeter[0]))
        self.region_polygon = Polygon(region_perimeter)

        lawn_perimeter = np.array(self.lawn_points).reshape(-1,2)[::2]
        lawn_perimeter = np.vstack((lawn_perimeter, lawn_perimeter[0]))
        self.lawn_polygon = Polygon(lawn_perimeter)

    def find_initial_position(self):
        x_verts, y_verts = np.array(self.lawn_polygon.boundary.coords).T
        pos = util.find_random_point_on_polygon(x_verts, y_verts)
        return pos

    def _new_direction(self):
        a = self.theta_min
        b = self.theta_max
        return np.random.rand() * (b-a) + a

    def _calculate_autonomy(self):
        max_real_distance = self.velocity * self.autonomy
        max_perimeter_len = max(self.lawn_polygon.bounds)
        size_ratio = max_perimeter_len / self.real_perimeter_size
        return round(max_real_distance * size_ratio / self.step)
    
    def _inside_perimeter(self, x, y):
        point = Point(x, y)
        return self.lawn_polygon.contains(point)


class Simulator(Base):
    def __init__(self, **kwargs):
        super(Simulator, self).__init__(**kwargs)
        
        self.step = kwargs['step'] if 'step' in kwargs else 0.05
        self.units = kwargs['units'] if 'units' in kwargs else 2
        self.velocity = kwargs['velocity'] if 'velocity' in kwargs else 0.5
        self.autonomy = kwargs['autonomy'] if 'autonomy' in kwargs else 1800
        self.real_perimeter_size = kwargs['size'] if 'size' in kwargs else 80
        self.unit_size = kwargs['unit_size'] if 'unit_size' in kwargs else 0.15
        self.max_stretch_len = kwargs['max_len'] if 'max_len' in kwargs else 16
        self.find_mown_area = kwargs['coverage'] if 'coverage' in kwargs else None

        self.max_n_steps = self._calculate_autonomy()
        
        self.stop_unit0 = False
        self.stop_unit1 = False

        self.steps_unit0 = 0
        self.steps_unit1 = 0
        
        # initialise units
        for u in range(self.units):
            pos0 = self.find_initial_position()
            exec(f"self.pos_unit{u} = pos0")
            exec(f"self.path_unit{u} = [pos0]")
            exec(f"self.dir_unit{u} = self._initial_direction(*pos0)")
        
    def _initial_direction(self, x0, y0):
        # find initial direction of a unit
        found = False
        while not found:
            initial_direction = self._new_direction()
            x, y = self._new_step(self.step, initial_direction)
            xnew = x0 + x
            ynew = y0 + y
            if self._inside_perimeter(xnew, ynew):
                found = True
        return initial_direction
    
    def _bump(self):
        # 0.15 : unit scale size 
        # scale 80cm (~unit size) / 80m (~lawn width)
        pos_unit0 = np.array(self.pos_unit0)
        pos_unit1 = np.array(self.pos_unit1)
        unit_distance = np.linalg.norm(pos_unit0 - pos_unit1)
        if unit_distance < self.unit_size:
            return True
        else:
            return False
    
    def _new_step(self, t, direction):
        x = np.cos(direction) * t
        y = np.sin(direction) * t
        return x,y
    
    def _advancer(self, pos0s, directions):
        outised_perimeter_unit0 = False
        outised_perimeter_unit1 = False
        
        [x0_unit0, y0_unit0], [x0_unit1, y0_unit1] = pos0s
        direction_unit0, direction_unit1 = directions
        
        distances = np.arange(0, self.max_stretch_len, self.step) 
        distances += self.step
        for distance in distances:
            
            #interrupt if both units have reached max n steps
            if self.stop_unit0 and self.stop_unit1:
                break

            #advance unit0 if it has covered less than max n steps
            if self.steps_unit0 < self.max_n_steps:
                if not outised_perimeter_unit0:
                    xnew, ynew = self._new_step(distance, direction_unit0)
                    x_unit0 = x0_unit0 + xnew
                    y_unit0 = y0_unit0 + ynew
                    self.pos_unit0 = [x_unit0, y_unit0]
            else:
                self.stop_unit0 = True
            
            #advance unit1 if it has covered less than max n steps
            if self.steps_unit1 < self.max_n_steps:
                if not outised_perimeter_unit1:
                    xnew, ynew = self._new_step(distance, direction_unit1)
                    x_unit1 = x0_unit1 + xnew
                    y_unit1 = y0_unit1 + ynew
                    self.pos_unit1 = [x_unit1, y_unit1]
            else:
                self.stop_unit1 = True
            
            #check if units bumped into each other
            if self._bump():
                break
            else:
                #interrupt if both units have reached the edge
                if outised_perimeter_unit0 and outised_perimeter_unit1:
                    break
                else:
                    if not self.stop_unit0 and not outised_perimeter_unit0:
                        #check if new step takes unit0 beyond the perimeter
                        if not self._inside_perimeter(*self.pos_unit0):
                            outised_perimeter_unit0 = True
                        else:
                            if self.find_mown_area is not None:
                                self.find_mown_area(self.pos_unit0)
                            self.path_unit0.append(self.pos_unit0)
                            self.steps_unit0 += 1
                    
                    if not self.stop_unit1 and not outised_perimeter_unit1:
                        #check if new step takes unit1 beyond the perimeter
                        if not self._inside_perimeter(*self.pos_unit1):
                            outised_perimeter_unit1 = True
                        else:
                            if self.find_mown_area is not None:
                                self.find_mown_area(self.pos_unit0)
                            self.path_unit1.append(self.pos_unit1)
                            self.steps_unit1 += 1
    
    def _new_stretch(self, first_call=True):
        pos0s = []
        directions = []
        for u in range(self.units):
            direction = eval(f"self.dir_unit{u}")
            if first_call:
                pos0 = eval(f"self.pos_unit{u}")
                pos0s.append(pos0)
                directions.append(direction)
            else:
                direction += self._new_direction()
                exec(f"self.dir_unit{u} = direction")
                pos0 = eval(f"self.path_unit{u}[-1]")
                pos0s.append(pos0)
                directions.append(direction)
        return pos0s, directions
    
    def simulate(self, restart=False):
        if restart:
            self.stop_unit0 = False
            self.stop_unit1 = False
            self.steps_unit0 = 0
            self.steps_unit1 = 0
        
        pos0s, directions = self._new_stretch()
        
        #simulate until both units cover the max aloud distance
        while not self.stop_unit0 and not self.stop_unit1:
            self._advancer(pos0s, directions)
            pos0s, directions = self._new_stretch(False)
