import gdstk
from shapely.geometry import Polygon
import numpy as np

class GDSLoader:
    def __init__(self, scale=1.0):
        self.scale = scale

    def load_gds(self, filename):
        lib = gdstk.read_gds(filename)
        if not lib.top_level():
            raise RuntimeError("No top-level cells found")
        cell = lib.top_level()[0]
        cell.flatten()
        return cell

    def extract_polygons(self, cell, datatype=0):
        layer_polygons = {}

        for poly in cell.polygons:
            if poly.datatype != datatype:
                continue
            points = poly.points * self.scale
            shp = Polygon(points)
            if not shp.is_empty:
                layer_polygons.setdefault((poly.layer, poly.datatype), []).append(shp)

        for path in cell.paths:
            if path.datatype != datatype:
                continue
            for poly in path.to_polygons():
                points = poly.points * self.scale
                shp = Polygon(points)
                if not shp.is_empty:
                    layer_polygons.setdefault((path.layer, path.datatype), []).append(shp)

        return layer_polygons
