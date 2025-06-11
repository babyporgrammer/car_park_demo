from math import radians, cos, sin, asin, sqrt

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    计算两个经纬度坐标之间的距离（单位：公里）
    """
    R = 6371  # 地球半径（单位：km）
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c
