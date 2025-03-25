from django.db import migrations
from decimal import Decimal, InvalidOperation

def update_prices(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    for product in Product.objects.all():
        try:
            current_price = Decimal(str(product.price))
            product.price = current_price
            product.save()
        except (InvalidOperation, TypeError):
            # Если цена некорректная, установим значение по умолчанию
            product.price = Decimal('0.00')
            product.save()

def reverse_update_prices(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    for product in Product.objects.all():
        try:
            current_price = Decimal(str(product.price))
            product.price = current_price
            product.save()
        except (InvalidOperation, TypeError):
            product.price = Decimal('0.00')
            product.save()

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_prices, reverse_update_prices),
    ] 