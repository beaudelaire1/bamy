# Flow de calcul des prix

Ce document décrit l'enchaînement des règles applicables lors du calcul
du prix unitaire final d'un produit dans Xeros B2B.  Le moteur de
tarification suit un ordre déterministe afin de garantir la
prévisibilité des tarifs proposés.

## Étapes du calcul

1. **Promotion catalogue ciblée** — via l'adaptateur de catalogue
   promotionnel `PromoCatalogPort`.  Si une promotion spécifique
   s'applique au produit pour un client donné, cette valeur l'emporte
   sur toutes les autres règles.

2. **Grille B2B** — application des règles de grille selon le
   `client_type` de l'utilisateur (`wholesaler`, `big_retail`,
   `small_retail`).  Un compte non vérifié entraîne une majoration
   automatique de +5 %.

3. **Promotion simple** — réduction directe via `discount_price`
   définie sur le modèle `Product`.  Elle n'est prise en compte
   qu'en l'absence de promotion catalogue ou de grille B2B.

4. **Prix public** — valeur de repli lorsque aucune règle
   supérieure ne s'applique.

5. **Règles avancées** — remises et contraintes appliquées a
   posteriori :

   - **Remise par quantité :** 10 % dès 50 unités, 20 % dès 100 unités.
   - **Remise par marque :** certaines marques (ex. `acme`) offrent
     5 % supplémentaires.
   - **Remise par famille de produits :** certaines catégories (ex.
     `Electronics`) accordent 3 % supplémentaires.
   - **Prix plancher :** le prix final ne descend jamais sous 70 %
     du prix public.

Ces règles avancées sont regroupées dans
`core.domain.pricing_rules.AdvancedPricingRules`.  Elles sont
automatiquement appliquées dans le service de prévisualisation via
`PricingEngine.determine_price_with_context`.
