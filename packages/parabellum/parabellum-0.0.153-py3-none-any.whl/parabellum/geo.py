# %%
# import contextily as ctx
import geopandas as gpd

# import jax.numpy as jnp
# import matplotlib.pyplot as plt
# import numpy as np
from cachier import cachier
import osmnx as ox
from geopy.geocoders import Nominatim
from rasterio import features, transform
from shapely.geometry import Point, box


@cachier()
def geometry_fn(place, radius):
    # get center
    geolocator = Nominatim(user_agent="geo_building_mask")
    loc = geolocator.geocode(place)
    lon, lat = loc.longitude, loc.latitude

    # get square
    pt_wgs = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs="EPSG:4326").to_crs("EPSG:3857")
    cx, cy = pt_wgs.geometry.iloc[0].x, pt_wgs.geometry.iloc[0].y
    aoi_utm = gpd.GeoSeries(box(cx - radius, cy - radius, cx + radius, cy + radius), crs=pt_wgs.crs)

    # get content
    aoi_wgs = aoi_utm.to_crs("EPSG:4326").iloc[0]
    buildings = ox.features_from_polygon(aoi_wgs, tags={"building": True})

    # filter
    buildings_utm = buildings.to_crs(aoi_utm.crs)
    buildings_utm = buildings_utm[buildings_utm.geometry.area > 0]

    # crop
    minx, miny, maxx, maxy = aoi_utm.total_bounds
    width = height = 2 * radius  # pixel size = 1 meter
    aff = transform.from_bounds(minx, miny, maxx, maxy, width, height)

    # rasterize
    shapes = ((geom, 1) for geom in buildings_utm.geometry if geom is not None and not geom.is_empty)
    mask = features.rasterize(shapes=shapes, out_shape=(height, width), transform=aff, fill=0, all_touched=True)

    return mask


# %%
# plt.imshow(geometry_fn("Thun, Switzerland", 256))
