"""Module de test pour RecupPointSet.

Ce module gère les tests de la fonction RecupPointSet défini dans triangulation.py
"""
import contextlib
import time
from unittest.mock import patch

import pytest

from triangulation import recupPointSet

# --- Tests de comportement ---

VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"

def test_recupPointSet_invalid_id_format():
    """Test l'apparition d'erreur.
    
    lorsque que le format de l'id du pointset est invalide.
    """
    with pytest.raises(Exception) as exc:
        recupPointSet("")
    assert "INVALID_ID_FORMAT" in str(exc.value)


@patch("triangulation.requests.get")
def test_recupPointSet_pointset_not_found(mock_get):
    """Test l'apparition d'erreur.
    
    lorsque que le pointset n'est pas trouvé.
    """
    mock_get.return_value.status_code = 404
    with pytest.raises(Exception) as exc:
        recupPointSet(VALID_UUID)
    assert "NO_POINTSET_FOUND" in str(exc.value)


@patch("triangulation.requests.get")
def test_recupPointSet_no_response_server(mock_get):
    """Test l'apparition d'erreur.
    
    lorsque que le serveur est indisponnible.
    """
    mock_get.side_effect = Exception("timeout")
    with pytest.raises(Exception) as exc:
        recupPointSet(VALID_UUID)
    assert "NO_RESPONSE_SERVEUR" in str(exc.value)


@patch("triangulation.requests.get")
def test_recupPointSet_success(mock_get):
    """Test le comportement de la fonction en cas de succès."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"\x00\x01"
    res = recupPointSet(VALID_UUID)
    assert res == b"\x00\x01"
    
@patch("triangulation.requests.get")
def test_recupPointSet_generic_http_error(mock_get):
    """Test l'apparition d'erreur.
    
    lorsque que le serveur renvoie une erreur classique.
    """
    mock_get.return_value.status_code = 500
    with pytest.raises(Exception) as exc:
        recupPointSet("123e4567-e89b-12d3-a456-426614174000")
    assert "NO_RESPONSE_SERVEUR" in str(exc.value)
    
# --- Tests de performance ---

def test_recupPointSet_perf_small():
    """Test les perfommances en cas de petit dataset."""
    start = time.time()
    with contextlib.suppress(Exception):
        recupPointSet("1")
    end = time.time()
    assert (end - start) < 0.20