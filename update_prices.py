import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelryshop.settings')
django.setup()

from store.models import Product
from django.db.models import F

# Обновляем цены всех товаров
Product.objects.all().update(price=F('price') * 100)

print("Цены успешно обновлены!") 