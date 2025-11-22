"""Vues de l'application de fidélité.

Cette vue fournit une page publique décrivant le programme de fidélité de
la plateforme B2B. Les clients peuvent y consulter les avantages,
conditions et modalités d'inscription au programme.
"""

from django.shortcuts import render


def program(request):
    """Affiche la page du programme de fidélité.

    Cette page présente les avantages du programme de fidélité et
    explique comment les clients peuvent collecter et utiliser leurs
    points ou remises.
    """
    return render(request, "loyalty/program.html")