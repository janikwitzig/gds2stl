import argparse
import json
from gds_loader import GDSLoader
from scene_builder import SceneBuilder

def main():
    parser = argparse.ArgumentParser(description="Render 3D view of a GDS file")
    parser.add_argument("gds_file", type=str, help="Path to GDS file", default="na2i1hdx0.gds")
    parser.add_argument("--config", type=str, default="xt018.json",
                        help="Path to JSON layer config")
    args = parser.parse_args()

    # Load layer config
    with open(args.config) as f:
        print("Loading layer config from", args.config)
        layer_config = json.load(f)

    # Load GDS
    loader = GDSLoader()
    cell = loader.load_gds(args.gds_file)
    layer_polygons = loader.extract_polygons(cell)

    # Build scene
    builder = SceneBuilder(layer_config)
    scene = builder.build_scene(layer_polygons)

    # Show scene
    scene.show(viewer="gl")  # pyglet<2

if __name__ == "__main__":
    main()
