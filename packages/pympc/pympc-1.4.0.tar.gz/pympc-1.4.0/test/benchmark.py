from pympc import pympc

ceres_result = pympc.minor_planet_check(61.78375, 945, 59640.0, 5, "/tmp/mpcorb_xephem.csv", chunk_size=0)
print(ceres_result)