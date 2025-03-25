from django.db import migrations
from decimal import Decimal

def fix_product_prices(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    # Обновляем все цены в базе данных
    Product.objects.all().update(price=Decimal('0.00'))

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0005_merge_0002_update_prices_0004_auto_20210529_1741'),
    ]

    operations = [
        migrations.RunPython(fix_product_prices),
    ] 