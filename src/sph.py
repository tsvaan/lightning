import math

a_e = 6371.0

def spherToCart(lat, lon):
    x = math.cos(lat) * math.cos(lon)
    y = math.cos(lat) * math.sin(lon)
    z = math.sin(lat)
    return (x, y, z)

def cartToSpher(x, y, z):
    lat = math.atan2(z, math.sqrt(x * x + y * y))
    lon = math.atan2(y, x)
    return (lat, lon)

def rotate(x, y, a):
    c = math.cos(a)
    s = math.sin(a)
    u = x * c + y * s
    v = -x * s + y * c
    return (u, v)

def inverse(lat1, lon1, lat2, lon2):
    x, y, z = spherToCart(lat2, lon2)
    x, y = rotate(x, y, lon1)
    z, x = rotate(z, x, math.pi / 2 - lat1)
    lat, lon = cartToSpher(x, y, z)
    dist = math.pi / 2 - lat
    azi = math.pi - lon
    return (dist, azi)

def direct(lat1, lon1, dist, azi):
    x, y, z = spherToCart(math.pi / 2 - dist, math.pi - azi)
    z, x = rotate(z, x, lat1 - math.pi / 2)
    x, y = rotate(x, y, -lon1)
    lat2, lon2 = cartToSpher(x, y, z)
    return (lat2, lon2)

def angular(lat1, lon1, lat2, lon2, azi13, azi23):
    failure = False
    dist12, azi21 = inverse(lat2, lon2, lat1, lon1)
    dist12, azi12 = inverse(lat1, lon1, lat2, lon2)
    cos_beta1 = math.cos(azi13 - azi12)
    sin_beta1 = math.sin(azi13 - azi12)
    cos_beta2 = math.cos(azi21 - azi23)
    sin_beta2 = math.sin(azi21 - azi23)
    cos_dist12 = math.cos(dist12);
    sin_dist12 = math.sin(dist12);
    if sin_beta1 == 0. and sin_beta2 == 0.:
        failure = True
        lat3 = 0.
        lon3 = 0.
    elif sin_beta1 == 0.:
        lat3 = lat2
        lon3 = lon2
    elif sin_beta2 == 0.:
        lat3 = lat1
        lon3 = lon1
    elif sin_beta1 * sin_beta2 < 0.:
        if math.fabs(sin_beta1) >= math.fabs(sin_beta2):
            cos_beta2 = -cos_beta2
            sin_beta2 = -sin_beta2
        else:
            cos_beta1 = -cos_beta1
            sin_beta1 = -sin_beta1
    else:
        dist13 = math.atan2(math.fabs(sin_beta2) * sin_dist12, cos_beta2 * math.fabs(sin_beta1) + math.fabs(sin_beta2) * cos_beta1 * cos_dist12)
        lat3, lon3 = direct(lat1, lon1, dist13, azi13)
    return (failure, lat3, lon3)

def linear(lat1, lon1, lat2, lon2, dist13, dist23, clockwise):
    failure = False
    if dist13 == 0.:
        lat3 = lat1
        lon3 = lon1
    elif dist23 == 0.:
        lat3 = lat2
        lon3 = lon2
    else:
        dist12, azi12 = inverse(lat1, lon1, lat2, lon2)
        cos_beta1 = (math.cos(dist23) - math.cos(dist12) * math.cos(dist13)) / (math.sin(dist12) * math.sin(dist13))
        if math.fabs(cos_beta1) > 1.:
            failure = True
            lat3 = 0.
            lon3 = 0.
        else:
            if clockwise:
                azi13 = azi12 + math.acos(cos_beta1)
            else:
                azi13 = azi12 - math.acos(cos_beta1)
            lat3, lon3 = direct(lat1, lon1, dist13, azi13)
    return (failure, lat3, lon3)

