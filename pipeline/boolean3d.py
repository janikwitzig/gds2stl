def apply_3d_booleans(solids, rules_cfg):
    for target, cutters in rules_cfg.get("subtract", {}).items():
        if target not in solids:
            continue
        for cutter in cutters:
            if cutter in solids:
                solids[target].subtract(solids[cutter])
