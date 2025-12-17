# Lancer tous les tests
test:
	pytest

# Lancer uniquement les tests unitaires (exclure les tests de performance)
unit_test:
	pytest -m "not perf"

# Lancer uniquement les tests de performance
perf_test:
	pytest -m "perf"

# Générer un rapport de couverture de code
coverage:
	coverage run -m pytest
	coverage report -m

# Vérifier la qualité du code
lint:
	ruff check .

# Générer la documentation
doc:
	pdoc3 --html --output-dir docs triangulation.py