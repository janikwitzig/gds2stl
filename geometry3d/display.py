import trimesh
import numpy as np
from geometry3d.solid import Solid3D

def show_solid3d(solid: Solid3D, color=None):
    mesh = solid.mesh
    if mesh is None:
        return

    if color is not None:
        mesh.visual.face_colors = color

    mesh.show()

def show_scene(scene):
    """
    scene: trimesh.Scene
    """
    if scene is not None:
        scene.show()
