# Flow de gestion des promotions

Ce document décrit comment les promotions sont modélisées et appliquées
dans Xeros B2B.

## Modélisation

Les promotions sont gérées via un adaptateur (`PromoCatalogPort`) qui
permet d'interroger un catalogue externe (par exemple un ERP) afin de
déterminer si un produit bénéficie d'un prix promotionnel pour un
client donné.  Cette approche en port/adaptateur permet de
substituer facilement l'implémentation (cache Redis, API distante,
fichier local, etc.).

## Publication

Un gestionnaire de promotions peut créer ou importer des promotions
dans le catalogue.  Avant publication, un validateur anti‑conflit
vérifie qu'il n'existe pas déjà une promotion active sur la même
période pour le même produit ou le même client.  En cas de collision,
la publication est bloquée et un rapport est affiché.

## Application

Lors du calcul de prix, la première étape consiste à consulter
l'adaptateur de promo (`promo_port.get_applicable_promo`).  Si une
promotion est retournée, son montant est utilisé directement comme
prix final.  Les autres règles de tarification sont alors ignorées.

## API de diagnostic

Une API `GET /promotions/check/` (non implémentée ici) peut être
exposée pour diagnostiquer les conflits de promotions.  Elle
renverrait la liste des promotions actives, expirées et futures,
ainsi que les éventuels chevauchements détectés.
