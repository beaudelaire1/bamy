"""
Celery tasks for the integrations app.

This module defines asynchronous tasks used to process import jobs
submitted via the admin interface.  Each task receives the primary
key of an :class:`~integrations.models.ImportTask` instance, reads
the associated file and creates or updates products accordingly.  It
supports Excel, CSV and JSON formats via the pandas library.

When the task finishes, it updates the status and counters on the
``ImportTask`` instance.  Any encountered errors are aggregated into
the ``errors`` field for display to the user.
"""

from celery import shared_task
import pandas as pd
from django.utils.text import slugify
from django.utils import timezone

from .models import ImportTask
from catalog.models import Product, Category, Brand


@shared_task
def process_import_task(task_id: int) -> None:
    """Traite un fichier d'import de produits.

    Cette tâche est appelée de manière asynchrone via Celery.  Elle
    récupère l'instance :class:`ImportTask` associée, lit le fichier
    (Excel, CSV ou JSON) et crée ou met à jour des produits.  Les
    catégories et marques sont créées à la volée si nécessaire.

    :param task_id: identifiant de la tâche d'import à traiter
    """
    import_task = ImportTask.objects.get(id=task_id)
    import_task.status = 'processing'
    import_task.save(update_fields=['status'])

    def normalise_dict(record: dict) -> dict:
        """Renvoie un dictionnaire avec des clés normalisées.

        Les clés sont transformées en minuscules, les espaces et
        underscores sont supprimés pour permettre une correspondance plus
        souple des colonnes dans les différents formats de fichiers.
        """
        return {k.strip().lower(): v for k, v in record.items()}

    try:
        # Charger les données du fichier
        path = import_task.file.path
        ext = path.lower().rsplit('.', 1)[-1]
        records = []
        if ext in {'xls', 'xlsx'}:
            df = pd.read_excel(path, sheet_name=0)
            records = df.to_dict(orient='records')
        elif ext in {'csv', 'tsv'}:
            import csv
            delimiter = ',' if ext == 'csv' else '\t'
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                records = list(reader)
        elif ext in {'json', 'js', 'txt'}:
            import json
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    records = data.get('products', [])
                elif isinstance(data, list):
                    records = data
                else:
                    raise ValueError('Format JSON inattendu : liste ou objet requis.')
        else:
            raise ValueError('Format de fichier non pris en charge.')

        success = 0
        failure = 0
        errors = []

        for idx, row in enumerate(records, start=1):
            try:
                # Normaliser les noms de colonnes
                data = normalise_dict(row)

                # Champ identifiant du produit
                art_code = data.get('code article') or data.get('article_code') or data.get('code_article') or data.get('sku')
                if not art_code:
                    raise ValueError("'code article' manquant.")

                # Nom complet (désignation)
                designation = (
                    data.get('designation')
                    or data.get('désignation')
                    or data.get('nom')
                    or data.get('title')
                )
                if not designation:
                    raise ValueError("'designation' manquant.")

                # Stock
                stock_val = data.get('stock') or data.get('quantite') or data.get('quantité')
                if stock_val is None:
                    raise ValueError("'stock' manquant.")
                try:
                    stock_val = int(stock_val)
                except Exception:
                    raise ValueError(f"Stock invalide : {stock_val}")

                # Prix
                price_val = data.get('prix de vente') or data.get('prix') or data.get('price')
                if price_val is None:
                    raise ValueError("'prix de vente' manquant.")
                from decimal import Decimal
                try:
                    price_val = Decimal(str(price_val).replace(',', '.'))
                except Exception:
                    raise ValueError(f"Prix invalide : {price_val}")

                # Champs optionnels
                ean = data.get('ean') or data.get('code ean')
                pcb_code = data.get('pcb') or data.get('pcb_code') or data.get('code pcb')
                image = data.get('image du produit') or data.get('image')
                category_name = data.get('categorie') or data.get('category')
                brand_name = data.get('marque') or data.get('brand')

                # Résolution des relations
                category = None
                brand = None
                if category_name:
                    category_slug = slugify(category_name)
                    category, _ = Category.objects.get_or_create(name=category_name, defaults={'slug': category_slug})
                if brand_name:
                    brand_slug = slugify(brand_name)
                    brand, _ = Brand.objects.get_or_create(name=brand_name, defaults={'slug': brand_slug})

                # Création ou mise à jour du produit
                product, created = Product.objects.get_or_create(
                    article_code=art_code,
                    defaults={
                        'sku': art_code,
                        'title': designation,
                        'price': price_val,
                        'stock': stock_val,
                        'category': category,
                        'brand': brand,
                        'ean': ean,
                        'pcb_code': pcb_code,
                    }
                )
                if not created:
                    product.title = designation
                    product.price = price_val
                    product.stock = stock_val
                    product.ean = ean
                    product.pcb_code = pcb_code
                    product.category = category
                    product.brand = brand
                    product.save()
                # Mise à jour de l'image
                if image:
                    # Nettoyage du chemin : retirer un éventuel préfixe "media/"
                    img_path = str(image)
                    if img_path.startswith('media/'):
                        img_path = img_path[len('media/') :]
                    product.image = img_path
                    product.save(update_fields=['image'])
                success += 1
            except Exception as exc:
                failure += 1
                errors.append(f"Ligne {idx}: {exc}")

        # Mise à jour finale de la tâche
        import_task.status = 'completed' if not errors else 'failed'
        import_task.success_count = success
        import_task.failure_count = failure
        import_task.completed_at = timezone.now()
        if errors:
            import_task.errors = '\n'.join(errors)
        import_task.save()
    except Exception as exc:
        # Erreur non gérée
        import_task.status = 'failed'
        import_task.completed_at = timezone.now()
        import_task.errors = str(exc)
        import_task.save()
        # Lever à nouveau l'exception pour que Celery la capture et la consigne
        raise