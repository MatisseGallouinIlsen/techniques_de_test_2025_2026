"""Module de test pour Triangulation.

Ce module gère les tests de la fonction Triangulation défini dans triangulation.py
"""
import contextlib
import time
from unittest.mock import patch

import pytest

from triangulation import triangulation


def test_triangulation_not_enough_points():
    """Test l'apparition d'erreur.
    
    lorsque que le nombres de points est insuffisants (moins de 3).
    """
    with pytest.raises(Exception) as exec:
        triangulation([])
    assert "INVALID_POINTSET" in str(exec.value)

    with pytest.raises(Exception) as exec:
        triangulation([(0, 0)])
    assert "INVALID_POINTSET" in str(exec.value)
    
    with pytest.raises(Exception) as exec:
        triangulation([(0, 0), (1, 1)])
    assert "INVALID_POINTSET" in str(exec.value)

def test_triangulation_colinear_points():
    """Test l'apparition d'erreur.
    
    lorsque que les points sont colinéaires.
    """
    pts = [(0, 0), (1, 1), (2, 2)]
    with pytest.raises(Exception) as exc:
        triangulation(pts)
    assert "INVALID_POINTSET" in str(exc.value)


def test_triangulation_invalid_coordinates():
    """Test l'apparition d'erreur.
    
    lorsque que les points possèdent des coordonnées invalides.
    """
    pts = [(0, 0), (float('nan'), 2), (3, 4)]
    with pytest.raises(Exception) as exc:
        triangulation(pts)
    assert "INVALID_POINT" in str(exc.value)

def test_triangulation_bad_points_type():
    """Test l'apparition d'erreur.
    
    lorsque que les coordonnées des points possède le mauvais type.
    """
    pts = [(0, 0), ("1", 0), (0, 1)]
    with pytest.raises(Exception) as exc:
        triangulation(pts)
    assert "INVALID_POINT" in str(exc.value)
    
@patch("triangulation._add_triangle", side_effect=Exception("Internal Error"))
def test_triangulation_internal_error(_):
    """Test l'apparition d'erreur.
    
    lorsque une erreur arrive lors de la triangulation.
    """
    pts = [(0, 0), (1, 0), (0, 1)] 
    with pytest.raises(Exception) as exc:
        triangulation(pts)
    assert "ERROR_TRIANGULATION" in str(exc.value)

def test_triangulation_success():
    """Test le comportement de la fonction en cas de succès."""
    res = triangulation([(0, 0), (1, 0), (0, 1)])
    assert isinstance(res, list)
    assert len(res) >= 1

# --- Tests de performance ---
@pytest.mark.perf
def test_perf_triangulation_small():
    """Test les perfommances en cas de petit dataset."""
    points = [(i, i % 10) for i in range(10)]
    start = time.time()
    with contextlib.suppress(Exception):
        triangulation(points)
    end = time.time()
    assert (end - start) < 0.10
@pytest.mark.perf
def test_perf_triangulation_medium():
    """Test les perfommances en cas de moyen dataset."""
    points = [(i, i % 100) for i in range(1000)]
    start = time.time()
    with contextlib.suppress(Exception):
        triangulation(points)
    end = time.time()
    assert (end - start) < 0.50
@pytest.mark.perf
def test_perf_triangulation_large():
    """Test les perfommances en cas de gros dataset."""
    points = [(i, i % 1000) for i in range(10000)]
    start = time.time()
    with contextlib.suppress(Exception):
        triangulation(points)
    end = time.time()
    assert (end - start) < 10.0