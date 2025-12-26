from pathlib import Path
from util.config import load_tech_configs, load_user_config
from util.print import print_bounding_box
from pipeline.builder import build_shapes
from pipeline.boolean2d import apply_2d_booleans
from pipeline.zresolver import resolve_z_ranges
from geometry3d.solid import Solid3D
from pipeline.scene_builder import SceneBuilder
from geometry3d.display import show_scene
from gds.gds_loader import GDSHandler
from layers.store import LayerStore
from util.ui import console

import argparse


def main():

    parser = argparse.ArgumentParser(description="GDS to 3D Model Converter")
    parser.add_argument('gds', type=str, help='Path to the GDS file to load')
    parser.add_argument('--config', type=str, help='Path to the user configuration', default='config', required=False)
    parser.add_argument('--tech', type=str, help='Path to the technology configuration', required=True)
    parser.add_argument('--cut', type=float, nargs=4, help='Rectangle to cut the cell (xmin, ymin, xmax, ymax)', default=None, required=False)
    parser.add_argument('-o', '--output', type=str, help='Output file for the 3D model', required=False)
    parser.add_argument('--no-show', action='store_true', help='Do not display the 3D model', required=False)

    args = parser.parse_args()

    gdsfile = args.gds
    if not Path(gdsfile).exists():
        console.print(f"GDS file {gdsfile} does not exist.", style="red")
        return
    userconfig = Path(args.config)
    if not userconfig.exists():
        console.print(f"User config file {userconfig} does not exist. Using default config.", style="yellow")
        userconfig = None
    techconfig = Path(args.tech)
    if not techconfig.exists():
        console.print(f"Tech config path {techconfig} does not exist.", style="red")
        return

    console.rule("[bold red]Running GDS23D")
    
    # Load configs
    tech_cfg = load_tech_configs(techconfig)
    user_cfg  = load_user_config(userconfig)

    gdshandler = GDSHandler()
    gdshandler.load(gdsfile)
    gdshandler.flatten()


    cell = gdshandler.get_cell()
    if cell is None:
        console.print("No cell found in GDS file.", style="red")
        return
    
    bounds = cell.bounding_box()
    if bounds is None:
        return
    (xmin, ymin), (xmax, ymax) = bounds

    print_bounding_box((xmin, ymin, xmax, ymax), cut=args.cut)

    
    
    console.print(f"Cell '{cell.name}' loaded with {gdshandler.polygon_count} polygons, {gdshandler.path_count} paths, and {gdshandler.reference_count} references.", style="green")
    store = LayerStore(cell)

    if args.cut is not None:
        xmin, ymin, xmax, ymax = args.cut
        console.print(f"Cutting cell with rectangle: ({xmin}, {ymin}) - ({xmax}, {ymax})")
        store.cut_with_rectangle(xmin, ymin, xmax, ymax)
        console.print("Cell cut completed.", style="green")


    # --- 2D build ---
    shapes = build_shapes(store, tech_cfg["layers"])
    apply_2d_booleans(shapes, tech_cfg["tech"])

    # --- Resolve Z ---
    z_ranges = resolve_z_ranges(shapes, user_cfg, tech_cfg["tech"])

    # --- Build Solid3D objects ---
    solids = {}
    for name, shape in shapes.items():
        z0, z1 = z_ranges[name]
        height = z1 - z0
        solids[name] = Solid3D(shape, height, name=name)

    # --- Assemble Scene ---
    builder = SceneBuilder(solids, z_ranges, tech_cfg["tech"], user_cfg)
    scene = builder.assemble()
    if not args.no_show:
        show_scene(scene)
    scene = builder.combine_scene(scene)

    if args.output:
        scene = builder.prepare_for_print(scene)
        scene.export(args.output)
        return
    # --- Show Scene ---

if __name__ == "__main__":
    main()
