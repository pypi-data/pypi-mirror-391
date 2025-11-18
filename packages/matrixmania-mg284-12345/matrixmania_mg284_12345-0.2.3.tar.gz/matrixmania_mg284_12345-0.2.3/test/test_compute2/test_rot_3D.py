from matrixmania.compute2 import rot_3D
import pytest
import math


def test_rot_3D_90x():

    # Arrange
    a = 90
    expected_value = [[1, 0, 0],
                    [0, 6.123233995736766e-17, -1.0],
                    [0, 1.0, 6.123233995736766e-17]
                    ]

    # Act
    result = rot_3D(a, "x")

    # Assert
    for r_row, e_row in zip(result, expected_value):
        for r, e in zip(r_row, e_row):
            assert math.isclose(r, e, abs_tol=1e-9)


def test_angle_is_wrong_type():
    """Tests if Type Error is raised when angle is not int or float"""
    a = "p"

    with pytest.raises(TypeError):
        rot_3D(a, "x")

def test_axis_is_wrong_type():
    """Tests if Value Error is raised when axis is not str"""
    a = 90

    with pytest.raises(ValueError):
        rot_3D(a, 8)

def test_axis_not_xyz():
    """Tests if Value Error is raised when axis is a string that's not x, y or z"""
    a = 90

    with pytest.raises(ValueError):
        rot_3D(a, "l")

def test_rot_3D_negative():

    a = -90

    expected_value = [[6.123233995736766e-17, 0, -1.0],
                    [0, 1, 0],
                    [1.0, 0, 6.123233995736766e-17]
                    ]

    result = rot_3D(a, "y")

    for r_row, e_row in zip(result, expected_value):
        for r, e in zip(r_row, e_row):
            assert math.isclose(r, e, abs_tol=1e-9)