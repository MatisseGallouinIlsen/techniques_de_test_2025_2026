"""Serveur API Flask pour le service de Triangulation.

Expose un endpoint GET /triangulation/{id} qui orchestre
la récupération, le calcul et le renvoi des triangles.
"""
from flask import Flask, Response, jsonify

import triangulation

app = Flask(__name__)

@app.route('/triangulation/<pointSetId>', methods=['GET'])
def get_triangulation(pointSetId):
    """Endpoint principal pour la triangulation.

    Récupère un set de points, calcule la triangulation et retourne le binaire.
    """
    try:
        # 1. Récupération
        point_set_bytes = triangulation.recupPointSet(pointSetId)
        
        # 2. Parsing
        points = triangulation.parsePointSet(point_set_bytes)
        
        # 3. Calcul
        triangles = triangulation.triangulation(points)
        
        # 4. Encodage
        result_bytes = triangulation.parseTriangle(point_set_bytes, triangles)
        
        return Response(result_bytes, mimetype='application/octet-stream', status=200)

    except Exception as e:
        err_msg = str(e)
        # Mapping des erreurs Python vers les codes HTTP
        if err_msg == "INVALID_ID_FORMAT":
            return jsonify({
                "code": "INVALID_ID_FORMAT",
                "message": "Invalid ID format"
                }), 400
        elif err_msg == "NO_POINTSET_FOUND":
            return jsonify({
                "code": "POINTSET_NOT_FOUND", 
                "message": "PointSet not found"
                }), 404
        elif err_msg in ["INVALID_POINTSET", "INVALID_TRIANGLE", "INVALID_POINT"]:
            return jsonify({
                "code": "INVALID_REQUEST", 
                "message": err_msg
                }), 400
        elif err_msg == "NO_RESPONSE_SERVEUR":
            return jsonify({
                "code": "SERVICE_UNAVAILABLE", 
                "message": "PointSetManager unavailable"
                }), 503
        else:
            return jsonify({
                "code": "INTERNAL_ERROR", 
                "message": err_msg
                }), 500