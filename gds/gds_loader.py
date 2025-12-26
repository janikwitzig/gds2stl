from shapely.geometry import box, Polygon, MultiPolygon
from gdstk import Cell
import gdstk
import numpy as np
from rich.status import Status
from rich.progress import Progress
from util.ui import console

class GDSHandler:
    def __init__(self, scale=1.0):
        self.__scale = scale
        self.__cell = None
        self.__n_polygons = None

    def load(self, filename):
        with Status(f"Loading GDS file {filename}...", console=console) as status:
            lib = gdstk.read_gds(filename)
            top_level = lib.top_level()
            if not top_level:
                status.update("No top-level cells found", spinner="dots12")
                raise RuntimeError("No top-level cells found")
            cell = top_level[0]
            self.__cell = cell
        console.print(f"Loaded GDS file {filename}")

    def scale(self, factor: float):
        with Status(f"Scaling cell by factor {factor}...", console=console) as status:
            cell = self.__cell
            if cell is None or type(cell) is not gdstk.Cell:
                status.update("No cell loaded", spinner="dots12")
                return
            for poly in cell.polygons:
                for point in poly.points:
                    point = (point[0] * factor, point[1] * factor)
            self.__cell = cell
        

    def flatten(self):
        with Status("Flattening cell...", console=console) as status:
            cell = self.__cell
            if cell is None or type(cell) is not gdstk.Cell:
                status.update("No cell loaded", spinner="dots12")
                return
            self.__cell = cell.flatten()
        console.print("Cell flattened")

    @property
    def name(self):
        if self.__cell is None:
            return ""
        return self.__cell.name

    @property
    def polygon_count(self):
        if self.__cell is None or type(self.__cell) is not gdstk.Cell:
            return 0
        if self.__n_polygons is None:
            self.__n_polygons = len(self.__cell.polygons)
        return self.__n_polygons
    
    @property
    def reference_count(self):
        if self.__cell is None or type(self.__cell) is not gdstk.Cell:
            return 0
        return len(self.__cell.references)
    
    @property
    def path_count(self):
        if self.__cell is None or type(self.__cell) is not gdstk.Cell:
            return 0
        return len(self.__cell.paths)




    def cut_cell_with_rectangle(self, xmin, ymin, xmax, ymax):
        if self.__cell is None or type(self.__cell) is not gdstk.Cell:
            console.print("No cell loaded", style="red")
            return
        clip = box(xmin, ymin, xmax, ymax)
        new_cell = gdstk.Cell(f"{self.__cell.name}")

        n_polygons = len(self.__cell.polygons)
        console.print(f"Cutting {n_polygons} polygons...", style="blue")
        with Progress(console=console) as progress:
            task = progress.add_task("Cutting...", total=len(self.__cell.polygons))

            for poly in self.__cell.polygons:
                progress.update(task, advance=1)
                shp = Polygon(poly.points)
                clipped = shp.intersection(clip)

                if clipped.is_empty:
                    continue

                if isinstance(clipped, Polygon):
                    polys = [clipped]
                elif isinstance(clipped, MultiPolygon):
                    polys = clipped.geoms
                else:
                    continue

                for p in polys:
                    coords = p.exterior.coords
                    coords_sequence: list[tuple[float, float]] = [(float(c[0]), float(c[1])) for c in coords]
                    
                    new_cell.add(
                        gdstk.Polygon(
                            points=coords_sequence,
                            layer=poly.layer,
                            datatype=poly.datatype,
                        )
                    )

        self.__cell = new_cell
        console.print("Cutting done")
    
    def get_cell(self) -> Cell | None:
        if self.__cell is None or type(self.__cell) is not gdstk.Cell:
            console.print("No cell loaded", style="red")
            return None

        return self.__cell
    
    def save_as_svg(self, cell: gdstk.Cell, filename: str):
        with Status(f"Saving cell as SVG to {filename}...", console=console) as status:
            cell.write_svg(filename)

        console.print(f"Saved SVG to {filename}")