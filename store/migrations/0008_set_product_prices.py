from django.db import migrations
from decimal import Decimal
import random

def set_product_prices(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    # Список возможных цен
    prices = [
        Decimal('150000.00'),  # 150,000 тг
        Decimal('250000.00'),  # 250,000 тг
        Decimal('350000.00'),  # 350,000 тг
        Decimal('450000.00'),  # 450,000 тг
        Decimal('500000.00'),  # 500,000 тг
        Decimal('180000.00'),  # 180,000 тг
        Decimal('280000.00'),  # 280,000 тг
        Decimal('380000.00'),  # 380,000 тг
        Decimal('480000.00'),  # 480,000 тг
        Decimal('200000.00'),  # 200,000 тг
    ]
    
    # Обновляем цены для всех товаров
    for product in Product.objects.all():
        product.price = random.choice(prices)
        product.save()

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0007_fix_product_prices'),
    ]

    operations = [
        migrations.RunPython(set_product_prices),
    ] 