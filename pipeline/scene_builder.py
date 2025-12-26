import trimesh

class SceneBuilder:
    def __init__(self, solids, z_ranges, rules_cfg, user_cfg):
        """
        solids    : dict[name -> Solid3D]
        z_ranges  : dict[name -> (z0, z1)]
        rules_cfg : rules.json
        user_cfg  : user.json
        """
        self.solids = solids
        self.z_ranges = z_ranges
        self.rules_cfg = rules_cfg
        self.user_cfg = user_cfg
        self.__hue = 0.0
        self.__golden_ratio = 0.618033988749895

    def assemble(self):
        """
        Returns a single trimesh.Scene with all solids placed and cut correctly
        """
        scene = trimesh.Scene()
        built_meshes: dict[str, trimesh.Trimesh] = {}

        # Build all solids at origin
        for name, solid in self.solids.items():
            solid.build()
            built_meshes[name] = solid.mesh.copy()

        # Apply Z translations
        for name, mesh in built_meshes.items():
            z0, z1 = self.z_ranges[name]
            # print(f"Placing {name} at z={z0} to z={z1}")
            mesh.apply_translation([0, 0, z0])
            built_meshes[name] = mesh

        # Apply boolean subtractions
        for target, cutters in self.rules_cfg.get("extend_down_to", {}).items():
            if target not in built_meshes:
                continue
            target_mesh = built_meshes[target]
            for cutter_name in cutters:
                if cutter_name in built_meshes:
                    cutter_mesh = built_meshes[cutter_name]
                    try:
                        target_mesh = target_mesh.difference(cutter_mesh, engine="manifold")
                    except Exception as e:
                        print(f"[WARN] Boolean failed: {target} - {cutter_name}: {e}")
            built_meshes[target] = target_mesh

        # Add meshes to scene with colors
        for name, mesh in built_meshes.items():
            color = (
                self.user_cfg.get("layers", {}).get(name, {}).get("color")
            )
            if color is not None:
                mesh.visual.face_colors = color
            else:
                rgb = self.next_rgb()
                rgb = tuple(int(c * 255) for c in rgb)
                # print(f"Assigning color {rgb} to layer {name}")
                mesh.visual = trimesh.visual.ColorVisuals(
                    mesh,
                    face_colors=list(rgb) + [200]
                )
            scene.add_geometry(mesh, node_name=name)

        return scene
    
    def combine_scene(self, scene: trimesh.Scene) -> trimesh.Trimesh:
        meshes = []

        for geom in scene.geometry.values():
            if not isinstance(geom, trimesh.Trimesh):
                continue

            mesh = trimesh.Trimesh(
                vertices=geom.vertices.copy(),
                faces=geom.faces.copy(),
                process=False
            )
            meshes.append(mesh)

        return trimesh.util.concatenate(meshes)



    
    def prepare_for_print(self, scene: trimesh.Trimesh) -> trimesh.Trimesh:
        # scene.remove_duplicate_faces()
        # scene.remove_degenerate_faces()
        scene.fill_holes()
        scene.remove_unreferenced_vertices()
        scene.rezero()

        # Optional but recommended
        scene.merge_vertices()
        # print("Watertight:", scene.is_watertight)
        return scene

    
    def next_rgb(self):
        self.__hue = (self.__hue + self.__golden_ratio) % 1.0
        return self.hsv_to_rgb(self.__hue, 0.7, 0.95)

    @staticmethod
    def hsv_to_rgb(h, s, v):
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        i %= 6

        return {
            0: (v, t, p),
            1: (q, v, p),
            2: (p, v, t),
            3: (p, q, v),
            4: (t, p, v),
            5: (v, p, q),
        }[i]