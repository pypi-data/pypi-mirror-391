from matrixmania.compute2 import matmul
import pytest


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


def test_2by4_4by3():

    # Arrange
    a = matrix_a
    b = matrix_b
    expected_value = [
                    [20, 37, 26],
                    [-1, 27, -8]
                    ]

    # Act
    result = matmul(a, b)

    # Assert
    assert result == expected_value
    assert isinstance(result, list)
    assert all(isinstance(row, list) for row in result)



def test_2by2_2by4():

    # Arrange
    a = matrix_d
    b = matrix_a
    expected_value = [[-1, 8, 9, 6],[1, 20, 17, 16]]

    # Act
    result = matmul(a, b)

    # Assert
    assert result == expected_value
    assert isinstance(result, list)
    assert all(isinstance(row, list) for row in result)


def test_2by4_2by2():
    """Tests if Value Error is raised when dimensions don't match"""
    a = matrix_a
    b = matrix_d

    with pytest.raises(ValueError):
        matmul(a, b)

def test_with_string():

    """Tests if Type Error is raised when element is string"""
    a = matrix_d
    b = matrix_s

    with pytest.raises(TypeError):
        matmul(a, b)

