"""
Commande de gestion permettant d'importer des produits en masse depuis un
fichier CSV ou JSON.

Cette commande lit un fichier passé via l'argument ``--file`` et crée
ou met à jour des instances de ``Product`` en fonction de l'identifiant
unique ``article_code``. Les champs importés sont les suivants :

* ``article_code`` : identifiant unique du produit (obligatoire).
* ``ean`` : code EAN (facultatif).
* ``pcb_code`` : code constructeur/PCB (facultatif).
* ``designation`` : nom complet du produit (obligatoire).
* ``stock`` : quantité en stock (obligatoire).
* ``price`` : prix de vente TTC (obligatoire).
* ``image`` : URL ou chemin vers l'image (facultatif).
* ``category`` et ``brand`` : noms de la catégorie et de la marque (optionnels).

Si une ligne comporte un ``article_code`` qui existe déjà en base, le
produit correspondant est mis à jour ; sinon un nouvel enregistrement
est créé. Les catégories et marques sont recherchées par leur nom et
créées si nécessaire. Un log d'intégration est systématiquement créé
afin de tracer l'opération.
"""

import csv
import json
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Product, Category, Brand
from integrations.models import IntegrationLog


class Command(BaseCommand):
    help = "Importe des produits depuis un fichier CSV, JSON ou Excel (.xls/.xlsx)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Chemin vers le fichier à importer (CSV, JSON ou Excel).",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            raise CommandError(f"Le fichier {file_path} n'existe pas.")

        ext = file_path.suffix.lower()
        records = []
        try:
            if ext in {".json", ".js", ".txt"}:
                # Lecture des données JSON
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # On accepte un objet JSON contenant une clé "products"
                        records = data.get("products", [])
                    elif isinstance(data, list):
                        records = data
                    else:
                        raise ValueError("Format JSON inattendu : liste ou objet requis.")
            elif ext in {".csv", ".tsv"}:
                # Lecture des données CSV/TSV
                with open(file_path, newline="", encoding="utf-8") as f:
                    delimiter = "," if ext == ".csv" else "\t"
                    reader = csv.DictReader(f, delimiter=delimiter)
                    records = list(reader)
            elif ext in {".xls", ".xlsx"}:
                # Lecture d'un fichier Excel via pandas
                try:
                    import pandas as pd
                except ImportError as exc:
                    raise CommandError(
                        "Impossible de lire un fichier Excel : pandas n'est pas installé." ) from exc
                try:
                    df = pd.read_excel(file_path, sheet_name=0)
                except Exception as exc:
                    raise CommandError(f"Erreur lors de la lecture du fichier Excel : {exc}")
                records = df.to_dict(orient="records")
            else:
                raise CommandError("Format de fichier non pris en charge. Utilisez CSV, JSON ou Excel.")
        except Exception as exc:
            raise CommandError(f"Erreur de lecture du fichier : {exc}")

        created_count = 0
        updated_count = 0
        errors = []

        # Démarre une transaction pour garantir la cohérence
        with transaction.atomic():
            for i, row in enumerate(records, start=1):
                try:
                    # Normalise les clés en minuscules sans espace
                    normalized = {k.strip().lower(): v for k, v in row.items()}

                    art_code = normalized.get("code article") or normalized.get("article_code") or normalized.get("code_article") or normalized.get("sku")
                    if not art_code:
                        raise ValueError("'code article' manquant.")

                    # Le nom complet du produit peut être fourni sous plusieurs clés :
                    # - "designation" (sans accent)
                    # - "désignation" (avec accent)
                    # - "nom" ou "title" comme alternatives
                    designation = (
                        normalized.get("designation")
                        or normalized.get("désignation")
                        or normalized.get("nom")
                        or normalized.get("title")
                    )
                    if not designation:
                        raise ValueError("'designation' manquant.")

                    stock = normalized.get("stock") or normalized.get("quantite") or normalized.get("quantité")
                    if stock is None:
                        raise ValueError("'stock' manquant.")
                    try:
                        stock = int(stock)
                    except (ValueError, TypeError):
                        raise ValueError(f"Stock invalide : {stock}")

                    price = normalized.get("prix de vente") or normalized.get("prix") or normalized.get("price")
                    if price is None:
                        raise ValueError("'prix de vente' manquant.")
                    try:
                        price = Decimal(str(price).replace(",", "."))
                    except Exception:
                        raise ValueError(f"Prix invalide : {price}")

                    ean = normalized.get("ean") or normalized.get("code ean")
                    pcb_code = normalized.get("pcb") or normalized.get("pcb_code") or normalized.get("code pcb")
                    image = normalized.get("image du produit") or normalized.get("image")
                    category_name = normalized.get("categorie") or normalized.get("category")
                    brand_name = normalized.get("marque") or normalized.get("brand")

                    # Recherche ou création des relations
                    category = None
                    brand = None
                    if category_name:
                        category, _ = Category.objects.get_or_create(name=category_name, defaults={"slug": category_name.lower().replace(" ", "-")})
                    else:
                        category = Category.objects.filter(is_active=True).first()

                    if brand_name:
                        brand, _ = Brand.objects.get_or_create(name=brand_name, defaults={"slug": brand_name.lower().replace(" ", "-")})
                    else:
                        brand = Brand.objects.filter(is_active=True).first()

                    # Création ou mise à jour du produit
                    product, created = Product.objects.get_or_create(article_code=art_code, defaults={
                        "sku": art_code,
                        "title": designation,
                        "price": price,
                        "stock": stock,
                        "category": category,
                        "brand": brand,
                        "ean": ean,
                        "pcb_code": pcb_code,
                    })
                    if created:
                        created_count += 1
                    else:
                        # MàJ des champs variables
                        product.title = designation
                        product.price = price
                        product.stock = stock
                        product.ean = ean
                        product.pcb_code = pcb_code
                        product.category = category
                        product.brand = brand
                        product.save()
                        updated_count += 1
                    # Mise à jour de l'image si fournie
                    #
                    # Lorsque l'import fournit un chemin de fichier, il peut inclure
                    # le préfixe "media/" (ex.: "media/products/test1.png").  Or, le
                    # champ ImageField stocke un chemin relatif à MEDIA_ROOT et
                    # utilise "upload_to" (ici "products/") pour construire l'URL.
                    # Si l'on stocke un chemin commençant par "media/", l'URL
                    # résultante devient "/media/media/…", ce qui rend l'image
                    # introuvable.  On supprime donc le préfixe "media/" avant de
                    # assigner le chemin et on laisse Django gérer le stockage.
                    if image:
                        # Nettoyer le chemin d'image : retirer éventuel « media/ » en début
                        # et normaliser les séparateurs.
                        img_path = str(image)
                        # Les fichiers importés doivent se trouver sous MEDIA_ROOT.
                        # Par convention, si le chemin commence par "media/", on l'enlève.
                        if img_path.startswith("media/"):
                            img_path = img_path[len("media/") :]
                        # Affecte le chemin nettoyé. Cela n'effectue pas de copie de fichier :
                        # les fichiers doivent être présents dans MEDIA_ROOT au préalable.
                        product.image = img_path
                        product.save(update_fields=["image"])
                except Exception as exc:
                    errors.append(f"Ligne {i}: {exc}")

        # Enregistrement du log
        status = "success" if not errors else "partial"
        details_lines = [f"{created_count} créés, {updated_count} mis à jour."]
        if errors:
            details_lines.append("Erreurs :")
            details_lines.extend(errors)
        IntegrationLog.objects.create(
            name="import_products",
            status=status,
            details="\n".join(details_lines),
        )

        # Affichage du résultat à l'utilisateur
        if errors:
            self.stdout.write(self.style.WARNING(f"Import terminé avec des erreurs : {len(errors)} lignes en erreur."))
        else:
            self.stdout.write(self.style.SUCCESS("Import terminé avec succès."))
        self.stdout.write(f"{created_count} produits créés, {updated_count} mis à jour.")