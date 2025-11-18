# Matrixmultiplikation, Transponieren einer Matrix und Rotation

from typing import List, Tuple
import math
from tabulate import tabulate




# Matrixmultiplikation

def matmul(a: List[List[int | float]], b: List[List[int | float]]) -> List[List[int | float]]:

    """
    Multiply 2 matrices
    :param a: matrix 1
    :type a: List[List[int | float]]
    :param b: matrix 2
    :type b: List[List[int | float]]
    :return: Product of the 2 matrices
    :rtype: List[List[int | float]]
    :raises ValueError: when width of matrix 1 is not equal to height of matrix 2
    :raises TypeError: when element in matrix is not int or float
    """

    check_for_string(a)
    check_for_string(b)

    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])

    if not cols_a == rows_b:
        raise ValueError("Width of first matrix is not equal to height of second matrix!")

    result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]

    return result




#Transponieren einer Matrix

def transpose(f: List[List[int | float]]) -> List[List[int | float]]:

    """
    Transpose the matrix
    :param f: the given matrix
    :type f: List[List[int | float]]
    :return: transposed matrix
    :rtype: List[List[int | float]]
    :raises ValueError: when matrix is empty or not all rows have the same amount of columns
    :raises TypeError: when element in matrix is not int or float
    """

    if not f or not all(f) or not f[0]:
        raise ValueError("Matrix is empty!")

    check_for_string(f)

    rows_f, cols_f = len(f), len(f[0])

    for i in range(rows_f):
        if not len(f[i]) == cols_f:
            raise ValueError("Not all rows have the same amount of columns!")

    result = [[0 for _ in range(rows_f)] for _ in range(cols_f)]
    for i in range(rows_f):
        for j in range(cols_f):
            result[j][i] = f[i][j]

    return result




# Rotation 2D

def rot_2D(degree: int | float) -> List[List[int | float]]:

    """
    Rotationmatrix of given angle for 2D
    :param degree: the given angle
    :type degree: int | float
    :raises TypeError: when degree is not int or float
    :return: rotationmatrix
    :rtype: List[List[int | float]]
    """

    if not isinstance(degree, (int, float)):
        raise TypeError("Degree must be int or float!")

    angle : int | float = math.radians(degree)
    matrix_rotation = [[math.cos(angle), -math.sin(angle)],
                       [math.sin(angle), math.cos(angle)]
                      ]

    return matrix_rotation


# Rotation 3D

def rot_3D(angle: int | float, axis: str) -> List[List[int | float]]:

    """
    Rotationmatrix of given angle for 3D
    :param angle: the given angle
    :type angle: int | float
    :param axis: the given axis
    :type axis: str
    :raises TypeError: when angle is not int or float
    :raises ValueError: when axis is not x, y or z
    :return: rotationmatrix
    :rtype: List[List[int | float]]
    """

    if axis not in ("x", "y", "z"):
        raise ValueError("Axis must be x, y or z!")

    if not isinstance(angle, (int, float)):
        raise TypeError("Angle must be int or float!")


    new_angle : int | float = math.radians(angle)

    x_rotation = [[1, 0, 0],
                  [0, math.cos(new_angle), -math.sin(new_angle)],
                  [0, math.sin(new_angle), math.cos(new_angle)]
                  ]

    y_rotation = [[math.cos(new_angle), 0, math.sin(new_angle)],
                  [0, 1, 0],
                  [-math.sin(new_angle), 0, math.cos(new_angle)]
                  ]

    z_rotation = [[math.cos(new_angle), -math.sin(new_angle), 0],
                  [math.sin(new_angle), math.cos(new_angle), 0],
                  [0, 0, 1]
                  ]

    rotations = {"x": x_rotation, "y": y_rotation, "z": z_rotation}

    return rotations[axis]



# Projektion von Punkt in 3D auf 2D Ebene

def project_ortho(point: Tuple[int | float, int | float, int | float], scale: int | float = 1) -> (
        Tuple)[int | float, int | float]:

    """
    Projection of a 3d point to 2d
    :param point: point in 3D
    :type point: Tuple[int | float, int | float, int | float] or a list
    :param scale: the scaling factor
    :type scale: int | float = 1
    :raises TypeError: when x, y or z is not int or float
    :raises TypeError: when scale is not int or float
    :return: the (scaled) point in 2D
    :rtype: Tuple[int | float, int | float]
    """


    if not (isinstance(point, int | tuple) or isinstance(point, list)) or len(point) != 3:
        raise TypeError("point must be a tuple/list of three numeric values")

    if not isinstance(scale, (int, float)):
        raise TypeError("Scale must be int or float!")

    if not all(isinstance(i, (int, float)) for i in point):
        raise TypeError("x, y, z in point must be int or float")

    x, y, z = point

    x_scaled = float(x) * float(scale)
    y_scaled = float(y) * float(scale)

    return (x_scaled, y_scaled)




# Checks if Type of a matrix is not int or float

def check_for_string(matrix: List[List[int | float]]) -> None:

    """
    Checks that all elements in the matrix are integers or floats
    :param matrix: The matrix to check (list of lists of int or float)
    :type matrix: List[List[int | float]]
    :raises TypeError: If any element is not an int or float
    """

    if not all(isinstance(x, (int, float)) for row in matrix for x in row):
        raise TypeError("All elements of the matrix must be int or float")




if __name__ == "__main__":

    # hab ich alles selbst programmiert
    
    # matrixmultiplikation

    matrix_a = [[3, 4, -1, 4],
                [-2, 2, 5, 1]
                ]
    matrix_b = [[1, 3, -2],
                [2, 5, 1],
                [-1, 4, -4],
                [2, 3, 6]
                ]
    matrix_d = [[1, 2],
                [3, 4]
                ]

    matrix_s = [["p", 2],
                [3, 4]
                ]


    print("Matrix A:")
    print(tabulate(matrix_a))

    try:
        matrix_c : List[List[int | float]] = matmul(matrix_a, matrix_b)
        print("Ergebnis C = A * B:")
        print("[")
        for row in matrix_c:
            print(row)
        print("]")
    except ValueError as v:
        print(f"Mistake for matrix_c: {v}")

    try:
        matrix_e : List[List[int | float]] = matmul(matrix_a, matrix_d)
        print("Ergebnis E = A * D:")
        for row in matrix_e:
            print(row)
    except ValueError as v:
        print(f"Mistake for matrix_e: {v}")

    try:
        matrix_h : List[List[int | float]] = matmul(matrix_d, matrix_s)
        print("Ergebnis H = D * S:")
        for row in matrix_h:
            print(row)
    except TypeError as t:
        print(f"Mistake for matrix_h: {t}")



    # transponieren

    matrix_f = [[1, 2, 3],
                [4, 5, 6]
                ]

    matrix_g : List[List[int | float]] = transpose(matrix_f)
    print("[")
    for row in matrix_g:
        print(row)
    print("]")


    # rotation matrix 2D

    matrix_r : List[List[int | float]] = rot_2D(90)
    print("[")
    for row in matrix_r:
        print(row)
    print("]")


    # rotation matrix 3D

    matrix_r3x: List[List[int | float]] = rot_3D(90, "x")
    print("[")
    for row in matrix_r3x:
        print(row)
    print("]")

    matrix_r3y: List[List[int | float]] = rot_3D(-90, "y")
    print("[")
    for row in matrix_r3y:
        print(row)
    print("]")

    matrix_r3z: List[List[int | float]] = rot_3D(90, "z")
    print("[")
    for row in matrix_r3z:
        print(row)
    print("]")


    # Projection

    print(project_ortho((0.5, -0.5, 10), 200)) # -> (100, -100)


# verbesserungsvorschläge:
# angeben ob winkel in deg oder rad angegeben werden
# in rot 3D: es müssen nicht für alle achsen gerechnet werden, nur für die die verlangt ist
