from gdstk import Cell
from shapely.geometry import box, Polygon, MultiPolygon

class LayerStore:
    def __init__(self, cell: Cell):
        self._layers = {}

        for p  in cell.polygons:
            key = (p.layer, p.datatype)
            self._layers.setdefault(key, []).append(p.points)

    def get(self, layer, datatype = 0):
        return self._layers.get((layer, datatype), [])

    