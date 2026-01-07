import numpy as np
from pathlib import Path
from MOMP.params.region_def import polygon_boundary


#def polygon_boundary(da):
#
#    orig_lat = da.lat.values
#    orig_lon = da.lon.values
#
#    lat_diff = abs(orig_lat[1]-orig_lat[0])
#    if abs(lat_diff - 2.0) < 0.1:  # 2-degree resolution
#        polygon1_lon = np.array([83, 75, 75, 71, 71, 77, 77, 79, 79, 83, 83, 89, 89, 85, 85, 83, 83])
#        polygon1_lat = np.array([17, 17, 21, 21, 29, 29, 27, 27, 25, 25, 23, 23, 21, 21, 19, 19, 17])
#        print("Using 2-degree CMZ polygon coordinates")
#    elif abs(lat_diff - 4.0) < 0.1:  # 4-degree resolution
#        polygon1_lon = np.array([86, 74, 74, 70, 70, 82, 82, 86, 86])
#        polygon1_lat = np.array([18, 18, 22, 22, 30, 30, 26, 26, 18])
#        print("Using 4-degree CMZ polygon coordinates")
#    elif abs(lat_diff - 1.0) < 0.1:  # 1-degree resolution
#        polygon1_lon = np.array([74, 85, 85, 86, 86, 87, 87, 88, 88, 88, 85, 85, 82, 82, 79, 79, 78, 78, 69, 69, 74, 74])
#        polygon1_lat = np.array([18, 18, 19, 19, 20, 20, 21, 21, 21, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 21, 21, 18])
#        print("Using 1-degree CMZ polygon coordinates")
#
#    return polygon1_lat, polygon1_lon



# Function to find grid points inside a polygon (For core-monsoon zone analysis)
def points_inside_polygon(polygon_lon, polygon_lat, grid_lons, grid_lats):
    """
    Find grid points that are inside a polygon.

    Parameters:
    polygon_lon: array of polygon longitude vertices
    polygon_lat: array of polygon latitude vertices
    grid_lons: array of grid longitude points
    grid_lats: array of grid latitude points

    Returns:
    inside_mask: boolean array indicating which points are inside
    inside_lons: longitude coordinates of points inside polygon
    inside_lats: latitude coordinates of points inside polygon
    """

    # Create polygon path
    polygon_vertices = np.column_stack((polygon_lon, polygon_lat))
    polygon_path = Path(polygon_vertices)

    # Create meshgrid if needed
    if grid_lons.ndim == 1 and grid_lats.ndim == 1:
        lon_grid, lat_grid = np.meshgrid(grid_lons, grid_lats)
    else:
        lon_grid, lat_grid = grid_lons, grid_lats

    # Flatten the grids to test each point
    points = np.column_stack((lon_grid.ravel(), lat_grid.ravel()))

    # Test which points are inside the polygon
    inside_mask = polygon_path.contains_points(points)
    inside_mask = inside_mask.reshape(lon_grid.shape)

    # Get coordinates of points inside polygon
    inside_lons = lon_grid[inside_mask]
    inside_lats = lat_grid[inside_mask]

    return inside_mask, inside_lons, inside_lats



def polygon_mask(da_ref, da_model):
    """mask data based on polygon boundary"""
    orig_lat = da_ref.lat.values
    orig_lon = da_ref.lon.values
    polygon1_lat, polygon1_lon = polygon_boundary(da_ref)

    inside_mask, inside_lons, inside_lats = points_inside_polygon(polygon1_lon, polygon1_lat, orig_lon, orig_lat)

    da_model_slice = da_model.sel(lat=inside_lats, lon=inside_lons)

    return da_model_slice



def get_india_outline(shpfile_path):
    """
    Get India outline coordinates from shapefile.
    """
    import geopandas as gpd
    # Update this path to your India shapefile
    india_gdf = gpd.read_file(shpfile_path)

    boundaries = []
    for geom in india_gdf.geometry:
        if hasattr(geom, 'exterior'):
            coords = list(geom.exterior.coords)
            lon_coords = [coord[0] for coord in coords]
            lat_coords = [coord[1] for coord in coords]
            boundaries.append((lon_coords, lat_coords))
        elif hasattr(geom, 'geoms'):
            for sub_geom in geom.geoms:
                if hasattr(sub_geom, 'exterior'):
                    coords = list(sub_geom.exterior.coords)
                    lon_coords = [coord[0] for coord in coords]
                    lat_coords = [coord[1] for coord in coords]
                    boundaries.append((lon_coords, lat_coords))
    return boundaries

