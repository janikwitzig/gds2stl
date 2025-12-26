import matplotlib.pyplot as plt

def show_shape2d(shape, color=None, ax=None):
    """
    shape: Shape2D instance
    color: RGBA or matplotlib color
    """
    if ax is None:
        fig, ax = plt.subplots()

    geom = shape.geom
    if geom is None or geom.is_empty:
        return

    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]

    for poly in polys:
        x, y = poly.exterior.xy
        ax.fill(x, y, color=color, alpha=0.6)
        for hole in poly.interiors:
            hx, hy = hole.xy
            ax.fill(hx, hy, color="white")

    ax.set_aspect("equal")
    ax.set_title(shape.name)
    plt.show()
