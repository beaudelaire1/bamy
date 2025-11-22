from pathlib import Path
import os

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
SECRET_KEY = env("SECRET_KEY", default="unsafe")
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

    # nouvelles apps internes
    "crm",
    "notifications",
    "integrations",

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

    # Activation du framework sitemap pour SEO
    "django.contrib.sitemaps",
]

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# API REST conditionnelle
#
# Le support de l'API REST (djangorestframework + app interne "api") est
# activé uniquement si deux conditions sont remplies :
#   1. La bibliothèque ``djangorestframework`` est installée et compatible.
#   2. La variable d'environnement ``ENABLE_REST_API`` est définie à ``True``.
#
# Cette approche évite les erreurs ImportError (par exemple
# ``parse_header_parameters`` manquant) lorsque ``rest_framework`` est installé
# mais incompatible avec la version de Django utilisée.  En définissant
# ENABLE_REST_API=True dans l'environnement, vous forcez l'activation de l'API
# REST ; sinon, elle reste désactivée par défaut.

ENABLE_REST_API = False
try:
    # Vérifie si l'utilisateur souhaite activer l'API REST via variable d'env.
    # Utilise la méthode .bool du fallback/env pour interroger la variable.
    ENABLE_REST_API = env.bool("ENABLE_REST_API", default=False)  # type: ignore[attr-defined]
except Exception:
    # Si env.bool n'est pas disponible (fallback minimal), ignore.
    ENABLE_REST_API = False

if ENABLE_REST_API:
    try:
        import rest_framework  # type: ignore
        # Si l'import réussit, on ajoute les apps nécessaires.
        INSTALLED_APPS += ["rest_framework", "api"]
    except Exception:
        # Si rest_framework est absent ou incompatible, ne pas activer l'API
        # et ne pas lever d'erreur. L'utilisateur devra installer une version
        # compatible ou désactiver ENABLE_REST_API.
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
        # Ajout explicite du nom de l'engin pour éviter l'erreur
        # KeyError: 'django' lors de la recherche d'un moteur de template.
        # Par défaut, Django utilise l'alias "django" si NAME n'est pas fourni.
        # Toutefois, certaines installations peuvent rencontrer un KeyError
        # si cette clef est absente. Nous l'indiquons donc explicitement.
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
                "cart.context_processors.cart",  # <- panier global
                "payments.context_processors.payment_public_keys",  # <- clés publiques de payement

            ],
            # <- pour utiliser le filtre "currency" partout
            "builtins": ["core.templatetags.compat"],
        },
    },
]

WSGI_APPLICATION = "xeros_project.wsgi.application"

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

AUTH_USER_MODEL = "userauths.User"  # Custom user dès le départ

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------------------------------------------------
# Paramètres reCAPTCHA
#
# Pour activer la protection anti‑robot, définissez dans votre fichier .env
# RECAPTCHA_PUBLIC_KEY et RECAPTCHA_PRIVATE_KEY selon les clés fournies par
# Google.  Les formulaires de contact et de demande de devis vérifieront
# automatiquement les jetons reCAPTCHA.  Par défaut, aucune clé n'est
# définie afin de ne pas bloquer le développement local.
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY", default=None)
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY", default=None)

# -----------------------------------------------------------------------------
# Emails et contacts internes
#
# Pour les formulaires de contact et de demande de devis, nous définissons
# l'adresse d'expédition par défaut ainsi que la liste de diffusion interne.
# Ces valeurs peuvent être surchargées via des variables d'environnement.
# Par défaut, en environnement de développement, l'email est envoyé vers
# ``console.EmailBackend`` qui affiche les messages dans la console.
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@xeros.local")
INTERNAL_CONTACTS = env.list("INTERNAL_CONTACTS", default=["contact@xeros.local"])

# Utilise l'email backend console en développement pour ne pas envoyer
# réellement les courriels. Vous pouvez surcharger EMAIL_BACKEND dans
# votre .env pour utiliser SMTP en production.
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# Whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------------------------------------------
# Configuration de Celery
#
# Ces paramètres déterminent comment Celery se connecte au broker
# de messages et comment les résultats sont stockés.  Ils sont
# chargés via la bibliothèque django-environ (voir ``env``).  Par
# défaut, Celery utilisera Redis sur localhost si aucune variable
# d'environnement n'est définie.  Modifiez ``CELERY_BROKER_URL`` et
# ``CELERY_RESULT_BACKEND`` dans votre fichier .env pour pointer vers
# votre infrastructure (Redis, RabbitMQ, etc.).
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

# Pour les environnements de développement, on peut exécuter les
# tasks immédiatement et de manière synchrone en activant la
# configuration suivante.  Ce comportement est contrôlé via la
# variable d'environnement ``CELERY_TASK_ALWAYS_EAGER`` ou, par
# défaut, via la valeur de DEBUG.
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=DEBUG)

# Tentative d'import de la bibliothèque Redis.  Si elle n'est pas
# installée, on bascule automatiquement Celery sur un broker en mémoire,
# ce qui permet d'exécuter les tâches sans dépendance externe.  Pour
# une utilisation en production, installez le paquet `redis` (python
# redis-py) et lancez un serveur Redis, puis définissez les variables
# CELERY_BROKER_URL et CELERY_RESULT_BACKEND dans votre fichier .env.
try:
    import redis  # noqa: F401
except ImportError:
    # Aucun module redis : utiliser un broker en mémoire
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
    "site_logo": None,  # on ajoutera plus tard
    "show_ui_builder": False,
    # Ajout d'un lien vers le site public dans le menu supérieur de l'admin
    # Ce lien s'ouvre dans une nouvelle fenêtre et permet aux administrateurs
    # de consulter rapidement la boutique B2B.
    "topmenu_links": [
        {
            "name": "Aller au site",
            "url": "/",  # URL racine du site
            "new_window": True,
        },
    ],

    # Icônes modernes pour les applications de l'admin. Ces classes FontAwesome
    # sont utilisées par Jazzmin pour illustrer les menus. Vous pouvez
    # ajuster les classes selon vos préférences (fa-solid, fa-regular…).
    "icons": {
        "auth": "fas fa-user-shield",
        "catalog": "fas fa-box-open",
        "cart": "fas fa-shopping-basket",
        "orders": "fas fa-receipt",
        "crm": "fas fa-address-card",
        "marketing": "fas fa-bullhorn",
        "notifications": "fas fa-bell",
        "returns": "fas fa-undo",
        "recruitment": "fas fa-briefcase",
        "loyalty": "fas fa-gift",
        "userauths": "fas fa-users",
    },
}
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14   # 14 jours si "remember" coché (par défaut)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # sera forcé à True au cas par cas via la vue

# Utiliser l'URL nommée de l'application userauths pour éviter les collisions.
LOGIN_URL = "userauths:login"
# LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

# Emails (dev) : les emails de reset s’affichent en console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# (Optionnel) durcir les mots de passe en prod, mettre des validateurs ici
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

# app session_id
CART_SESSION_ID = "cart"
# CORE_SESSION_ID = "core"
# CATALOG_SESSION_ID = "catalog"

# methode de payement avec stripe
# Stripe

try:
    from .local_settings import *
except ImportError:
    pass

# -------------------------------------------------------------------
# Cache configuration
#
# En environnement de développement, nous utilisons un cache en mémoire.  Pour
# la production, configurez un backend Redis ou Memcached via les variables
# d'environnement ou un fichier local_settings.py.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "xeros-cache",
    }
}

# -------------------------------------------------------------------
# Observabilité : intégration Sentry facultative
#
# Si la variable d'environnement ``SENTRY_DSN`` est définie, Sentry est
# initialisé pour capturer les erreurs et exceptions non interceptées.
# Le taux d'échantillonnage des traces APM peut être ajusté via
# ``SENTRY_TRACES_SAMPLE_RATE``.  Lorsque Sentry n'est pas installé ou
# qu'aucune DSN n'est fournie, cette section est ignorée.
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
        # Sentry n'est pas disponible ; vous pouvez installer le paquet
        # ``sentry-sdk`` pour activer l'envoi des erreurs en production.
        pass

# -------------------------------------------------------------------
# Sécurité en production
# Ces paramètres renforcent la sécurité lorsque DEBUG est à False.
# Ils redirigent les requêtes HTTP vers HTTPS, configurent des entêtes
# HSTS et sécurisent les cookies de session et CSRF. La liste des
# origines CSRF de confiance peut être définie via la variable
# d'environnement `CSRF_TRUSTED_ORIGINS`.
if not DEBUG:
    # Force les redirections vers HTTPS
    SECURE_SSL_REDIRECT = True
    # Durée (en secondes) du HSTS, ici 30 jours
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Cookies sécurisés : uniquement envoyés via HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Origines autorisées pour les requêtes CSRF (via environ)
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

    # Politique SameSite pour les cookies (protège contre le CSRF de navigation
    # inter-sites).  Les valeurs possibles sont "Lax", "Strict" ou "None" (ce
    # dernier nécessite un cookie sécurisé).  On utilise Lax par défaut.
    SESSION_COOKIE_SAMESITE = env("SESSION_COOKIE_SAMESITE", default="Lax")
    CSRF_COOKIE_SAMESITE = env("CSRF_COOKIE_SAMESITE", default="Lax")

    # Empêche la mise en cache du contenu mixte ou l'interprétation
    # de fichiers CSS/JS mal typés par le navigateur.
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Active le filtre XSS (les navigateurs modernes l'ignorent mais ne
    # gêne pas).
    SECURE_BROWSER_XSS_FILTER = True

    # Interdit l'intégration du site dans des frames externes (clickjacking)
    X_FRAME_OPTIONS = "DENY"







