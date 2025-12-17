"""Module de test API.

Ce module gère les tests de l'API flask donné dans le fichier app.py
"""
import contextlib
import os
import sys
from unittest.mock import patch

import pytest

sys.path.append(os.getcwd())

with contextlib.suppress(ImportError):
    from app import app

@pytest.fixture
def client():
    """Génération de la configuration de test pour le client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_triangulation_success(client):
    """Test Comportement normal de l'endpoint."""
    # On doit mocker TOUTES les étapes, y compris parsePointSet
    with patch("triangulation.recupPointSet") as mock_recup, \
         patch("triangulation.parsePointSet") as mock_parse_pts, \
         patch("triangulation.triangulation") as mock_algo, \
         patch("triangulation.parseTriangle") as mock_parse_tri:
        
        mock_recup.return_value = b"FAKE_DATA"
        mock_parse_pts.return_value = [(0,0), (1,1), (0,1)] # Des points valides
        mock_algo.return_value = [((0,0), (1,1), (0,1))]    # Un triangle valide
        mock_parse_tri.return_value = b"RESULT_BINARY"

        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")
        
        assert response.status_code == 200
        assert response.data == b"RESULT_BINARY"

def test_api_invalid_uuid(client):
    """Test le retour 400 quand l'uuid rentré est mauvais."""
    response = client.get("/triangulation/not-a-uuid")
    assert response.status_code == 400
    
def test_api_pointset_not_found(client):
    """Teste le retour 404 quand le pointset n'existe pas."""
    # On simule que recupPointSet lève l'exception NO_POINTSET_FOUND
    with patch(
        "triangulation.recupPointSet", 
        side_effect=Exception("NO_POINTSET_FOUND")
        ):
        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")
        assert response.status_code == 404
        assert response.json['code'] == 'POINTSET_NOT_FOUND'

def test_api_service_unavailable(client):
    """Teste le retour 503 quand le manager ne répond pas."""
    with patch(
        "triangulation.recupPointSet", 
        side_effect=Exception("NO_RESPONSE_SERVEUR")
        ):
        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")
        assert response.status_code == 503
        assert response.json['code'] == 'SERVICE_UNAVAILABLE'

def test_api_internal_error(client):
    """Teste le retour 500 sur une erreur imprévue."""
    with patch(
        "triangulation.recupPointSet", 
        side_effect=Exception("Boom!")
        ):
        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")
        assert response.status_code == 500
        assert response.json['code'] == 'INTERNAL_ERROR'

def test_api_invalid_request(client):
    """Test le retour 400 dans le cas où le pointset est invalide."""
    with patch(
        "triangulation.recupPointSet", 
        side_effect=Exception("INVALID_POINTSET")
        ):
        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")
        assert response.status_code == 400
        assert response.json['code'] == 'INVALID_REQUEST'