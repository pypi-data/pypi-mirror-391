from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import numpy as np
from typing import List, Tuple
from shapely import wkt

def slice_polygon_to_grid(
    wkt_polygon: str,
    grid_size: float,
    bbox: Tuple[float, float, float, float] = None
) -> List[str]:
    """
    Slice a large polygon into smaller pieces that fit a regular grid.

    Args:
        wkt_polygon (str): The well-known text representation of the polygon to be sliced.
        grid_size (float): The grid cell size (in same units as polygon coordinates).
        bbox (tuple, optional): (minx, miny, maxx, maxy) to constrain the grid.
            If not provided, the polygon's bounding box is used.

    Returns:
        List[str]: List of wkt polygon strings  (each is the intersection of the polygon and one grid cell).
    """
    
    polygon = wkt.loads(wkt_polygon)
    
    if bbox is None:
        minx, miny, maxx, maxy = polygon.bounds
    else:
        minx, miny, maxx, maxy = bbox

    # Create grid coordinates
    x_coords = np.arange(minx, maxx, grid_size)
    y_coords = np.arange(miny, maxy, grid_size)

    pieces = []
    for x in x_coords:
        for y in y_coords:
            cell = box(x, y, x + grid_size, y + grid_size)
            intersection = polygon.intersection(cell)
            if not intersection.is_empty:
                # Handle MultiPolygons (split into individual polygons)
                if intersection.geom_type == "Polygon":
                    pieces.append(intersection)
                elif intersection.geom_type == "MultiPolygon":
                    pieces.extend(intersection.geoms)

    return [wkt.dumps(p) for p in pieces]