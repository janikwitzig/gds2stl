import trimesh
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon
import numpy as np

class SceneBuilder:
    def __init__(self, layer_config, extrusion_height=0.5):
        self.layer_config = layer_config
        self.extrusion_height_default = extrusion_height

    @staticmethod
    def flatten_polygons(polygons):
        merged = unary_union(polygons)
        if merged.is_empty:
            return []
        if isinstance(merged, Polygon):
            return [merged]
        if isinstance(merged, MultiPolygon):
            return list(merged.geoms)
        return []

    def build_scene(self, layer_polygons):
        layer_meshes = {}
        last_z_top = 0.0

        layer_tops = {}

        for layer in self.layer_config.values():
            z_start = layer.get("z_start", None)
            if z_start is None:
                layer["z_start"] = None

        sorted_layers = self.layer_config.items()
        # Layers sorted by explicit z_start if present, otherwise by key
        # sorted_layers = sorted(
        #     self.layer_config.items(),
        #     key=lambda x: (x[1]["z_start"] if x[1]["z_start"] is not None else float('inf'))
        # )

        for key, cfg in sorted_layers:
            # print("Processing layer", key)
            layer_name = cfg["name"]
            polys = layer_polygons.get((int(key), cfg.get("datatype", 0)), [])

            # TODO: this should be post-processing for export
            # Combine with other layers if specified
            # for combine_key in cfg.get("combine_with", []):
            #     polys.extend(layer_polygons.get((combine_key, 0), []))

            # Flatten and union
            flat_polys = self.flatten_polygons(polys)
            if not flat_polys:
                continue

            # Subtract layers if specified
            subtract_keys = cfg.get("subtract", [])
            if subtract_keys:
                subtract_polys = []
                for s in subtract_keys:
                    subtract_polys.extend(layer_polygons.get((s, 0), []))
                if subtract_polys:
                    subtract_union = unary_union(subtract_polys)
                    flat_polys = [p.difference(subtract_union) for p in flat_polys]

            meshes = []

            # Determine Z start
            z_start = cfg.get("z_start")
            if z_start is None:
                z_start = last_z_top

            # Determine height
            height = cfg.get("height")
            if height is None:
                height = self.extrusion_height_default

            # Handle extrude_down_to
            extrude_down_layers = cfg.get("extrude_down_to", [])
            down_union = None
            down_layer_nos = []
            down_layers = {}
            if extrude_down_layers:
                down_polys = []
                for l in extrude_down_layers:
                    down_layer_nos.append(l)
                    down_layers[l] = unary_union(layer_polygons.get((l, 0), []))
                    down_polys.extend(layer_polygons.get((l, 0), []))
                if down_polys:
                    down_union = unary_union(down_polys)

            n_polys = len(flat_polys)
            for i, poly in enumerate(flat_polys):
                # print(f"  Extruding polygon {i+1}/{n_polys}")

                if poly.is_empty:
                    continue

                # Ensure single polygon
                polys_to_extrude = []
                if isinstance(poly, Polygon):
                    polys_to_extrude = [poly]
                elif isinstance(poly, MultiPolygon):
                    polys_to_extrude = list(poly.geoms)

                for single_poly in polys_to_extrude:
                    extrude_height = height
                    z_low = z_start


                    if down_union:
                        # Intersection in XY with extrude-down layers
                        intersection = single_poly.intersection(down_union)
                        if intersection.is_empty:
                            continue
                        for l in down_layer_nos:
                            if single_poly.intersects(down_layers[l]):
                                extrude_height += z_start - layer_tops[l]
                                z_low = layer_tops[l]

                        if isinstance(intersection, Polygon):
                            single_poly = intersection
                        elif isinstance(intersection, MultiPolygon):
                            polys_to_process = list(intersection.geoms)
                        else:
                            continue


                    mesh = trimesh.creation.extrude_polygon(single_poly, height=extrude_height, engine="earcut")
                    mesh.apply_translation([0, 0, z_low])
                    layer_tops[int(key)] = z_low + extrude_height

                    color = cfg.get("color", [200, 200, 200, 100])
                    mesh.visual.face_colors = np.array(color, dtype=np.uint8)
                    meshes.append(mesh)

            if meshes:
                layer_meshes[layer_name] = trimesh.util.concatenate(meshes)
                last_z_top = z_start + height

        # Build scene
        scene = trimesh.Scene()
        for name, mesh in layer_meshes.items():
            scene.add_geometry(mesh, node_name=name)

        return scene
