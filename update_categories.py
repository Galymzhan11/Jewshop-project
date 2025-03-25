import os
import django

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewshop.settings')
django.setup()

from store.models import Category

def update_categories():
    # Словарь для замены названий категорий
    category_updates = {
        'Rings': 'Кольца',
    }
    
    # Обновляем каждую категорию
    for old_name, new_name in category_updates.items():
        updated = Category.objects.filter(title=old_name).update(title=new_name)
        if updated:
            print(f'Обновлена категория: {old_name} -> {new_name}')

if __name__ == '__main__':
    update_categories() 