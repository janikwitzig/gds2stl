import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union
from layers.store import LayerStore
import copy
from rich.status import Status
from rich.progress import Progress
from util.ui import console

class Shape2D:
    def __init__(self, geom=None, name=None):
        self.geom: Polygon | None = geom
        self.name = name or "Shape2D"

    @classmethod
    def from_layers(cls, store: LayerStore, layers, name=None):
        polys = []
        for layer, datatypes in layers:
            if isinstance(datatypes, int):
                datatypes = [datatypes]
            for dt in datatypes:
                for pts in store.get(layer, dt):
                    poly = Polygon(pts)
                    if not poly.is_valid:

                        poly = poly.buffer(0)
                    if not poly.is_empty:
                        polys.append(poly)

        

        return cls(unary_union(polys), name)

    def union(self, other: Shape2D):
        self.geom = self.geom.union(other.geom)
        return self

    def subtract(self, other: Shape2D, tol = None):
        if tol is not None:
            other = copy.deepcopy(other)
            other.buffer(tol)
        self.geom = self.geom.difference(other.geom)
        return self

    def buffer(self, tol: float):

        self.geom = self.geom.buffer(tol, join_style=2)
        return self

    def show(self, ax=None, color="C0"):
        if ax is None:
            fig, ax = plt.subplots()

        geom = self.geom
        polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]

        for poly in polys:
            x, y = poly.exterior.xy
            ax.fill(x, y, alpha=0.6, color=color)
            for hole in poly.interiors:
                hx, hy = hole.xy
                ax.fill(hx, hy, color="white")

        ax.set_aspect("equal")
        ax.set_title(self.name)
        plt.show()
