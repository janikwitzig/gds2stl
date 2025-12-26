from geometry2d.shape import Shape2D

def apply_2d_booleans(shapes: dict[str, Shape2D], tech_cfg):
    for target, cutters in tech_cfg.get("subtract", {}).items():
        if target not in shapes:
            continue
        for cutter in cutters:
            if cutter in shapes:
                shapes[target].subtract(shapes[cutter])
