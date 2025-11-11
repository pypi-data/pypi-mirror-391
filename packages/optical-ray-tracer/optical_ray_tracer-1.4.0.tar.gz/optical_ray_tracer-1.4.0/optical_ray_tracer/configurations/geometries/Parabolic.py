from optical_ray_tracer.configurations.main import Geometry
from decimal import Decimal, getcontext
from typing import Union
import sympy as spy
import numpy as np
# from numba import jit
from optical_ray_tracer.utils.rotation_vect import rotationVectU
from optical_ray_tracer.rays.source.main import RaySource
getcontext().prec = 80


class ParabolicReflector(Geometry):
    """
    Class: parabolicReflector
    This class defines a parabolic reflector geometry with specified focal lengths, height, and rotation angle. 
    It provides methods to compute the symbolic equation, boundaries, volume, and generate rays from a source 
    within the reflector's angular view.
    Attributes:
        f_x (float): Focal length along the x-axis. Default is 0.5.
        f_y (float): Focal length along the y-axis. Default is 0.5.
        h (float): Height of the parabolic reflector. Default is 0.5.
        z_0 (float): Offset along the z-axis. Default is 0.0.
        rot_angle (float): Rotation angle of the reflector in radians. Default is 0.0.
        edge_tol (float): Tolerance for edge calculations. Default is 1e-3.
        diameter_x (float): Diameter of the reflector along the x-axis.
        diameter_y (float): Diameter of the reflector along the y-axis.
        z_max (float): Maximum z-coordinate of the reflector.
        rot_x (numpy.ndarray): Rotation matrix for the x-axis.
    Methods:
        __init__(f_x=0.5, f_y=0.5, h=0.5, z_0=0.0, rot_angle=0.0):
            Initializes the parabolic reflector with the given parameters.
        symbolic_equation():
            Computes the symbolic equation of the parabolic reflector in the rotated frame.
        boundaries():
            Computes the boundaries of the parabolic reflector in the rotated frame, considering the height 
        volume():
            Computes the isosurface volume points of the parabolic reflector within the specified boundaries.
        generate_rays_from_source(n_rays: int, source: object):
            Generates rays originating from a source within the bounds of the parabolic geometry.
        parabola_aperture_conic_section(phi):
            Computes the coordinates of a point on the parabola's aperture for a given azimuthal angle `phi`.
        parabola_aperture_theta_limit(phi: float, pt_origin: np.ndarray):
            Calculates the angular limit (theta) for a parabolic aperture given a specific azimuthal angle (phi) 
        compute_material_surface(r: Union[float, np.ndarray], h: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
            Computes the surface area of a parabolic material based on its ray (r) and height (h).
        collection_area():
            Calculates the collection area of the parabolic geometry as the area of an ellipse defined by 
            the semi-major and semi-minor axes.
    """

    def __init__(self, f_x=0.5, f_y=0.5, h=0.5, surf_pos=None, rotation_angle=0.0, edge_tol=1e-3):
        super().__init__(surf_pos=surf_pos, rotation_angle=rotation_angle, edge_tol=edge_tol)

        self.f_x = f_x
        self.f_y = f_y
        self.h = h
        self.diameter_x = 2 * np.sqrt(h * 4 * f_x) - self.edge_tol
        self.diameter_y = 2 * np.sqrt(h * 4 * f_y) - self.edge_tol
        self.z_max = h + self.geometry_position[2]
        # Rotation matrix around x axis
        self.rot_x = rotationVectU(np.array([1, 0, 0]), self.rotation_angle)

    def symbolic_equation(self):
        """
        Compute the symbolic equation of the parabolic reflector in the rotated frame.
        This method calculates the symbolic representation of the parabolic reflector's 
        equation after applying a rotation transformation. The equation is expressed 
        in terms of the rotated coordinates and the parameters of the parabola.
        Returns:
            sympy.Expr: A symbolic expression representing the parabolic reflector's 
            equation in the rotated frame. The equation is of the form:
                Z - (1/(4*fx))*X² - (1/(4*fy))*Y² - Z_0 = 0
            where `fx` and `fy` are the focal lengths along the x and y axes, respectively, 
            and `Z_0` is the offset along the z-axis.
        """
        x_m, y_m, z_m = spy.symbols('x y z')
        u = spy.Matrix([x_m - self.geometry_position[0], y_m - self.geometry_position[1], z_m - self.geometry_position[2]])
        rot = spy.Matrix(self.rot_x)
        u_rot = rot * u
        # Equation Z - (1/(4*fx))*X² - (1/(4*fy))*Y² - Z_0 = 0
        a = (1. / (4. * self.f_x))
        b = (1. / (4. * self.f_y))
        func = spy.simplify(u_rot[2] - a * u_rot[0] ** 2 - b * u_rot[1] ** 2)

        return func

    def solved_symbolic_equation(self):
        x_m, y_m, z_m = spy.symbols('x y z')
        return spy.solve(self.symbolic_equation(), z_m)[0]
    
    def boundaries(self):
        """
        Compute the boundaries of the parabolic reflector in the rotated frame, considering the desired height 
        and dimensions of the reflector.
        The method calculates the minimum and maximum extents of the reflector in the y and z directions 
        after applying a rotation transformation. The x-direction boundaries are determined by the diameter 
        of the reflector.
        Returns:
            list: A list of boundaries in the format [[xmin, xmax], [ymin, ymax], [zmin, zmax]], where:
                - xmin, xmax: The minimum and maximum x-coordinates, determined by the reflector's diameter.
                - ymin, ymax: The minimum and maximum y-coordinates after rotation.
                - zmin, zmax: The minimum and maximum z-coordinates after rotation.
        
        Compute the boundaries of the parabolic reflector in the rotated frame taking in account the desired height of the reflector
        """

        # Compute the graphical extent after the rotation
        rot_lim_1 = np.dot(self.rot_x, np.array([0, -self.diameter_y/2 + self.geometry_position[1], 0]))
        rot_lim_2 = np.dot(self.rot_x, np.array([0, self.diameter_y/2 + self.geometry_position[1], 0]))
        rot_lim_3 = np.dot(self.rot_x, np.array([0, -self.diameter_y/2 + self.geometry_position[1], self.z_max]))
        rot_lim_4 = np.dot(self.rot_x, np.array([0, self.diameter_y/2 + self.geometry_position[1], self.z_max]))
        yl_min = np.min(np.array([rot_lim_1[1], rot_lim_2[1], rot_lim_3[1], rot_lim_4[1]]))
        yl_max = np.max(np.array([rot_lim_1[1], rot_lim_2[1], rot_lim_3[1], rot_lim_4[1]]))
        zl_min = np.min(np.array([rot_lim_1[2], rot_lim_2[2], rot_lim_3[2], rot_lim_4[2]]))
        zl_max = np.max(np.array([rot_lim_1[2], rot_lim_2[2], rot_lim_3[2], rot_lim_4[2]]))

        return [[-self.diameter_x/2 + self.geometry_position[0], self.diameter_x/2 + self.geometry_position[0]],
                [yl_min, yl_max], [zl_min, zl_max]]

    def volume(self):
        """
        Compute the isosurface volume points of the reflector within the specified boundaries.
        This method calculates the volume of the isosurface defined by the reflector's equation.
        It evaluates the equation over a 3D grid of points within the boundaries and applies a rotation
        transformation to determine the valid points. Points outside the height limit are excluded.
        Returns:
            numpy.ndarray: A 3D array representing the isosurface volume, where values close to zero
            correspond to the isosurface points.
        Notes:
            - The method uses symbolic computation to define the equation and evaluates it
              numerically over the grid.
            - The rotation transformation is applied to align the points with the reflector's orientation.
            - Debugging information about the volume shape and the number of isosurface points can be printed.
        """

        # Compute parabola surface equation
        x, y, z = spy.symbols('x y z')
        equ = self.symbolic_equation()
        parabola_equ = spy.lambdify((x, y, z), equ, 'numpy')
        bounds = self.boundaries()
        nb_pts = 9
        xx, yy, zz = np.meshgrid(np.linspace(bounds[0][0], bounds[0][1], nb_pts),
                                 np.linspace(bounds[1][0], bounds[1][1], nb_pts),
                                 np.linspace(bounds[2][0], bounds[2][1], nb_pts),
                                 indexing='ij')
        values = parabola_equ(xx, yy, zz)
        z_rot = np.zeros(xx.shape)
        for ii in np.arange(nb_pts):
            for jj in np.arange(nb_pts):
                for kk in np.arange(nb_pts):
                    z_rot[ii, jj, kk] = np.dot(self.rot_x,
                                               (xx[ii, jj, kk], yy[ii, jj, kk], zz[ii, jj, kk]))[2]

        values[z_rot >= self.h] = 0.1
        # print("Volume shape: ", values.shape)
        # print("IsoSurface nb of pts", np.size(np.where(np.abs(values)== 0.0)))

        return [values]

    # @jit(parallel=True)
    def generate_rays_from_source(self, n_rays: int, source: RaySource):
        """
        Generate rays originating from a source within the bounds of the reflector geometry.
        This method generates a specified number of rays (`n_rays`) from a given source object.
        The rays are distributed based on the reflector aperture and are defined by their
        direction vectors and origin points.
        Args:
            n_rays (int): The total number of rays to generate. The rays are distributed
                          approximately evenly in a grid-like pattern.
            source (object): The source object that provides the origin points and direction
                             vectors for the rays. The source object must implement a `rays`
                             method that accepts `theta` and `phi` parameters.
        Returns:
            tuple: A tuple containing two lists:
                - vec_dir (list): A list of direction vectors for the generated rays.
                - pt_orig (list): A list of origin points for the generated rays.
        Notes:
            - The `source.rays` method is expected to return direction vectors and origin
              points for the specified `theta` and `phi` values.
        """
        n_phi = int(np.sqrt(n_rays))
        n_theta = int(n_rays/n_phi)
        phi_tab = np.linspace(0, 2 * np.pi, n_phi, endpoint=False)
        vec_dir = []
        pt_orig = []
        for idx, val in enumerate(phi_tab.tolist()):
            # print("Origine = ", np.array(source.pt_origin))
            theta_lim, phi_val = self.parabola_aperture_theta_limit(val, np.array(source.pt_origin))
            if idx==0:
                theta_tab = np.linspace(theta_lim[0], theta_lim[1], num=n_theta, endpoint=False)
            else:
                theta_tab = np.linspace(theta_lim[0] + (theta_lim[1]-theta_lim[0]) / n_theta,
                                        theta_lim[1], num=n_theta, endpoint=False)
            v, p = source.rays(theta=theta_tab, phi=phi_val)
            vec_dir += v
            pt_orig += p

        return vec_dir, pt_orig

    def parabola_aperture_conic_section(self, phi: float):
        """
        The function computes the coordinates of a point on the parabola's aperture for a given a specific 
        azimuthal angle `phi`. The aperture is defined by the diameters along the x and y axes, and the 
        maximum z-coordinate (`z_max`). The resulting point is then transformed using a rotation matrix `rot_x`.
        Parameters:
        -----------
        phi : float
            The angle (in radians) used to compute the point on the parabolic aperture.
        Returns:
        --------
        numpy.ndarray
            A 3D vector [x, y, z] representing the coordinates of the point on the parabolic aperture.
        """

        a = np.array([(self.diameter_x/2 * np.cos(phi) ) + self.geometry_position[0],
                      (self.diameter_y/2 * np.sin(phi) ) + self.geometry_position[1],
                      self.z_max])
        vec = np.dot(self.rot_x, a)

        return vec

    def parabola_aperture_theta_limit(self, phi: float, pt_origin:np.ndarray):
        """
        Calculate the angular limit (theta) for a parabolic aperture given a specific azimuthal angle (phi) 
        and an origin point.
        This method computes the angular limit based on the geometry of a parabolic aperture, the position 
        of a point of origin, and the azimuthal angle. It uses vector mathematics to determine the angle 
        between vectors originating from the point of origin to the parabola's aperture and its rotated axis.
        Args:
            phi (float): The azimuthal angle in radians, which determines the position on the parabola's aperture.
            pt_origin (np.ndarray): A 3D numpy array representing the coordinates of the origin point.
        Returns:
            theta_lim: The angular limit (theta) calculated using the geometry of the parabola.
        """

        O_m = np.dot(self.rot_x, np.array([self.geometry_position[0], self.geometry_position[1], self.z_max]))
        M = self.parabola_aperture_conic_section(phi)
        S = pt_origin
        # OM = M - O_m
        # a = Decimal(OM[0] ** 2 + OM[1] ** 2 + OM[2] ** 2).sqrt()
        SO = O_m - S
        SO_norm = (Decimal(SO[0]) ** 2 + Decimal(SO[1]) ** 2 + Decimal(SO[2]) ** 2).sqrt()
        SM = M - S
        SM_norm = (Decimal(SM[0]) ** 2 + Decimal(SM[1]) ** 2 + Decimal(SM[2]) ** 2).sqrt()
        SxyM = np.array([SM[0], SM[1], 0]) #Projection of SM on (xy) plan
        SxyM_norm = Decimal(SxyM[0] ** 2 + SxyM[1] ** 2 + SxyM[2] ** 2).sqrt()
        # SxyO = np.array([0, 0, self.z_max]) - Sxy
        # e = Decimal(SxyO[0] ** 2 + SxyO[1] ** 2 + SxyO[2] ** 2).sqrt()
        # # dot products
        # sm_dot_sz = Decimal(SM[2]) * Decimal(SZ[2])
        # sxym_dot_sxyo = (Decimal(SxyM[0]) * Decimal(SxyO[0]) + Decimal(SxyM[1]) * Decimal(SxyO[1]) + Decimal(SxyM[2]) *
        #                  Decimal(SxyO[2]))
        # from dot product formula
        # cos_val = Decimal(dot_product) / Decimal(b * c)
        cos_theta = -Decimal(SM[2]) / SM_norm
        cos_theta_zero = -Decimal(SO[2]) / SO_norm
        # theta_lim = np.arctan2(float(SxyM_norm), -SM[2])

        if float(SxyM_norm)==0.0:
            # cos_phi = np.cos(phi)
            phi_val = phi
        else:
            # cos_phi = Decimal(SM[0]) / SxyM_norm
            tan_phi = (Decimal(SM[1]) / Decimal(SM[0])) if not SM[0]==0.0 else np.inf
            phi_val = np.arctan(float(tan_phi)) + int(SM[0]<0.0) * np.pi

        if (1-abs(float(cos_theta)))<1e-2:
            # small angles approximation
            theta_lim = float(2 * (1 - cos_theta))**0.5
        else:
            # full value
            theta_lim = np.arccos( float(cos_theta) )

        if (1-abs(float(cos_theta_zero)))<1e-2:
            # small angles approximation
            theta_zero = float(2 * (1 - cos_theta_zero)) ** 0.5
        else:
            # full value
            theta_zero = np.arccos( float(cos_theta_zero) )

        print("theta_zero = ", theta_zero * 180 / np.pi)
        print("theta_lim = ", theta_lim*180/np.pi)
        print("phi_val = ", phi_val*180/np.pi)

        return [theta_zero, theta_lim], phi_val
    
    @staticmethod
    def compute_material_surface(r: Union[float, np.ndarray], h: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Compute the surface area of a parabolic material.
        This function calculates the area of a parabola based on its ray (r) and height (h). 
        The inputs can be either floats or numpy arrays, but if numpy arrays are used, they must have the same shape.
        :param r: The ray of the parabola. Can be a float or a numpy array.
        :type r: float or numpy.ndarray
        :param h: The height of the parabola. Can be a float or a numpy array.
        :type h: float or numpy.ndarray
        :return: The computed area of the parabola. The return type matches the type of the inputs (float or numpy array).
        :rtype: float or numpy.ndarray
        """
        if isinstance(r, np.ndarray) and isinstance(h, np.ndarray):
            if not np.array_equal(r.shape, h.shape):
                raise ValueError("r and h should be numpy arrays of the same dimension or float")
        elif type(r) != type(h):
            raise ValueError("r and h should be same type: numpy arrays of the same dimension or float")

        a = np.pi * r / (6 * h ** 2)
        b = (r ** 2 + 4 * h ** 2) ** (3 / 2)
        area = a * (b - r ** 3)

        return area
    
    def collection_area(self):
        """
        Calculate the collection area of the parabolic geometry.

        The collection area is computed as the area of an ellipse defined by
        the semi-major axis (diameter_x / 2) and the semi-minor axis (diameter_y / 2).
        Note: This calculation does not currently account for the angle of collection.

        Returns:
            float: The collection area of the parabolic geometry.
        """
        # we should consider the angle of collection in future versions...
        return np.pi * self.diameter_x / 2 * self.diameter_y / 2
