import pytest
from requests import patch
import time
from triangulation import triangulation

def test_triangulation_not_enough_points():
    with pytest.raises(Exception):
        triangulation([])

    with pytest.raises(Exception):
        triangulation([(0, 0)])

    with pytest.raises(Exception):
        triangulation([(0, 0), (1, 1)])


def test_triangulation_colinear_points():
    pts = [(0, 0), (1, 1), (2, 2)]
    with pytest.raises(Exception) as exc:
        triangulation(pts)
    assert "INVALID_POINTSET" in str(exc.value)


def test_triangulation_invalid_coordinates():
    pts = [(0, 0), (1e200, 2), (3, 4)]
    with pytest.raises(Exception) as exc:
        triangulation(pts)
    assert "INVALID_POINT" in str(exc.value)


@patch("triangulation.some_internal_call", side_effect=Exception("fail"))
def test_triangulation_internal_error(_):
    with pytest.raises(Exception) as exc:
        triangulation([(0, 0), (1, 0), (0, 1)])
    assert "ERROR_TRIANGULATION" in str(exc.value)


def test_triangulation_success():
    res = triangulation([(0, 0), (1, 0), (0, 1)])
    assert isinstance(res, list)
    assert len(res) >= 1

# --- Tests de performance ---
@pytest.mark.perf
def test_perf_triangulation_small():
    points = [(i, i % 10) for i in range(10)]
    start = time.time()
    try:
        triangulation(points)
    except Exception:
        pass
    end = time.time()
    assert (end - start) < 0.10
@pytest.mark.perf
def test_perf_triangulation_medium():
    points = [(i, i % 100) for i in range(1000)]
    start = time.time()
    try:
        triangulation(points)
    except Exception:
        pass
    end = time.time()
    assert (end - start) < 0.50
@pytest.mark.perf
def test_perf_triangulation_large():
    points = [(i, i % 1000) for i in range(10000)]
    start = time.time()
    try:
        triangulation(points)
    except Exception:
        pass
    end = time.time()
    assert (end - start) < 10.0