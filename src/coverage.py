__author__ = "Andrea Chiappo"
__email__ = "chiappo.andrea@gmail.com"

import numpy as np

from shapely.geometry import Point

from simulator import Simulator

class Coverage(Simulator):
    """
    Class to initialise two units and run them through repeated operation 
    cycles, keeping track of the area covered, stopping them when the 
    total coverage exceed a threshold
    """

    def __init__(self, **kwargs):
        kwargs['coverage'] = self.find_mown_area
        super(Coverage, self).__init__(**kwargs)
        
        self.D = kwargs['D'] if 'D' in kwargs else 0.05
        self.patch_size = kwargs['patch_size'] if 'patch_size' in kwargs else 0.02
        self.target_ratio = kwargs['target_ratio'] if 'target_ratio' in kwargs else 0.95
        self.mown_grid = np.array([[None,None]], dtype=float)
        
        self.build_lawn_grid()
    
    def build_lawn_grid(self):
        """
        Given a lawn area, build a fine grid representing it
        which will determine the mowing progress
        """

        xmin, ymin, xmax, ymax = self.region_polygon.bounds

        x_grid = np.arange(xmin, xmax+self.patch_size, self.patch_size)
        y_grid = np.arange(ymin, ymax+self.patch_size, self.patch_size)
        region_grid = np.zeros((len(x_grid), len(y_grid), 2))

        for j,(y_i,y_f) in enumerate(zip(y_grid[:-1], y_grid[1:])):
            for i,(x_i,x_f) in enumerate(zip(x_grid[:-1],x_grid[1:])):
                region_grid[i,j] = [(x_f+x_i)/2, (y_f+y_i)/2]

        region_grid = region_grid.reshape(-1,2)

        exclude_indices = []
        for i,(x,y) in enumerate(region_grid):
            if not self.lawn_polygon.contains(Point(x, y)):
                exclude_indices.append(i)

        include_indices = np.arange(len(region_grid))
        include_indices = np.delete(include_indices, exclude_indices)

        self.lawn_grid = region_grid[include_indices]

    def find_mown_area(self, position):
        """
        Determine the lawn patches covered by the present position of a unit.
        This is obtained by calculating the distance of the patches centers 
        from the unit's position and marking the ones that are closer than 
        the unit's size. 
        The marking is achieved by setting to True the component of an 
        array representing the patches' coordinates.
        """
        
        #boolean array for every lawn patch: True if mower passed, False otherwise
        mown_patches_grid = np.zeros(len(self.lawn_grid), dtype=bool)

        #determine the distance of every patch from the mower's position
        pos_patch_distance = np.linalg.norm(self.lawn_grid-position, axis=1)

        #identify the patches within a distance D from the mower's position
        patches_indices = np.where(pos_patch_distance < self.D)[0]

        #set to True those patches where the mower has passed
        mown_patches_grid[patches_indices] = True

        temp_grid = self.lawn_grid[mown_patches_grid]

        self.mown_grid = np.concatenate((self.mown_grid, temp_grid))

    def __call__(self, verbose=False):
        """
        Method to repeatedly initiate new operation cycles, until the ratio 
        of the covered area to the total allowed (lawn) surface is larger than
        a (default but user-definable) ratio.
        """
        
        self.iteration = 0
        self.mown_area_ratio = 0
        
        first_execution = True

        while self.mown_area_ratio < self.target_ratio:
            if verbose:
                print(f"starting iteration {self.iteration}")
                print("simulate mowers")

            self.simulate(restart=True)

            if first_execution:
                self.mown_grid = self.mown_grid[1:]
                first_execution = False

            self.mown_grid = np.unique(self.mown_grid, axis=0)

            grid_area = len(self.lawn_grid) * self.patch_size**2
            mown_area = len(self.mown_grid) * self.patch_size**2

            self.mown_area_ratio = mown_area / grid_area
            
            if verbose:
                print(f"end of iteration {self.iteration}, ratio {self.mown_area_ratio}")

            self.iteration += 1

