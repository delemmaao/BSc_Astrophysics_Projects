"""
Base functions and classes for use in Space Dynamics
"""
import numpy as np  # numerical python
from scipy.integrate import odeint  # the solver from scipy
from typing import Callable, Sequence, Tuple, Optional
import warnings


class GravBody:
    """
    Create a gravitational body as an object by name, optionally providing in SI units:
    mass, radius, separation (from star if a planet), scale_height of atmosphere and surface_density of atmosphere.
    ONLY Earth is given in-built, for all others you should find their parameters online (NASA fact sheets).
    """

    def __init__(self, name: str, mass: Optional[float] = None,
                 radius: Optional[float] = None, separation: Optional[float] = None,
                 scale_height: Optional[float] = None, surface_density: Optional[float] = None):
        self.name = name.strip().capitalize()  # name of object
        self.mass = mass
        self.radius = radius
        self.separation = separation
        self.scale_height = scale_height
        self.surface_density = surface_density

    @classmethod
    def earth(cls):
        return cls('Earth', mass=5.9722e24, radius=6371e3,
                   separation=149.598e9, scale_height=8500, surface_density=1.217)
    @classmethod
    def moon(cls): 
        return cls('Moon', mass=0.07346e24, radius=1737.4e3)
    
    @classmethod
    def mars(cls): 
        return cls('Mars', mass=0.64169e24, radius=3389.5e3,
                   separation=149.598e9, scale_height=11.3e3, surface_density=0.02)

class Probe:
    """
    Create a probe/ spacecraft as an object with set values of drag and mass.
    Will handle either 1D, 2D or 3D cartesian cases and solve them through an ordinary differential equation solver.
    """

    def __init__(self, driver: Callable[[Sequence], Sequence], tfinal: float, tstepnum: int,
                 event: Optional[float] = None, eventflip: bool = False,
                 x0: Optional[float] = None, vx0: Optional[float] = None,
                 y0: Optional[float] = None, vy0: Optional[float] = None,
                 z0: Optional[float] = None, vz0: Optional[float] = None):
        """
        Initialisation class method

        Parameters
        ----------
        driver
            The function that will drive the odesolver
        tfinal
            The final time to iterate from 0 to
        tstepnum
            The number of steps in the linear time array; the more the better but longer
        event
            A value to cut posvel to based on position
        eventflip
            If true, make the event comparison be greater than rather than less than
        x0
            Start position in x (always required)
        vx0
            Start velocity in x (always required)
        y0
            Start position in y (used in 2D & 3D cases)
        vy0
            Start velocity in y (used in 2D & 3D cases)
        z0
            Start position in z (used in 3D cases)
        vz0
            Start velocity in z (used in 3D cases)
        """
        # unrealistic constants
        self.mass = 1.
        self.area = 0.01
        self.drag_coefficient = 1.
        self.driver = driver  # the driver function for solving the differential equations
        self.tfinal = tfinal  # final time step
        self.tstepnum = int(tstepnum)  # number of steps for the solver to take
        self.event = event
        self.eventflip = eventflip
        # creating posvel0 (initial conditions array)
        if np.any([val is not None for val in (z0, vz0)]):  # 3D case
            if np.any([val is None for val in (x0, y0, z0, vx0, vy0, vz0)]):
                raise AttributeError('x0, y0, z0, vx0, vy0, vz0 must be defined')
            self.posvel0 = self.__posvel0_create__(x0, y0, z0, vx0, vy0, vz0)
        elif np.any([val is not None for val in (y0, vy0)]):  # 2D case
            if np.any([val is None for val in (x0, y0, vx0, vy0)]):
                raise AttributeError('x0, y0, vx0, vy0 must be defined')
            self.posvel0 = self.__posvel0_create__(x0, y0, vx0, vy0)
        else:  # 1D case
            if np.any([val is None for val in (x0, vx0)]):
                raise AttributeError('x0 and vx0 must be defined')
            self.posvel0 = self.__posvel0_create__(x0, vx0)
        return

    @staticmethod
    def __posvel0_create__(*conditions) -> list:
        num_vars = len(conditions)
        if num_vars % 2:
            raise ValueError('Require even number of inputs in posvel0 (2, 4, 6)')
        ind_split = num_vars // 2
        pos = list(conditions[:ind_split])
        vel = list(conditions[ind_split:])
        return pos + vel

    def odesolve(self) -> Tuple[Sequence, Sequence]:
        def quadsum(i):
            if len(i) == 1:
                return i[0]
            return np.sqrt(np.sum(i ** 2))
        warnings.simplefilter('ignore')
        t: np.ndarray = np.linspace(0, self.tfinal, self.tstepnum)  # linearly separated time steps
        posvel = np.array(odeint(self.driver, self.posvel0, t, tfirst=True))  # solved posvel
        if self.event is not None:
            pos: np.ndarray = posvel[:, :posvel.shape[1] // 2]
            try:
                if not self.eventflip:
                    ind: int = np.flatnonzero(np.array([quadsum(i) for i in pos]) < self.event)[0]
                else:
                    ind = np.flatnonzero(np.array([quadsum(i) for i in pos]) > self.event)[0]
                if ind == len(pos) - 1:
                    raise IndexError
            except IndexError:
                pass
            else:
                posvel = posvel[:ind + 1]
                t = t[:ind + 1]
        return t, posvel
