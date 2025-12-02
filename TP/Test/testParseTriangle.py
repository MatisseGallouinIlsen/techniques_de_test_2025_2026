import pytest
import time
from requests import patch
from triangulation import parseTriangle

POINTSET_VALID = (
    b"\x03\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x80\x3F\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x80\x3F"
)

# --- Tests de comportement ---
def test_parseTriangle_invalid_pointset_format():
    with pytest.raises(Exception) as exc:
        parseTriangle(b"\x01", [])
    assert "INVALID_POINTSET_BYTE_FORMAT" in str(exc.value)


def test_parseTriangle_invalid_triangle_coordinates():
    with pytest.raises(Exception) as exc:
        parseTriangle(POINTSET_VALID, [((0, 0), (9999999999999, 1), (1, 1))])
    assert "INVALID_TRIANGLE" in str(exc.value)


def test_parseTriangle_colinear():
    tri = [((0, 0), (1, 1), (2, 2))]
    with pytest.raises(Exception) as exc:
        parseTriangle(POINTSET_VALID, tri)
    assert "INVALID_TRIANGLE" in str(exc.value)


@patch("triangulation.some_encoder", side_effect=Exception("encoding failed"))
def test_parseTriangle_encoding_error(_):
    with pytest.raises(Exception) as exc:
        parseTriangle(POINTSET_VALID, [((0, 0), (1, 0), (0, 1))])
    assert "ENCODING_ERROR" in str(exc.value)


def test_parseTriangle_success():
    res = parseTriangle(POINTSET_VALID, [((0, 0), (1, 0), (0, 1))])
    assert isinstance(res, (bytes, bytearray))


# ---- Test de Performance ----

def test_parseTriangle_perf_small():
    start = time.time()
    parseTriangle(POINTSET_VALID, [((0, 0), (1, 0), (0, 1))])
    end = time.time()
    assert (end - start) < 0.01


def test_parseTriangle_perf_medium():
    triangles = [((0, 0), (1, 0), (0, 1))] * 100
    start = time.time()
    parseTriangle(POINTSET_VALID, triangles)
    end = time.time()
    assert (end - start) < 0.2


def test_parseTriangle_perf_large():
    triangles = [((0, 0), (1, 0), (0, 1))] * 2000
    start = time.time()
    parseTriangle(POINTSET_VALID, triangles)
    end = time.time()
    assert (end - start) < 5


def test_parseTriangle_perf_invalid_triangle():
    start = time.time()
    with pytest.raises(Exception):
        parseTriangle(POINTSET_VALID, [((0, 0), (1, 1), (2, 2))])
    end = time.time()
    assert (end - start) < 0.01
