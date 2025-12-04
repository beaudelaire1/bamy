# Flow de devis et commandes

Cette documentation décrit le processus de création d'un devis et sa
transformation en commande dans Xeros B2B.

## Création d'un devis

1. Un utilisateur connecté choisit un client (s'il appartient à
   plusieurs organisations) et sélectionne les produits et
   quantités souhaités.

2. Une requête `POST /api/quotes/` est envoyée avec la liste des
   lignes.  Le sérialiseur `QuoteSerializer` crée le devis et
   calcule les prix unitaires via le service de pricing
   (`pricing_service.preview_price`).  Les montants sont figés sur
   chaque ligne (`unit_price`, `line_total`) afin de garantir la
   traçabilité.

3. Le devis est enregistré avec le statut **Brouillon**.  L'utilisateur
   peut ajouter des notes ou modifier les quantités avant d'envoyer le
   devis pour validation.

## Validation du devis

1. Un manager ou un utilisateur autorisé via le rôle "admin"
   sélectionne le devis et le marque comme **En attente de
   validation**.

2. Après vérification (cohérence des prix, disponibilité stock,
   approbation commerciale), le manager peut approuver le devis.

3. L'approbation du devis déclenche la création d'une commande.  Les
   lignes du devis sont copiées dans `Order` et `OrderItem`.  Le
   statut du devis passe à **Transformé en commande**.

## Historique des prix

Les prix appliqués au moment de la création du devis sont conservés
dans les champs `unit_price` et `line_total` de `QuoteItem`.  Lors de
la transformation en commande, ces valeurs sont copiées dans
`OrderItem` afin de conserver un historique des conditions tarifaires.
