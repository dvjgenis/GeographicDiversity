# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/utils.py

from haversine import haversine, Unit

def calculate_distance(location1, location2, coord_dict):
    coord1 = coord_dict[location1]
    coord2 = coord_dict[location2]
    distance = haversine(coord1, coord2, unit=Unit.MILES)
    return distance