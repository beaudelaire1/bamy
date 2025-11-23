# Branding & white‑label

Le branding monoinstance est géré via le modèle `core.models.SiteSettings`
et le context processor `core.context_processors.brand` qui injecte :

- `COMPANY_NAME`
- `COMPANY_TAGLINE`
- `BRAND` (couleurs principales)

Pour rebrander une instance, créez/modifiez une instance de `SiteSettings`
dans l'admin Django, sans modifier le code.
