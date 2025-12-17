"""Module de test pour ParseTriangle.

Ce module gère les tests de la fonction ParseTriangle défini dans triangulation.py
"""
import struct
import time
from unittest.mock import patch

import pytest

from triangulation import parseTriangle

POINTSET_VALID = (
    b"\x03\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x80\x3F\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x80\x3F"
)

# --- Tests de comportement ---
def test_parseTriangle_invalid_pointset_format():
    """Test l'apparition d'erreur.
    
    lorsque que le format du pointset est invalide.
    """
    with pytest.raises(Exception) as exc:
        parseTriangle(b"\x01", [])
    assert "INVALID_POINTSET_BYTE_FORMAT" in str(exc.value)


def test_parseTriangle_invalid_triangle_coordinates():
    """Test l'apparition d'erreur.
    
    lorsque que les coordonnées des points du triangles sont invalides.
    """
    with pytest.raises(Exception) as exc:
        parseTriangle(POINTSET_VALID, [((0, 0), (9999999999999, 1), (1, 1))])
    assert "INVALID_TRIANGLE" in str(exc.value)


def test_parseTriangle_colinear():
    """Test l'apparition d'erreur.
    
    lorsque que les points d'un triangle sont colinéaires.
    """
    tri = [((0, 0), (1, 1), (2, 2))]
    with pytest.raises(Exception) as exc:
        parseTriangle(POINTSET_VALID, tri)
    assert "INVALID_TRIANGLE" in str(exc.value)


@patch("struct.pack", side_effect=Exception("encoding failed"))
def test_parseTriangle_encoding_error(_):
    """Test l'apparition d'erreur.
    
    lorsque qu'une exception normale est renvoyé lors du parsing.
    """
    with pytest.raises(Exception) as exc:
        parseTriangle(POINTSET_VALID, [((0, 0), (1, 0), (0, 1))])
    assert "ENCODING_ERROR" in str(exc.value)

@patch("struct.pack", side_effect=KeyError("encoding failed"))
def test_parseTriangle_key_error(_):
    """Test l'apparition d'erreur.
    
    lorsque qu'une keyerror est renvoyé lors du parsing.
    """
    with pytest.raises(Exception) as exc:
        parseTriangle(POINTSET_VALID, [((0, 0), (1, 0), (0, 1))])
    assert "INVALID_TRIANGLE" in str(exc.value)
    
@patch("struct.pack", side_effect=struct.error("encoding failed"))
def test_parseTriangle_struct_error(_):
    """Test l'apparition d'erreur.
    
    lorsque qu'une struct.error est renvoyé lors du parsing.
    """
    with pytest.raises(Exception) as exc:
        parseTriangle(POINTSET_VALID, [((0, 0), (1, 0), (0, 1))])
    assert "ENCODING_ERROR" in str(exc.value)

def test_parseTriangle_success():
    """Test le comportement de la fonction en cas de succès."""
    res = parseTriangle(POINTSET_VALID, [((0, 0), (1, 0), (0, 1))])
    assert isinstance(res, (bytes, bytearray))


# ---- Test de Performance ----

def test_parseTriangle_perf_small():
    """Test les perfommances en cas de petit dataset."""
    start = time.time()
    parseTriangle(POINTSET_VALID, [((0, 0), (1, 0), (0, 1))])
    end = time.time()
    assert (end - start) < 0.01


def test_parseTriangle_perf_medium():
    """Test les perfommances en cas de moyen dataset."""
    triangles = [((0, 0), (1, 0), (0, 1))] * 100
    start = time.time()
    parseTriangle(POINTSET_VALID, triangles)
    end = time.time()
    assert (end - start) < 0.2


def test_parseTriangle_perf_large():
    """Test les perfommances en cas de gros dataset."""
    triangles = [((0, 0), (1, 0), (0, 1))] * 2000
    start = time.time()
    parseTriangle(POINTSET_VALID, triangles)
    end = time.time()
    assert (end - start) < 5