from pathlib import Path
import os
import sys  # pour vérifier les arguments de la ligne de commande

"""
Importation de la bibliothèque ``django-environ`` (alias ``environ``).

Certaines distributions Windows livrent un module ``environ`` hérité de
Python 2 qui n'est pas compatible avec Django (il déclenche une
``SyntaxError``).  Nous essayons d'abord d'importer la bonne
bibliothèque `django-environ`.  En cas d'échec, nous fournissons une
implémentation minimale ``_EnvFallback`` qui expose les méthodes
nécessaires (`__call__`, `bool`, `list`) pour lire les variables
d'environnement.  Cela permet de lancer le projet sans la dépendance
environ.
"""

try:
    # Essayons d'importer la bonne bibliothèque django-environ.  On l'alias
    # en préfixant par un underscore pour éviter toute confusion avec la
    # classe fallback définie plus bas.  Certaines distributions Windows
    # embarquent un module ``environ`` incompatible qui déclenche des
    # ``SyntaxError`` sous Python 3.  Cette clause protège donc contre
    # l'import de ce module héritage.
    import environ as _environ  # type: ignore[import]

    _has_environ = True
except Exception:
    # Le module django-environ n'est pas disponible ou pose problème.
    # Nous définissons `_has_environ` à False et utiliserons une
    # implémentation de secours plus bas.
    _has_environ = False


class _EnvFallback(dict):
    """
    Fallback de lecture des variables d'environnement.

    Cette classe fournit une interface minimaliste compatible avec
    ``django-environ``.  Si le package ``django-environ`` n'est pas
    disponible, ``env('VAR')`` continue de fonctionner en allant lire
    directement les variables d'environnement via ``os.environ``.

    - ``__call__(key, default=None)`` renvoie la valeur de ``key``
      depuis ``os.environ`` ou ``default``.
    - ``bool(key, default=False)`` convertit la valeur de ``key`` en
      booléen en interprétant ``"1"``, ``"true"``, ``"yes"`` et
      ``"on"`` comme ``True``.
    - ``list(key, default=None, sep=',')`` découpe la chaîne en liste
      en utilisant ``sep`` comme séparateur.
    """

    def __call__(self, key: str, default=None):
        val = os.environ.get(key)
        # Pour certaines variables critiques (comme SECRET_KEY),
        # on préfère échouer bruyamment plutôt que d'utiliser une
        # valeur de repli silencieuse.
        if val is None and key == "SECRET_KEY":
            from django.core.exceptions import ImproperlyConfigured

            raise ImproperlyConfigured(
                "SECRET_KEY must be defined in the environment or .env file.",
            )
        return val if val is not None else default

    def bool(self, key: str, default: bool = False):
        val = os.environ.get(key)
        if val is None:
            return default
        return str(val).strip().lower() in {"1", "true", "yes", "on"}

    def list(self, key: str, default=None, sep=","):
        val = os.environ.get(key)
        if val is None:
            return default if default is not None else []
        return [item.strip() for item in val.split(sep) if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent
if _has_environ:
    # Si django-environ est disponible, on instancie l'objet Env et on lit
    # les variables depuis le fichier .env (s'il existe).
    env = _environ.Env(
        DEBUG=(bool, True),
    )
    # Lecture du fichier .env placé à la racine du projet.  Si le fichier
    # n'existe pas, cette fonction ne fera rien.
    _environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
else:
    # Fallback : on utilise la classe _EnvFallback qui lit directement
    # les variables d'environnement sans support du fichier .env.
    env = _EnvFallback()

# Paramètres de base récupérés depuis l'environnement ou valeurs par défaut
# DEBUG est activé par défaut afin de faciliter le développement et le débogage.
# Vous pouvez toujours le désactiver via la variable d'environnement DEBUG=False.
DEBUG = env("DEBUG", default=True) if _has_environ else env.bool("DEBUG", default=True)
SECRET_KEY = env("SECRET_KEY")
_allowed_hosts = env("ALLOWED_HOSTS", default="")
if isinstance(_allowed_hosts, str):
    ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = list(_allowed_hosts)  # déjà liste

INSTALLED_APPS = [
    "jazzmin",  # avant django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # apps du projet
    "core",
    "userauths",
    "catalog",
    "cart",
    "orders",
    "crm",

    # Gestion des organisations clientes et multi‑utilisateur
    "clients",
    #"xeros_project.clients",


    # Module de devis et commandes B2B
    "quotes",

    # apps avec appel via api tiers
    "payments",

    # Avis, fidélité et retours
    "reviews",
    "loyalty",
    "returns",

    # Marketing et campagnes
    "marketing",

    # Application de gestion des offres d'emploi et des candidatures
    "recruitment",

    "django_ckeditor_5",

    # Gestion des sites (multi‑domaines)
    "api",
    "integrations",
    "notifications",

    # Import/export permet l'importation et l'exportation de données
    # depuis l'administration (CSV, XLSX). Vous devrez installer
    # django-import-export via pip pour activer ces fonctionnalités.
    "import_export",

    # Activation du framework sitemap pour SEO
    "django.contrib.sitemaps",
]

# -----------------------------------------------------------------------------
# API REST conditionnelle
# -----------------------------------------------------------------------------
ENABLE_REST_API = False
try:
    # Vérifie si l'utilisateur souhaite activer l'API REST via variable d'env.
    ENABLE_REST_API = env.bool("ENABLE_REST_API", default=False)  # type: ignore[attr-defined]
except Exception:
    ENABLE_REST_API = False

if ENABLE_REST_API:
    try:
        import rest_framework  # type: ignore

        # Si l'import réussit, on ajoute les apps nécessaires.
        INSTALLED_APPS += ["rest_framework", "rest_framework_simplejwt", "api"]
    except Exception:
        pass

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "xeros_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "NAME": "django",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.brand",  # <- branding global
                "core.context_processors.branding",  # injecte l'objet BrandingConfig
                "cart.context_processors.cart",  # <- panier global
                "payments.context_processors.payment_public_keys",  # <- clés publiques de payement
            ],
            "builtins": ["core.templatetags.compat"],
        },
    },
]

WSGI_APPLICATION = "xeros_project.wsgi.application"

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

# -----------------------------------------------------------------------------
# Mise en cache globale Redis
# -----------------------------------------------------------------------------
# Un cache Redis est utilisé pour accélérer les opérations de calcul de prix
# et stocker temporairement les catalogues et grilles tarifaires.  La
# variable d'environnement ``REDIS_URL`` peut être définie pour
# personnaliser l'URL de connexion.  En l'absence de configuration,
# Django utilisera un backend locmem par défaut.
try:
    REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/0")  # type: ignore[attr-defined]
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
except Exception:
    # Fallback simple : cache en mémoire locale (non partagé entre processus)
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "xeros-cache",
        }
    }

AUTH_USER_MODEL = "userauths.User"  # Custom user dès le départ

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------------------------------------------------
# Paramètres reCAPTCHA
# -----------------------------------------------------------------------------
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY", default=None)
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY", default=None)

# -----------------------------------------------------------------------------
# Emails et contacts internes
# -----------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@xeros.local")
INTERNAL_CONTACTS = env.list("INTERNAL_CONTACTS", default=["contact@xeros.local"])

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# Whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------------------------------------------
# Configuration de Celery
# -------------------------------------------------------------------
CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL",
    default="redis://localhost:6379/0",
)
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND",
    default="redis://localhost:6379/0",
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=DEBUG)

try:
    import redis  # noqa: F401
except ImportError:
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'

# Branding (pour Jazzmin & templates)
COMPANY_NAME = env("COMPANY_NAME", default="BamyTest")
COMPANY_TAGLINE = env("COMPANY_TAGLINE", default="Grossiste")
BRAND = {
    "PRIMARY": env("BRAND_PRIMARY", default="#0905f5"),
    "ACCENT": env("BRAND_ACCENT", default="#D4AF37"),
    "DARK": env("BRAND_DARK", default="#2D2D2D"),
    "LIGHT": env("BRAND_LIGHT", default="#F8F9FA"),
}

# Jazzmin (admin premium, cf. cahier)
JAZZMIN_SETTINGS = {
    "site_title": COMPANY_NAME,
    "site_header": COMPANY_NAME,
    "site_brand": COMPANY_NAME,
    "welcome_sign": f"Bienvenue chez {COMPANY_NAME}",
    "site_logo": None,
    "show_ui_builder": True,
    "topmenu_links": [
        {
            "name": "Voir le site",
            "url": "/",
            "new_window": True,
        },
        {
            "name": "Rapport des ventes",
            "url": "/admin/orders/order/report/",
            "new_window": False,
        },
    ],

    # Icônes modernes pour les applications de l'admin
    "icons": {
        "auth": "fas fa-users-cog",
        "userauths": "fas fa-user-shield",
        "catalog": "fas fa-store",
        "cart": "fas fa-shopping-basket",
        "orders": "fas fa-file-invoice",
        "marketing": "fas fa-bullhorn",
        "returns": "fas fa-undo-alt",
        "recruitment": "fas fa-briefcase",
        "loyalty": "fas fa-award",
        "reviews": "fas fa-star-half-alt",
        "payments": "fas fa-credit-card",
        "core": "fas fa-cogs",
    },

    # Icônes spécifiques pour chaque modèle (app_label.model_name en minuscules)
    "model_icons": {
        # --- AUTH & UTILISATEURS ---
        "auth.group": "fas fa-users",
        "userauths.user": "fas fa-user-tie",  # Utilisateur Custom
        "userauths.address": "fas fa-map-marked-alt",

        # --- CATALOGUE ---
        "catalog.category": "fas fa-layer-group",
        "catalog.brand": "fas fa-copyright",
        "catalog.product": "fas fa-box-open",
        "catalog.productimage": "fas fa-images",

        # --- COMMANDES & PANIER ---
        "orders.order": "fas fa-file-invoice-dollar",
        "orders.orderitem": "fas fa-list-ol",
        "cart.cart": "fas fa-shopping-cart",

        # --- PAIEMENTS ---
        "payments.payment": "fas fa-money-check-alt",

        # --- MARKETING & FIDÉLITÉ ---
        "marketing.campaign": "fas fa-bullhorn",
        "loyalty.loyaltyaccount": "fas fa-gift",
        "loyalty.reward": "fas fa-trophy",

        # --- AVIS & RETOURS ---
        "reviews.review": "fas fa-star",
        "returns.returnrequest": "fas fa-undo",

        # --- RECRUTEMENT ---
        "recruitment.jobposting": "fas fa-briefcase",
        "recruitment.jobapplication": "fas fa-file-contract",

        # --- CORE / CONFIGURATION ---
        "core.brandingconfig": "fas fa-paint-roller",
        "core.page": "fas fa-file-alt",
        "sites.site": "fas fa-globe",
    },

    # Ajoute un CSS personnalisé pour harmoniser Jazzmin
    "custom_css": "css/admin-overrides.css",

    # Recherche globale
    "search_model": ["catalog.Product", "orders.Order", "userauths.User"],
}

SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 jours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

LOGIN_URL = "userauths:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": ["bold", "italic", "link", "bulletedList", "numberedList", "blockQuote"],
        "language": "fr",
    }
}

CART_SESSION_ID = "cart"

try:
    from .local_settings import *
except ImportError:
    pass

# -------------------------------------------------------------------
# Cache configuration
# -------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "xeros-cache",
    }
}

# -------------------------------------------------------------------
# Observabilité : intégration Sentry facultative
# -------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default=None)
if SENTRY_DSN:
    try:
        import sentry_sdk  # type: ignore
        from sentry_sdk.integrations.django import DjangoIntegration  # type: ignore

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(env("SENTRY_TRACES_SAMPLE_RATE", default=0.0)),
            send_default_pii=True,
        )
    except Exception:
        pass

# -------------------------------------------------------------------
# Sécurité en production
# -------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
    SESSION_COOKIE_SAMESITE = env("SESSION_COOKIE_SAMESITE", default="Lax")
    CSRF_COOKIE_SAMESITE = env("CSRF_COOKIE_SAMESITE", default="Lax")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"

# Configuration Django REST Framework + JWT
from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
}

# API toujours activée en mode test
if os.environ.get("DJANGO_TEST", "") == "true":
    ENABLE_REST_API = True

# Active automatiquement l'API pendant les tests
if 'test' in sys.argv:
    ENABLE_REST_API = True