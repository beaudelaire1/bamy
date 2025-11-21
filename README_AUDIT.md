
# Kit d'audit – Xeros (Django B2B)

## Contenu
- `audit_xeros.py` : Script unique pour analyser **l’arborescence**, **les URLs nommées**, les **settings** et repérer des anomalies classiques (Cart/checkout/paiements).
- Génère deux fichiers **dans votre projet** :
  - `audit_report.md` (rapport complet en Markdown)
  - `audit_findings.txt` (observations synthétiques)

## Pré-requis
- Python 3 installé.
- Placez **ces fichiers à la racine du projet** (là où se trouve `manage.py`).

## Utilisation
```bash
# Depuis la racine du projet
python audit_xeros.py
# ou, si le script est ailleurs :
python audit_xeros.py --root /chemin/vers/le/projet
```

## Ce que j’attends pour la suite
1. Exécutez le script.
2. Ouvrez `audit_report.md` et copiez-collez ici :
   - La section **3) URLs nommées détectées**.
   - La section **5) Observations rapides**.
3. On corrige ensemble `cart/`, `orders/` et les `urls` à partir de ces résultats.
