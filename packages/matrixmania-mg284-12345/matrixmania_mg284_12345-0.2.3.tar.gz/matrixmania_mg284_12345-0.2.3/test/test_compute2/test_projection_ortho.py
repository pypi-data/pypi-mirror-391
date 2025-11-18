from matrixmania.compute2 import project_ortho
import pytest


def test_not_scaled():
    # Arrange
    point = (1.0, 2.0, 3.0)
    #scale = 1
    expected_value = (1.0, 2.0)

    # Act
    result = project_ortho(point)

    # Assert
    assert result == expected_value
    assert isinstance(result, tuple)


def test_scaled():
    # Arrange
    point = (1.0, 2.0, 3.0)
    scale = 100
    expected_value = (100.0, 200.0)

    # Act
    result = project_ortho(point, scale)

    # Assert
    assert result == expected_value
    assert isinstance(result, tuple)


def test_point_is_too_short():

    """Tests if Type Error is raised when point is not tuple/ list of three numbers"""

    point = (1.0, 2.0)
    scale = 1

    with pytest.raises(TypeError):
        project_ortho(point, scale)


def test_point_is_wrong_type():

    """Tests if Type Error is raised when point is not tuple/ list of numbers with type int or float"""

    point = (1.0, 2.0, "hi")
    scale = 1

    with pytest.raises(TypeError):
        project_ortho(point, scale)


def test_scale_is_wrong_type():

    """Tests if Type Error is raised when scale is not int or float"""

    point = (1.0, 2.0, 3.0)
    scale = "hallo"

    with pytest.raises(TypeError):
        project_ortho(point, scale)

