from django.apps import AppConfig


class ClientsConfig(AppConfig):
    """Configuration for the clients app.

    By default Django will discover this app using the dotted path
    ``xeros_src.clients``.  It should be added to ``INSTALLED_APPS`` in
    ``xeros_project/settings.py``.
    """

    name = "clients"
    verbose_name = "Clients"
