# Architecture hexagonale – Xeros B2B

Ce projet adopte progressivement une architecture hexagonale (ports & adapters).

- Les **interfaces de domaine** (ports) sont définies dans `core/interfaces.py`.
- Les **services métier** (cas d'usage) sont regroupés dans `core/services/`.
- Les **adapters d'infrastructure** (Django ORM, panier session) sont dans `core/repositories/`.
- Le module `core/factory.py` fournit une fabrique centralisée pour instancier les services.
