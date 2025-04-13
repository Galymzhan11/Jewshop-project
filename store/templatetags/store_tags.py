from django import template
from django.conf import settings
from store.models import Cart

register = template.Library()

@register.simple_tag
def get_media_prefix():
    """
    Returns the MEDIA_URL from settings.
    """
    return settings.MEDIA_URL

@register.simple_tag
def get_cart_count(user):
    """
    Получает количество товаров в корзине пользователя
    """
    if user.is_authenticated:
        return Cart.objects.filter(user=user).count()
    return 0

@register.filter
def mul(value, arg):
    """
    Multiplies the value by the argument
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """
    Divides the value by the argument
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def get_item(dictionary, key):
    """
    Получает элемент из словаря по ключу
    Пытается использовать как строковый, так и числовой ключ
    """
    # Пробуем получить значение по ключу как есть
    value = dictionary.get(key, None)
    if value is not None:
        return value
    
    # Пробуем преобразовать строковый ключ в числовой
    try:
        numeric_key = int(key)
        return dictionary.get(numeric_key, 0)
    except (ValueError, TypeError):
        pass
    
    # Если ключ числовой, пробуем его строковое представление
    try:
        str_key = str(key)
        return dictionary.get(str_key, 0)
    except:
        pass
    
    return 0

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''