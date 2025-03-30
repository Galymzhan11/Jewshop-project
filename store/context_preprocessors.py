from store.models import Category, Cart


def store_menu(request):
    categories = Category.objects.filter(is_active=True)[:5]  # Ограничиваем до 5 категорий для меню
    return {'menu_categories': categories}

def cart_menu(request):
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        return {'cart_count': cart_count}
    return {'cart_count': 0}