from geometry2d.shape import Shape2D

def resolve_z_ranges(shapes: dict[str, Shape2D], user_cfg, rules_cfg):
    """
    Returns dict[name -> [z0, z1]] for all layers.
    Layers are placed either at the same z0 as ancestors (subtract relationship)
    or stacked incrementally.
    """
    default_z0 = user_cfg.get("default_z_start", 0)
    z_ranges = {}

    subtract_cfg = rules_cfg.get("subtract", {})

    # Build reverse map for transitive lookup
    reverse_subtract_cfg = {}
    for parent, children in subtract_cfg.items():
        for child in children:
            reverse_subtract_cfg.setdefault(child, []).append(parent)

    def transitive_up(reverse_map, start):
        seen = set()
        stack = [start]
        while stack:
            node = stack.pop()
            for parent in reverse_map.get(node, []):
                if parent not in seen:
                    seen.add(parent)
                    stack.append(parent)
        return seen

    # Process layers in any order, handle transitive z0 inheritance
    for name in shapes.keys():
        layer_cfg = user_cfg.get("layers", {}).get(name, {})
        height = layer_cfg.get("height", 0.5)

        # Determine z0: if any ancestor has already z_ranges, use min(z0)
        ancestors = transitive_up(reverse_subtract_cfg, name)
        ancestor_z0s = [z_ranges[a][0] for a in ancestors if a in z_ranges]
        if ancestor_z0s:
            z0 = min(ancestor_z0s)
        else:
            # Stack incrementally from last used z0
            z0 = max([z1 for z0_, z1 in z_ranges.values()], default=default_z0)

        z1 = z0 + height
        z_ranges[name] = [z0, z1]

    # Apply extend_down_to
    for name, targets in rules_cfg.get("extend_down_to", {}).items():
        if name not in z_ranges:
            continue
        target_z1s = [z_ranges[t][1] for t in targets if t in z_ranges]
        if target_z1s:
            z_ranges[name][0] = min(target_z1s)

    return z_ranges
