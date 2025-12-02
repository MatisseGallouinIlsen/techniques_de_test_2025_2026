Ce projet a pour objectif la mise en place d'un serveur permettant à partir d'un id de pointset donné de calculer les différents triangles pouvant être tracés

Pour ce faire un endpoint sera mise en place (/triangulation/{pointSetId})

Cet endpoint doit permettre :
- récupérer et analyser les informations de son endpoint
- récupérer un pointset à partir de son id en communiquant avec le serveur point_set_manager
- analyser la réponse du serveur point_set_manager pour en déduire les points
- calcul les triangles issus des points trouvés
- formate les triangles trouvé pour les envoyer au client
- envoie au client

A partir du rôle de cet endpoint on peut en déduire les fonctions nécessaires : 

- recupPointSet(idPointSet) visant à récupérer notre poinset
- parsePointSet(byteResponse) permet la transformation des bytes renvoyés en points pour notre triangulation
- triangulation(List<Point>) calcul tous les triangles possibles issus des différents points de la liste
- parseTriangle(byteResponse,List<Triangle>) reprend notre pointset sous forme de byte et y ajoute les bytes nécessaire au 
  triangle

Ses fonctions devront forcément renvoyé des erreurs dans certains cas : 

- recupPointSet :
    - mauvais format d'id passé en paramètre
     Message Erreur : invalid PointSetID format
     Code : INVALID_ID_FORMAT
    - aucun poinset trouvé avec l'id donné
     Message Erreur : PointSet not found
     Code : NO_POINTSET_FOUND
    - aucune réponse du serveur
     Message Erreur : serveur indisponible 
     Code : NO_RESPONSE_SERVEUR

- parsePointSet : 
    - mauvais format de réponse
     Message Erreur : invalid response format
     Code : INVALID_RESPONSE_FORMAT
    - erreur lors de la lecture des informations
     Message Erreur : failed to decode points
     Code : DECODE_ERROR
    - mauvaise coordonnées trouvé pour le point
     Message Erreur : not able to read point coordinates
     Code : DECODE_ERROR

- triangulation : 
    - nombre insuffisant de point (moins de 3)
     Message Erreur : not enough points for a triangle
     Code : INVALID_POINTSET
    - impossible de former un triangle avec les points données (colinéaires)
     Message Erreur : no triangle can be build with PointSet
     Code : INVALID_POINTSET
    - erreur interne de l'algorithme
     Message Erreur : triangulation failed
     Code : ERROR_TRIANGULATION
    - mauvaise coordonnées de points
     Message Erreur : invalid points coordinates
     Code : INVALID_POINT

- parseTriangle : 
    - mauvais format de pointset
     Message Erreur : byte format pointset is invalid
     Code : INVALID_POINTSET_BYTE_FORMAT
    - mauvaise coordonnée des points formant le triangle
     Message Erreur : wrong coordinates for triangle
     Code : INVALID_TRIANGLE
    - les points utilisés sont colinéaires
     Message Erreur : points can't form a triangle
     Code : INVALID_TRIANGLE
    - échec de l'encodage
     Message Erreur : an error occured in the encodage
     Code : ENCODING_ERROR

A partir de ces informations on peut estimer les tests nécessaires pour chacune de ces fonctions et comment les réaliser : 

- recupPointSet
    - Test de comportement : 
        - cas testé :
        ID invalide
        - description :
        L’ID fourni ne respecte pas le format attendu
        - méthode :
        Appeler la fonction avec un ID vide ou un ID de mauvais type
        - attendu :
        Erreur INVALID_ID_FORMAT

        - cas testé :
        PointSet introuvable
        - description :
        Aucun pointset correspondant à l’ID donné
        - méthode :
        Simuler une réponse 404 du serveur point_set_manager à l'aide d'un mock
        - attendu :
        Erreur NO_POINTSET_FOUND

        - cas testé :
        Serveur indisponible
        - description :
        Le serveur ne répond pas ou timeout
        - méthode :
        Simuler une absence de réponse du serveur
        - attendu :
        Erreur NO_RESPONSE_SERVER

        - cas testé :
        Récupération réussie
        - description :
        Le pointset est correctement retourné par le serveur
        - méthode :
        Simuler une réponse serveur avec le pointset à l'aide d'un mock
        - attendu :
        Retour des bytes du pointset
    
    - Test de performance :
        - cas testé : 
         petit jeu de points
        - description : 
         Triangulation de 3 à 10 points aléatoires
        - méthode : 
         Générer un pointset aléatoire et mesurer le temps d’exécution
        - attendu : 
         Temps d’exécution rapide (ex : <10 ms)

        - cas testé : 
         jeu de points moyen
        - description : 
         Triangulation de 50 à 100 points aléatoires
        - méthode : 
         Générer un pointset de taille moyenne et mesurer le temps d’exécution
        - attendu : 
         Temps d’exécution raisonnable (ex : <200 ms)

        - cas testé : 
         jeu de points volumineux
        - description : 
         Triangulation de 500 à 1000 points
        - méthode : 
         Générer un pointset volumineux et mesurer le temps d’exécution
        - attendu : 
         La fonction termine sans crash, temps mesuré pour suivi des performances

        - cas testé : 
         points colinéaires
        - description : 
         Plus de 50 points alignés sur une même ligne
        - méthode : 
         Générer les points et exécuter la triangulation
        - attendu : 
         Fonction renvoie rapidement l’erreur INVALID_POINTSET

- parsePointSet :
    - cas testé :
     Format de réponse invalide
    - description :
     Les bytes reçus ne respectent pas la structure attendue
    - méthode :
     Utiliser un bytearray mal formé
    - attendu :
     Erreur INVALID_RESPONSE_FORMAT

    - cas testé :
     Erreur de décodage
    - description :
     Erreur dans la lecture des points
    - méthode :
     Envoyer un bytearray avec des tailles incorrectes
    - attendu :
     Erreur DECODE_ERROR

    - cas testé :
     Coordonnées invalides
    - description :
     Les coordonnées extraites ne sont pas valides
    - méthode :
     Forger un bytearray contenant des valeurs impossibles
    - attendu :
     Erreur DECODE_ERROR

    - cas testé :
     Décodage réussi
    - description :
     Le bytearray contient des points valides
    - méthode :
     Structure binaire correcte
    - attendu :
     Retour d’une liste de points

- triangulation : 
    - cas testé :
     Moins de 3 points
    - description :
     Impossible de construire un triangle
    - méthode :
     Liste contenant 0, 1 ou 2 points
    - attendu :
     Erreur INVALID_POINTSET

    - cas testé :
     Points colinéaires
    - description :
     Même si >3 points, aucun triangle possible
    - méthode :
     Liste contenant des points alignés (ex : (0,0), (1,1), (2,2))
    - attendu :
     Erreur INVALID_POINTSET

    - cas testé :
     Coordonnées invalides
    - description :
     Un point contient une valeur incohérente
    - méthode :
     Créer un point invalide dans la liste
    - attendu :
     Erreur INVALID_POINT

    - cas testé :
     Erreur interne
    - description :
     L’algorithme rencontre une exception imprévue
    - méthode :
     Mock d’une erreur interne dans la fonction
    - attendu :
     Erreur ERROR_TRIANGULATION

    - cas testé :
     Triangulation réussie
    - description :
     Les points permettent de produire au moins un triangle
    - méthode :
     Liste de 3+ points non colinéaires
    - attendu :
     Retour d’une liste de triangles

- parseTriangle : 
    - Test de Comportement : 
        - cas testé :
        PointSet byte invalide
        - description :
        Le pointset binaire ne respecte pas le format attendu
        - méthode :
        Envoyer un bytearray incomplet ou mal structuré
        - attendu :
        Erreur INVALID_POINTSET_BYTE_FORMAT

        - cas testé :
        Coordonnées invalides pour un triangle
        - description :
        Les indices ou points utilisés sont incorrects ou hors limite
        - méthode :
        Utiliser un triangle ayant des points avec des valeurs impossibles (Coordonnées invalides)
        - attendu :
        Erreur INVALID_TRIANGLE

        - cas testé :
        Triangle dégénéré / colinéaire
        - description :
        Les trois points utilisés ne peuvent pas former un triangle
        - méthode :
        Points identiques ou colinéaires dans un triangle
        - attendu :
        Erreur INVALID_TRIANGLE

        - cas testé :
        Erreur d’encodage
        - description :
        Problème lors de la construction du binaire final
        - méthode :
        Simuler un buffer incorrect
        - attendu :
        Erreur ENCODING_ERROR

        - cas testé :
        Encodage réussi
        - description :
        Le pointset est correctement complété avec les triangles
        - méthode :
        Bytearray pointset valide + liste de triangles valide
        - attendu :
        Retour du bytearray final
    - Test de Performance : 
        - cas testé :
         conversion petit pointset
        - description :
         Pointset avec 3-10 points et 1-5 triangles
        - méthode :
         Parser et encoder le pointset en mesurant le temps d’exécution
        - attendu :
         Temps <10 ms

        - cas testé :
         conversion pointset moyen
        - description :
         Pointset de 50 points avec 100 triangles
        - méthode :
         Parser et encoder le pointset en mesurant le temps
        - attendu :
         Temps d’exécution raisonnable (ex : <200 ms)

        - cas testé :
         conversion pointset volumineux
        - description :
         Pointset de 500 points avec triangles générés automatiquement
        - méthode :
         Parser et encoder le pointset
        - attendu :
         Fonction termine sans crash, temps mesuré pour suivi

        - cas testé :
         encodage points invalides
        - description :
         Pointset valide avec triangle invalide (colinéaire)
        - méthode :
         Parser et encoder le pointset
        - attendu :
         Fonction renvoie rapidement l’erreur INVALID_TRIANGLE