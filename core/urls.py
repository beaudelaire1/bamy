from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy_policy, name="privacy"),
    path("cookies/", views.cookies_policy, name="cookies"),
    path("contact/", views.contact, name="contact"),
    # La route de recrutement générique a été retirée au profit de l'application
    # dédiée ``recruitment``. Les offres d'emploi et les candidatures
    # sont maintenant gérées par ``recruitment.urls`` déclaré dans
    # ``xeros_project/urls.py``. Conservez cette ligne commentée pour
    # référence si vous souhaitez réactiver le formulaire générique.
    # path("recruitment/", views.recruitment, name="recruitment"),
]
