from gdstk import Cell
from shapely.geometry import box, Polygon, MultiPolygon

class LayerStore:
    def __init__(self, cell: Cell):
        self._layers = {}

        for p  in cell.polygons:
            key = (p.layer, p.datatype)
            self._layers.setdefault(key, []).append(p.points)

        for p in cell.paths:
            key = (p.layers[0], p.datatypes[0])
            pathpolys = p.to_polygons()
            for poly in pathpolys:
                self._layers.setdefault(key, []).append(poly.points)

    def get(self, layer, datatype = 0):
        return self._layers.get((layer, datatype), [])
    
    def cut_with_rectangle(self, xmin: float, ymin: float, xmax: float, ymax: float):
        clip = box(xmin, ymin, xmax, ymax)

        for key, value in self._layers.items():
            new_polys = []
            for points in value:
                poly = Polygon(points)
                clipped = poly.intersection(clip)
                
                if clipped.is_empty:
                    continue

                if isinstance(clipped, Polygon):
                    polys = [clipped]
                elif isinstance(clipped, MultiPolygon):
                    polys = clipped.geoms
                else:
                    continue

                for p in polys:
                    new_polys.append(list(p.exterior.coords))
            self._layers[key] = new_polys
    