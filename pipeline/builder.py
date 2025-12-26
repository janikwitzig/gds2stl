from geometry2d.shape import Shape2D
from layers.store import LayerStore
from rich.progress import Progress
from util.ui import console

def build_shapes(store: LayerStore, layers_cfg) -> dict[str, Shape2D]:
    """
    store      : LayerStore
    layers_cfg : tech/layers.json

    returns dict[name -> Shape2D]
    """
    shapes = {}

    with Progress(console=console) as progress:
        task = progress.add_task("Building shapes...", total=len(layers_cfg))
        for name, spec in layers_cfg.items():
            progress.update(task, advance=1)
            layer = spec["layer"]
            datatype = spec.get("datatype")

            shapes[name] = Shape2D.from_layers(
                store,
                layers=[(layer, datatype)],
                name=name
            )

    return shapes
