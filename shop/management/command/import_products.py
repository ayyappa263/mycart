import csv
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Product, master_Category

class Command(BaseCommand):
    help = "Import fashion dataset"

    def handle(self, *args, **kwargs):

        csv_path = r"C:\Langchain\Chatbot\fashion_cleaned_dataset.csv"

        products = []
        categories = {}

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:

                cat_name = row["master_Category"]

                if cat_name not in categories:
                    category, _ = master_Category.objects.get_or_create(
                        name=cat_name,
                        defaults={
                            "slug": slugify(cat_name)
                        }
                    )
                    categories[cat_name] = category

                category = categories[cat_name]

                product = Product(
                    id=row["id"],
                    product_name=row["product_name"],
                    master_Category=category,
                    sub_Category=row["sub_Category"],
                    article_Type=row["article_Type"],
                    colour=row["Colour"],
                    gender=row["gender"],
                    season=row["season"],
                    usage=row["usage"],
                    price=int(row["price"]),
                    slug=slugify(f"{row['product_name']}-{row['id']}"),

                    # Image already copied to media/shop/images/
                    image=f"shop/images/{row['id']}.jpg"
                )

                products.append(product)

                if len(products) >= 1000:
                    Product.objects.bulk_create(
                        products,
                        ignore_conflicts=True
                    )
                    products = []

            if products:
                Product.objects.bulk_create(
                    products,
                    ignore_conflicts=True
                )