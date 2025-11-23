# API v1 – Endpoints principaux

L'API REST est exposée sous le préfixe `/api/` lorsque `ENABLE_REST_API=True`.

## Authentification

- `POST /api/auth/login/` : obtention d'un couple (access, refresh) JWT.
- `POST /api/auth/refresh/` : rafraîchissement du token d'accès.

## Panier

- `GET /api/cart/` : récupération du panier courant.
- `POST /api/cart/add/` : ajout d'un article au panier.
- `POST /api/cart/clear/` : vidage du panier.
- `POST /api/cart/checkout/` : création d'une commande à partir du panier.

## Produits

- `GET /api/products/search/?q=...` : recherche rapide de produits.
