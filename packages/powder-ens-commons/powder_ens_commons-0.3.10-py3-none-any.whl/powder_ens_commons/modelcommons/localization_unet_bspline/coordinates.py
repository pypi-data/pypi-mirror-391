import numpy as np
from utm import from_latlon


CAMPUS_POLYGON = np.array([
[40.75833665000094,-111.8394345921071],
[40.75766986565535,-111.8370482437152],
[40.75705769188596,-111.8359381518518],
[40.76245626062813,-111.8282855297867],
[40.76459575636777,-111.8286592166043],
[40.76641466547591,-111.826331587571 ], 
[40.77359472666938,-111.8332758813709],
[40.77480702773148,-111.835519504827 ], 
[40.77445294405955,-111.8403812582976],
[40.77122030026813,-111.8480792084893],
[40.76727460060798,-111.8490369825005],
[40.76732632624882,-111.8527037831718],
[40.75825492988778,-111.8527317126743],
[40.75833665000094,-111.8394345921071],
])

CAMPUS_LATLON = np.array([
    (40.75413,
    -111.85390),
    (40.77500,
    -111.82632),
])

DENSE_LATLON = np.array([
    (40.761023, -111.848101),
    (40.773322, -111.831527),
])

ANTWERP_LATLON = np.array([
    (51.178,4.37),
    (51.250,4.45),
])
antwerp_center_point = np.array([6500,3500])

def convert_gps_to_utm(gps_coordinates, origin_to_subtract=None):
    if isinstance(gps_coordinates, (np.ndarray, np.generic)):
        lat = gps_coordinates[:,0]
        lon = gps_coordinates[:,1]
    else:
        lat, lon = gps_coordinates
    x,y,_,_ = from_latlon(lat, lon)
    if origin_to_subtract is not None:
        x -= origin_to_subtract[0]
        y -= origin_to_subtract[1]
    return np.vstack((x, y)).T