from util.ui import console

type BoundingBox = tuple[float, float, float, float]

def print_bounding_box(box : BoundingBox, cut: BoundingBox | None = None):
    xmin, ymin, xmax, ymax = box
    if xmin is None or ymin is None or xmax is None or ymax is None:
        return

    # Print bounding box as ASCII art
    width = xmax - xmin
    height = ymax - ymin
    
    # Scale for ASCII (target ~60 chars width, adjust height proportionally)
    max_width_chars = 60
    max_height_chars = 30
    
    if width > 0 and height > 0:
        aspect_ratio = height / width
        
        # Adjust for character aspect ratio (chars are ~2x taller than wide)
        char_aspect = 2.0
        
        box_width = min(max_width_chars, int(max_height_chars / (aspect_ratio / char_aspect)))
        box_height = int(box_width * aspect_ratio / char_aspect)
        
        # Ensure minimum size
        box_width = max(10, box_width)
        box_height = max(3, box_height)
        
        # Format dimensions
        width_str = f"{width:.2f}"
        height_str = f"{height:.2f}"
        
        # Helper function to map world coordinates to grid coordinates
        def world_to_grid(x, y):
            grid_x = int((x - xmin) / width * box_width)
            grid_y = int((ymax - y) / height * box_height)  # Flip Y for display
            return grid_x, grid_y
        
        # Create a 2D grid for the ASCII art (just spaces, the border is added separately)
        grid = [[' ' for _ in range(box_width)] for _ in range(box_height)]
        
        # Draw the cut rectangle if specified
        cut_cells = set()
        if cut is not None:
            cut_xmin, cut_ymin, cut_xmax, cut_ymax = cut
            
            # Calculate cut boundaries in grid coordinates
            cut_x0, cut_y1 = world_to_grid(cut_xmin, cut_ymin)
            cut_x1, cut_y0 = world_to_grid(cut_xmax, cut_ymax)
            
            # Clamp to grid boundaries for drawing
            cut_x0_clamped = max(0, min(box_width - 1, cut_x0))
            cut_x1_clamped = max(0, min(box_width - 1, cut_x1))
            cut_y0_clamped = max(0, min(box_height - 1, cut_y0))
            cut_y1_clamped = max(0, min(box_height - 1, cut_y1))
            
            # Draw cut borders
            for x in range(cut_x0_clamped, cut_x1_clamped + 1):
                if 0 <= cut_y0 < box_height:
                    grid[cut_y0][x] = '='
                    cut_cells.add((cut_y0, x))
                if 0 <= cut_y1 < box_height:
                    grid[cut_y1][x] = '='
                    cut_cells.add((cut_y1, x))
            
            for y in range(cut_y0_clamped, cut_y1_clamped + 1):
                if 0 <= cut_x0 < box_width:
                    grid[y][cut_x0] = '‖'
                    cut_cells.add((y, cut_x0))
                if 0 <= cut_x1 < box_width:
                    grid[y][cut_x1] = '‖'
                    cut_cells.add((y, cut_x1))
            
            # Draw corners
            if 0 <= cut_y0 < box_height and 0 <= cut_x0 < box_width:
                grid[cut_y0][cut_x0] = '╔'
                cut_cells.add((cut_y0, cut_x0))
            if 0 <= cut_y0 < box_height and 0 <= cut_x1 < box_width:
                grid[cut_y0][cut_x1] = '╗'
                cut_cells.add((cut_y0, cut_x1))
            if 0 <= cut_y1 < box_height and 0 <= cut_x0 < box_width:
                grid[cut_y1][cut_x0] = '╚'
                cut_cells.add((cut_y1, cut_x0))
            if 0 <= cut_y1 < box_height and 0 <= cut_x1 < box_width:
                grid[cut_y1][cut_x1] = '╝'
                cut_cells.add((cut_y1, cut_x1))
        
        # Print width on top
        console.print(f"  {width_str:^{box_width}}")
        
        # Top border
        console.print("+" + "-" * box_width + "+")
        
        # Print grid with height label
        for i in range(box_height):
            line = '|'
            for j in range(box_width):
                char = grid[i][j]
                if (i, j) in cut_cells:
                    line += f"[red]{char}[/red]"
                else:
                    line += char
            line += '|'
            
            if i == box_height // 2:
                line += f" {height_str}"
            
            console.print(line, highlight=False)
        
        # Bottom border
        console.print("+" + "-" * box_width + "+")
        console.print()