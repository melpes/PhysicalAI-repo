import math


def quat_to_matrix(q):
    norm = math.sqrt(sum(c * c for c in q))
    w, x, y, z = (c / norm for c in q)
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]]


def axis_rotation(axis, angle_deg):
    half = math.radians(angle_deg) / 2
    norm = math.sqrt(sum(a * a for a in axis))
    return quat_to_matrix([math.cos(half)] + [a / norm * math.sin(half) for a in axis])


def quat_to_axis_angle(q):
    norm = math.sqrt(sum(c * c for c in q))
    w, x, y, z = (c / norm for c in q)
    s = math.sqrt(max(0.0, 1.0 - w * w))
    if s < 1e-12:
        return (0.0, 0.0, 1.0), 0.0
    return (x / s, y / s, z / s), math.degrees(2.0 * math.acos(w))


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def rotate(R, v):
    return [sum(R[i][k] * v[k] for k in range(3)) for i in range(3)]
