# Geometry base class for configuration geometries
from typing import Optional




class Geometry:

    def __init__(self, surf_pos, rotation_angle, edge_tol=1e-3):

        if surf_pos is None:
            surf_pos = [0.0, 0.0, 0.0]
        self.geometry_position = surf_pos
        self.rotation_angle = rotation_angle
        self.edge_tol = edge_tol

    def symbolic_equation(self):
        return None

    def volume(self):
        return []

    def collection_area(self):
        return 0.0

    def generate_rays_from_source(self, n_rays: int, source: object):
        return [], []
