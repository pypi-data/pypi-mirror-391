from matrixmania.compute2 import rot_2D
import pytest
import math


def test_rot_2D_90():

    # Arrange
    a = 90

    expected_value = [[0.0, -1.0],[1.0, 0.0]]

    # Act
    result = rot_2D(a)

    # Assert
    for r_row, e_row in zip(result, expected_value):
        for r, e in zip(r_row, e_row):
            assert math.isclose(r, e, abs_tol=1e-9)


def test_degree_is_wrong_type():
    """Tests if Type Error is raised if degree is not int or float"""
    a = "p"

    with pytest.raises(TypeError):
        rot_2D(a)


def test_rot_2D_negative():

    a = -90

    expected_value = [
                [0.0, 1.0],
                [-1.0, 0.0]
                ]

    result = rot_2D(a)

    for r_row, e_row in zip(result, expected_value):
        for r, e in zip(r_row, e_row):
            assert math.isclose(r, e, abs_tol=1e-9)