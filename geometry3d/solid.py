import trimesh
from trimesh.creation import extrude_polygon
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
import warnings

class Solid3D:
    def __init__(self, shape2d, height, name=None):
        """
        shape2d: Shape2D instance
        height : extrusion height
        """
        self.shape2d = shape2d
        self.height = height
        self.mesh = self.build()
        self.name = name or "Solid3D"

    def build(self):
        geom = self.shape2d.geom
        if geom is None or geom.is_empty:
            self.mesh = trimesh.Trimesh()
            return self.mesh

        polygons = self.__listify(geom)

        meshes = []
        for poly in polygons:
            if poly.is_empty or poly.area <= 0:
                continue
            if not poly.is_valid:
                warnings.warn(f"[WARN] Invalid polygon in {self.name}, attempting to fix.")
                poly = poly.buffer(0)
            try:
                m = extrude_polygon(poly, self.height)
                meshes.append(m)
            except Exception as e:
                print(f"[WARN] Failed to extrude {self.name}: {e}")

        self.mesh = trimesh.util.concatenate(meshes) if meshes else trimesh.Trimesh()
        return self.mesh

    def __listify(self, geom : Polygon | MultiPolygon | GeometryCollection) -> list[Polygon]:
        polygons = []
        if isinstance(geom, Polygon):
            polygons = [geom]
        elif isinstance(geom, MultiPolygon):
            polygons = list(geom.geoms)
        elif isinstance(geom, GeometryCollection):
            polygons = [g for g in geom.geoms if isinstance(g, Polygon)]
        return polygons