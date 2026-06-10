#mode light

pi = 3.141592653589793
e = 2.718281828459045

fn radians(deg):
    return deg * pi / 180

fn degrees(rad):
    return rad * 180 / pi

fn clamp(x, min_val, max_val):
    if x < min_val:
        return min_val
    if x > max_val:
        return max_val
    return x

fn lerp(a, b, t):
    return a + (b - a) * t
