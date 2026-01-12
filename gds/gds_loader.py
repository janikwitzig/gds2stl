from shapely.geometry import box, Polygon, MultiPolygon
from gdstk import Cell
import gdstk
import numpy as np
from rich.status import Status
from rich.progress import Progress
from util.ui import console

type Cell = gdstk.Cell
class GDSHandler:

    def load(self, filename) -> Cell:
        with Status(f"Loading GDS file {filename}...", console=console) as status:
            lib = gdstk.read_gds(filename)
            top_level = lib.top_level()
            if not top_level:
                status.update("No top-level cells found", spinner="dots12")
                raise RuntimeError("No top-level cells found")
            cell = top_level[0]
            console.print(lib.layers_and_datatypes())
        console.print(f"Loaded GDS file {filename}")

        if type(cell) is not gdstk.Cell:
            raise RuntimeError("No valid cell found in GDS file")
        
        return cell
        
    def flatten(self, cell: Cell) -> Cell:
        with Status("Flattening cell...", console=console) as status:

            flattened_cell = cell.flatten()

            new_cell = gdstk.Cell(f"{cell.name}")
            for poly in flattened_cell.polygons:
                new_cell.add(
                    poly
                )
            for path in flattened_cell.paths:
                path_polys = path.to_polygons()
                for p in path_polys:
                    new_cell.add(
                        gdstk.Polygon(
                            points=p.points,
                            layer=p.layer,
                            datatype=p.datatype,
                        )
                    )

        console.print("Cell flattened")
        return new_cell

    def cut_cell_with_rectangle(self, cell: Cell, xmin: float, ymin: float, xmax: float, ymax: float) -> Cell:
        with Status("Cutting cell with rectangle...", console=console) as status:
            if len(cell.paths) > 0 or len(cell.references) > 0:
                console.print("Cell must be flattened before cutting. Flattening now...", style="yellow")
                self.flatten(cell)

            status.update('Slicing along x-axis...')
            cell_polys = cell.polygons
            columns_polys = gdstk.slice(cell_polys, axis="x", position=[xmin, xmax])
            mid_col_polys = columns_polys[1]

            status.update('Slicing along y-axis...')
            rows_polys = gdstk.slice(mid_col_polys, axis="y", position=[ymin, ymax])
            mid_cell_polys = rows_polys[1]

            new_cell = gdstk.Cell(f"{cell.name}_cut")
            new_cell.add(*mid_cell_polys)
            return new_cell
        console.print("Cutting done")


    def __calculate_slice_positions(self, num_cuts: int, span: float) -> list[float]:
        """
        Calculate slice positions along one axis.
        
        Args:
            num_cuts: Number of cuts to make
            span: Total span along the axis
        
        Returns:
            List of slice positions
        """
        step = span / (num_cuts + 1)
        return [(i + 1) * step for i in range(num_cuts)]