
"""
Configuration des paramètres SMTP pour l'envoi de notifications par e-mail.

Ce module lit les variables d'environnement afin de récupérer les
informations sensibles (adresse e-mail et mot de passe). Il fournit
également des valeurs par défaut pour le serveur et le port SMTP.

Les variables d'environnement suivantes peuvent être définies :

* ``EMAIL_ADDRESS`` – adresse e-mail utilisée comme expéditeur
* ``EMAIL_PASSWORD`` – mot de passe ou token d'application pour l'e-mail
* ``EMAIL_SERVER`` – hôte du serveur SMTP (par défaut « smtp.gmail.com »)
* ``EMAIL_SERVER_PORT`` – port du serveur SMTP (par défaut 587)

En production, assurez-vous de définir ces variables dans votre fichier
.env ou dans l'environnement système afin de ne pas compromettre
vos identifiants.
"""

import os

# Utilise l'adresse e-mail configurée dans l'environnement ou None sinon.
config_email: str | None = os.getenv("EMAIL_ADDRESS")

# Mot de passe ou token d'application. Doit être défini pour permettre
# l'envoi d'e-mails. Ne versionnez jamais de mots de passe en clair.
config_password: str | None = os.getenv("EMAIL_PASSWORD")

# Serveur SMTP, par défaut Gmail. Personnalisez selon votre fournisseur.
config_server: str = os.getenv("EMAIL_SERVER", "smtp.gmail.com")

# Port SMTP, 587 pour TLS ou 465 pour SSL. 587 est le port par défaut.
try:
    config_server_port: int = int(os.getenv("EMAIL_SERVER_PORT", "587"))
except ValueError:
    config_server_port = 587

