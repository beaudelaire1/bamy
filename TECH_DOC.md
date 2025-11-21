# Documentation technique

Ce document présente l’architecture générale du projet **Xeros**, les instructions de déploiement et les bonnes pratiques à suivre pour maintenir et faire évoluer la plateforme. Il constitue une base pour l’équipe de développement et les administrateurs système.

## 1. Architecture applicative

### 1.1 Panorama des applications Django

Le projet est structuré en une collection d’applications découplées, chacune ayant une responsabilité claire :

| Application    | Responsabilité principale                                        |
|---------------|------------------------------------------------------------------|
| **core**      | Pages génériques (home, pages légales), composants communs      |
| **catalog**   | Catalogue produits (catégories, marques, produits, wishlist)    |
| **cart**      | Gestion du panier, calcul des totaux, application de coupons    |
| **orders**    | Processus de commande (checkout), modèles `Order` et `OrderItem` |
| **crm**       | Gestion des clients et prospects, formulaires de contact et devis |
| **notifications** | Envoi de notifications internes aux utilisateurs            |
| **integrations** | Import de produits (commandes de management), connecteurs    |
| **payments**  | Intégration des prestataires de paiement (PayPal, Stripe)        |
| **loyalty**   | Programme de fidélité (points, coupons)                          |
| **marketing** | Tâches marketing asynchrones (paniers abandonnés, newsletters)   |
| **returns**   | Gestion des demandes de retour de produits                        |
| **reviews**   | Avis et notations des produits                                   |
| **userauths** | Authentification, enregistrement, adresses et gestion du profil |

Ces applications communiquent via des imports et des clés étrangères. La séparation respecte les principes *single responsibility* et facilite la maintenance.

### 1.2 Services externes

- **PayPal & Stripe** : les modules `payments.paypal` et `payments.stripe_api` encapsulent les appels aux API. La configuration (clés secrètes) est lue depuis `settings.py` ou les variables d’environnement.
- **Celery** : les tâches longues ou planifiées (marketing) sont exécutées via Celery. Le fichier `xeros_project/celery.py` configure un *worker* et doit être démarré séparément.

### 1.3 Modèle de données

Le modèle principal est `Order`, qui regroupe toutes les informations relatives à une commande (utilisateur, coordonnées, totaux, statut). Chaque commande comporte des `OrderItem` pour détailler les lignes d’achat. Des relations existent avec :

- `LoyaltyAccount` (programme de fidélité)
- `Coupon` (remises)
- `Payment` (transaction de paiement – nouveau modèle ajouté)

Les produits sont définis dans `catalog.models.Product` et peuvent être filtrés par catégorie et marque. Le panier est une structure stockée en session via la classe `cart.Cart`.

## 2. Déploiement et configuration

### 2.1 Pré‑requis

- **Python ≥3.10**
- **Django ≥4.0**
- Un serveur de base de données (SQLite est utilisé pour le développement ; en production privilégier PostgreSQL ou MySQL).
- Des clés API pour les services de paiement (STRIPE_SECRET_KEY, PAYPAL_CLIENT_ID, PAYPAL_SECRET).
- Un broker pour Celery (ex. Redis) si les tâches asynchrones sont activées.

### 2.2 Installation

1. Cloner le dépôt et créer un environnement virtuel :

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Créer un fichier `xeros_project/local_settings.py` pour y stocker les paramètres sensibles et spécifiques à l’environnement :

   ```python
   SECRET_KEY = "…"
   DEBUG = False
   ALLOWED_HOSTS = ["example.com"]

   STRIPE_SECRET_KEY = "sk_live_…"
   PAYPAL_CLIENT_ID = "…"
   PAYPAL_SECRET = "…"

   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": "xeros",
           "USER": "xeros",
           "PASSWORD": "…",
           "HOST": "localhost",
           "PORT": "5432",
       }
   }

   CACHES = {
       "default": {
           "BACKEND": "django.core.cache.backends.redis.RedisCache",
           "LOCATION": "redis://127.0.0.1:6379/1",
       }
   }
   ```

3. Appliquer les migrations et collecter les fichiers statiques :

   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

4. Créer un superutilisateur pour accéder à l’interface d’administration :

   ```bash
   python manage.py createsuperuser
   ```

5. (Optionnel) Démarrer le worker Celery :

   ```bash
   celery -A xeros_project worker -l info
   ```

### 2.3 Paramètres de sécurité

Pour un déploiement en production, activez les options suivantes dans `local_settings.py` :

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
``` 

Définissez également `CSRF_TRUSTED_ORIGINS` si la plateforme est derrière un proxy ou un CDN.

## 3. Bonnes pratiques de développement

- **Tests** : utilisez `pytest` ou `django.test` pour valider les comportements critiques. Les tests existants (`catalog/tests`, `orders/tests`, `userauths/tests`) fournissent des exemples.
- **Linters** : intégrez `flake8` et `black` dans votre pipeline CI pour garantir un code propre et cohérent.
- **Sérialisation** : pour exposer des API publiques, privilégiez `django-rest-framework` et respectez les principes REST.
- **Journalisation** : configurez `LOGGING` dans `settings.py` afin de centraliser les logs (format JSON, rotation de fichiers). Les échecs de paiement ou les exceptions doivent être monitorés.
- **Mises à jour** : surveillez les versions des dépendances (Django, Celery, Stripe, PayPal SDK) et appliquez rapidement les correctifs de sécurité.

## 4. Perspectives d’évolution

La plateforme est conçue de manière modulaire. L’ajout de nouvelles applications (par ex. un module d’offres promotionnelles, une API GraphQL) se fait en déclarant l’application dans `INSTALLED_APPS` et en suivant la convention des URL namespacing pour éviter les collisions.

Des recommandations pour des fonctionnalités innovantes sont disponibles dans `INNOVATION.md`.

---

Cette documentation doit être enrichie au fur et à mesure de l’évolution du projet. N’hésitez pas à ajouter des diagrammes d’architecture, des exemples de commandes ou des procédures spécifiques à vos déploiements (CI/CD, infrastructure as code).