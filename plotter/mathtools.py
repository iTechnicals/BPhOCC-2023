import math
import numpy as np

def cfcs_to_func(x, coefficients):
    return_value = 0
    for i, cfc in enumerate(coefficients):
        return_value += cfc[0] * pow(x, i)
    return return_value

def regress(data, degree):
    xis = [0 for i in range(degree * 2 + 1)]
    xyis = [0 for i in range(degree + 1)]

    for i in range(degree * 2 + 1):
        for point in data:
            xis[i] += pow(point[0], i)
    
    for i in range(degree + 1):
        for point in data:
            xyis[i] += pow(point[0], i) * point[1]

    matrix_x = [[] for i in range(degree + 1)]
    for row in range(degree + 1):
        for column in range(degree + 1):
            matrix_x[row].append(xis[row + column])
    
    matrix_x = np.array(matrix_x)
    matrix_y = np.array([[xyis[x]] for x in range(degree + 1)])

    sols = np.linalg.inv(matrix_x) @ matrix_y
    return sols

def simpsons(func, a, b, N=50):
    dx = (b-a)/N
    x = np.linspace(a, b, N+1)
    y = func(x)

    S = dx / 3 * np.sum(y[0:-1:2] + 4*y[1::2] + y[2::2])
    return S

def orbit_angle(theta, P, epsilon):
    return P * pow(1 - pow(epsilon, 2), 3/2) * simpsons(lambda theta: pow(1 - epsilon * np.cos(theta), -2), 0, theta) / (math.pi * 2)