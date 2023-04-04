import math


def ManhattanDistance(a, b):
    dx = abs(b[0] - a[0])
    dy = abs(b[1] - a[1])
    return dx + dy


def EuclideanDistance(a, b):
    dx = abs(b[0] - a[0])
    dy = abs(b[1] - a[1])
    return (dx**2 + dy**2)**0.5


def ChebychevDistance(a, b):
    dx = abs(b[0] - a[0])
    dy = abs(b[1] - a[1])
    return max(dx, dy)


def OctileDistance(a, b):
    dx = abs(b[0] - a[0])
    dy = abs(b[1] - a[1])
    return dx + dy + (2**0.5 - 2) * min(dx, dy)


def ComputeCost(a, b):
    return EuclideanDistance(a, b)
