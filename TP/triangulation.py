"""Module de triangulation.

Ce module gère la récupération des points depuis le PointSetManager,
le parsing des données binaires et l'algorithme de calcul des triangles.
"""
import math
import struct
import uuid

import requests

#URL du PointSetManager (à configurer selon l'environnement, ici par défaut)
POINT_SET_MANAGER_URL = "http://pointset_manager:8080/pointset"


def recupPointSet(idPointSet):
    """Récupère le binaire d'un PointSet via l'API PointSetManager.

    Args:
        idPointSet (str): L'UUID du PointSet.

    Returns:
        bytes: Le contenu binaire.
        
    """
    # Validation du format UUID
    try:
        uuid.UUID(str(idPointSet))
    except ValueError as e:
        raise Exception("INVALID_ID_FORMAT") from e

    # Appel au service externe
    try:
        response = requests.get(f"{POINT_SET_MANAGER_URL}/{idPointSet}", timeout=5)
    except Exception as e:
        # Capture les timeouts et erreurs de connexion
        raise Exception("NO_RESPONSE_SERVEUR") from e

    # Gestion des codes HTTP
    if response.status_code == 404:
        raise Exception("NO_POINTSET_FOUND")
    elif response.status_code != 200:
        # Cas générique pour autres erreurs serveur
        raise Exception("NO_RESPONSE_SERVEUR")

    return response.content

def parsePointSet(byteResponse):
    """Transforme la réponse binaire en liste de tuples (x, y).

    Format: 
        [NbPoints (4 bytes)] + [X (4 bytes) Y (4 bytes)] * NbPoints
    
    Args:
        byteResponse (str|bytes): Les bytes représentant une liste de point.
        
    Returns:
        points: liste des points de byteResponse.
        
    """
    # Vérification minimale de la taille (au moins 4 bytes pour le nombre de points)
    if len(byteResponse) < 4:
        raise Exception("INVALID_RESPONSE_FORMAT")

    try:
        # Lecture du nombre de points (Little Endian 'I' = unsigned int)
        num_points = struct.unpack_from('<I', byteResponse, 0)[0]
        
        expected_size = 4 + (num_points * 8)
        if len(byteResponse) != expected_size:
            raise Exception("DECODE_ERROR")

        points = []
        offset = 4
        for _ in range(num_points):
            # Lecture de X et Y (Little Endian 'f' = float)
            x, y = struct.unpack_from('<ff', byteResponse, offset)
            
            # Vérification de la validité des coordonnées (NaN ou Inf)
            if not math.isfinite(x) or not math.isfinite(y):
                raise Exception("DECODE_ERROR")
            
            points.append((x, y))
            offset += 8
            
        return points

    except struct.error as e:
        raise Exception("DECODE_ERROR") from e


def _add_triangle(liste, p1, p2, p3):
    """Fonction helper isolée pour permettre le mock.
    
    Args:
        liste (list): liste contenant tous les différents triangles.
        p1 (tuple): tuple représentant un point.
        p2 (tuple): tuple représentant un point.
        p3 (tuple): tuple représentant un point.
        
    """
    liste.append((p1, p2, p3))
    
def triangulation(points):
    """Calcule des triangles à partir d'une liste de points.
    
    Args:
        points (list): liste des points dont on veut déterminer les triangles.
    
    Returns:
        triangles (list): liste des triangles générer.
        
    """
    # Vérifications préliminaires
    if len(points) < 3:
        raise Exception("INVALID_POINTSET")

    # Vérification des coordonnées invalides dans la liste brute
    for p in points:
        if not (isinstance(p[0], (int, float)) and isinstance(p[1], (int, float))):
             raise Exception("INVALID_POINT")
        if not math.isfinite(p[0]) or not math.isfinite(p[1]):
            raise Exception("INVALID_POINT")

    # Vérification de la colinéarité
    is_colinear = True
    (x0, y0) = points[0]
    (x1, y1) = points[1]
    
    # Vecteur directeur (dx, dy)
    dx = x1 - x0
    dy = y1 - y0

    for i in range(2, len(points)):
        xi, yi = points[i]
        # Produit scalaire : (yi - y0) * dx - (xi - x0) * dy == 0
        cross_product = (yi - y0) * dx - (xi - x0) * dy
        # On utilise une petite tolérance pour les float (epsilon)
        if abs(cross_product) > 1e-9:
            is_colinear = False
            break
    
    if is_colinear:
        raise Exception("INVALID_POINTSET")

    # Algorithme de triangulation
    # Ici, on connecte le point 0 à tous les autres (0, i, i+1).
    triangles = []
    try:
        for i in range(1, len(points) - 1):
            _add_triangle(triangles,points[0], points[i], points[i+1])
    except Exception as e:
        raise Exception("ERROR_TRIANGULATION") from e

    return triangles

def parseTriangle(byteResponse, triangles):
    """Génère le binaire contenant la liste des triangles et des points.
    
    Args:
        byteResponse (str|bytes): liste des points sous forme de byte.
        triangles : liste des triangles généré.

    Returns:
        output (bytes): liste des points et triangles parsé sous forme de byte.
        
    """
    # Re-parser les points pour obtenir leurs indices
    # On a besoin de savoir que le point (x,y) est à l'index i
    try:
        original_points = parsePointSet(byteResponse)
    except Exception as e :
        raise Exception("INVALID_POINTSET_BYTE_FORMAT")from e

    # Création d'un dictionnaire pour map inversée : (x, y) -> index
    point_to_index = {pt: i for i, pt in enumerate(original_points)}

    # Préparation du binaire de sortie 
    output = bytearray(byteResponse)

    # Encodage des triangles
    try:
        num_triangles = len(triangles)
        # Ajout du nombre de triangles (unsigned int)
        output.extend(struct.pack('<I', num_triangles))

        for tri in triangles:
            # tri est un tuple ((x1,y1), (x2,y2), (x3,y3))
            
            # Vérification colinéarité locale du triangle
            p1, p2, p3 = tri
            if abs((p2[1] - p1[1]) * (p3[0] - p2[0]) - \
                (p3[1] - p2[1]) * (p2[0] - p1[0])) < 1e-9:
                 raise Exception("INVALID_TRIANGLE")

            # Récupération des indices
            indices = []
            for p in tri:
                if p not in point_to_index:
                    # Le point du triangle n'existe pas dans le set original
                    raise Exception("INVALID_TRIANGLE")
                indices.append(point_to_index[p])
            
            # Ajout des 3 indices (3 * unsigned int)
            output.extend(struct.pack('<III', indices[0], indices[1], indices[2]))

    except KeyError as e:
        raise Exception("INVALID_TRIANGLE") from e
    except struct.error as e:
        raise Exception("ENCODING_ERROR") from e
    except Exception as e:
        if str(e) in ["INVALID_TRIANGLE", "INVALID_POINTSET_BYTE_FORMAT"]:
            raise e
        raise Exception("ENCODING_ERROR") from e

    return output