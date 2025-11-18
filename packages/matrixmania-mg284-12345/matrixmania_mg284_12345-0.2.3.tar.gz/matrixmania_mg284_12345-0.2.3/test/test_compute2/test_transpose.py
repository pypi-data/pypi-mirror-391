from matrixmania.compute2 import transpose
import pytest

matrix_a = [[3, 4, -1, 4],
            [-2, 2, 5, 1]
            ]

matrix_b = [[1, 3, -2],
            [2, 5, 1],
            [-1, 4, -4],
            [2, 3, 6]
            ]

matrix_d = [[],
            []
            ]

matrix_s = [["p", 2],
            [3, 4]
            ]

matrix_f = [[1, 2, 3],
            [3]
            ]



def test_with_string():

    """Tests if Type Error is raised when element is string"""
    a = matrix_s

    with pytest.raises(TypeError):
        transpose(a)

def test_for_none():

    """Tests if Value Error is raised when matrix is empty"""
    a = matrix_d

    with pytest.raises(ValueError):
        transpose(a)

def test_for_equal_columns():

    """Tests if Value Error is raised when not all rows have the same amount of columns"""
    a = matrix_f

    with pytest.raises(ValueError):
        transpose(a)

def test_for_2by4():
    # Arrange
    a = matrix_a
    expected_value = [[3, -2],
                      [4, 2],
                      [-1, 5],
                      [4, 1]
                      ]

    # Act
    result = transpose(a)

    # Assert
    assert result == expected_value
    assert isinstance(result, list)
    assert all(isinstance(row, list) for row in result)

