import pytest
from triangulation import parsePointSet
import time

POINTSET_VALID = (
    b"\x03\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x80\x3F\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x80\x3F"
)

# --- Tests de comportement ---

def test_parsePointSet_invalid_format():
    with pytest.raises(Exception) as exc:
        parsePointSet(b"\x01")
    assert "INVALID_RESPONSE_FORMAT" in str(exc.value)


def test_parsePointSet_decode_error():
    with pytest.raises(Exception) as exc:
        parsePointSet("\x02\x00\x00\x00\x01\xNN")
    assert "DECODE_ERROR" in str(exc.value)


def test_parsePointSet_invalid_coordinates():
    data = b"\x02\xFF\xFF\xFF\xFF"
    with pytest.raises(Exception) as exc:
        parsePointSet(data)
    assert "DECODE_ERROR" in str(exc.value)


def test_parsePointSet_success():
    res = parsePointSet(POINTSET_VALID)
    assert isinstance(res, list)
    assert len(res) == 2

# --- Tests de performance ---
@pytest.mark.perf
def test_perf_parse_small():
    data = POINTSET_VALID
    start = time.time()
    try:
        parsePointSet(data)
    except Exception:
        pass
    end = time.time()
    assert (end - start) < 0.05
    
@pytest.mark.perf
def test_perf_parse_medium():
    data = POINTSET_VALID*20
    start = time.time()
    try:
        parsePointSet(data)
    except Exception:
        pass
    end = time.time()
    assert (end - start) < 0.10

@pytest.mark.perf
def test_perf_parse_large():
    data = POINTSET_VALID*200
    start = time.time()
    try:
        parsePointSet(data)
    except Exception:
        pass
    end = time.time()
    assert (end - start) < 0.20