"""Module de test pour ParsePointSet.

Ce module gère les tests de la fonction ParsePointSet défini dans triangulation.py
"""
import contextlib
import struct
import time
from unittest.mock import patch

import pytest

from triangulation import parsePointSet

# Ce binaire déclare 3 points (\x03 au début)
POINTSET_VALID = (
    b"\x03\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x80\x3F\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x80\x3F"
)

# --- Tests de comportement ---

def test_parsePointSet_invalid_format():
    """Test l'apparition d'erreur.
    
    lorsque que le format est invalide.
    """
    with pytest.raises(Exception) as exc:
        parsePointSet(b"\x01")
    assert "INVALID_RESPONSE_FORMAT" in str(exc.value)

def test_parsePointSet_decode_error():
    """Test l'apparition d'erreur.
    
    lorsque que le décodage échoue.
    """
    with pytest.raises(Exception) as exc:
        parsePointSet(b"\x02\x00\x00\x00\x01\xFF")
    assert "DECODE_ERROR" in str(exc.value)

def test_parsePointSet_invalid_coordinates():
    """Test l'apparition d'erreur.
    
    lorsque que les coordonnées sont invalides.
    """
    data = b"\x02\xFF\xFF\xFF\xFF"
    with pytest.raises(Exception) as exc:
        parsePointSet(data)
    assert "DECODE_ERROR" in str(exc.value)
    
def test_parsePointSet_nan_coordinates():
    """Test l'apparition d'erreur.
     
    lorsque que les coordonnées sont égales à nan.
    """
    header = struct.pack('<I', 1)
    point_data = struct.pack('<ff', float('nan'), 0.0)
    data = header + point_data
    with pytest.raises(Exception) as exc:
        parsePointSet(data)
    assert "DECODE_ERROR" in str(exc.value)

@patch("struct.unpack_from", side_effect=struct.error("unparsing error"))
def test_parsePointSet_unpack_error(_):
    """Test l'apparition d'erreur.
    
    lorsque qu'une struct error est renvoyé.
    """
    data = b"\x02\xFF\xFF\xFF\xFF"
    with pytest.raises(Exception) as exc:
        parsePointSet(data)
    assert "DECODE_ERROR" in str(exc.value)

def test_parsePointSet_success():
    """Test le comportement de la fonction en cas de succès."""
    res = parsePointSet(POINTSET_VALID)
    assert isinstance(res, list)
    assert len(res) == 3

# --- Tests de performance ---
@pytest.mark.perf
def test_perf_parse_small():
    """Test les perfommances en cas de petit dataset."""
    data = POINTSET_VALID
    start = time.time()
    with contextlib.suppress(Exception):
        parsePointSet(data)
    end = time.time()
    assert (end - start) < 0.05
    
@pytest.mark.perf
def test_perf_parse_medium():
    """Test les perfommances en cas de moyen dataset."""
    data = POINTSET_VALID*20
    start = time.time()
    with contextlib.suppress(Exception):
        parsePointSet(data)
    end = time.time()
    assert (end - start) < 0.10

@pytest.mark.perf
def test_perf_parse_large():
    """Test les perfommances en cas de gros dataset."""
    data = POINTSET_VALID*200
    start = time.time()
    with contextlib.suppress(Exception):
        parsePointSet(data)
    end = time.time()
    assert (end - start) < 0.20