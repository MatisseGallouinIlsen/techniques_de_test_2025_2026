import pytest
from requests import patch
import time
from triangulation import recupPointSet

# --- Tests de comportement ---

def test_recupPointSet_invalid_id_format():
    with pytest.raises(Exception) as exc:
        recupPointSet("")
    assert "INVALID_ID_FORMAT" in str(exc.value)


@patch("triangulation.requests.get")
def test_recupPointSet_pointset_not_found(mock_get):
    mock_get.return_value.status_code = 404
    with pytest.raises(Exception) as exc:
        recupPointSet("123")
    assert "NO_POINTSET_FOUND" in str(exc.value)


@patch("triangulation.requests.get")
def test_recupPointSet_no_response_server(mock_get):
    mock_get.side_effect = Exception("timeout")
    with pytest.raises(Exception) as exc:
        recupPointSet("123")
    assert "NO_RESPONSE_SERVEUR" in str(exc.value)


@patch("triangulation.requests.get")
def test_recupPointSet_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"\x00\x01"
    res = recupPointSet("123")
    assert res == b"\x00\x01"
    
# --- Tests de performance ---

def test_recupPointSet_perf_small():
    start = time.time()
    try:
        recupPointSet("1")
    except Exception:
        pass
    end = time.time()
    assert (end - start) < 0.20