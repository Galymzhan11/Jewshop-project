from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Category, Product, Cart, Order, Address, Review, STATUS_CHOICES, PAYMENT_STATUS_CHOICES
from django.db.models import Count, Q, Min, Max, Avg
from .forms import RegistrationForm, AddressForm, LoginForm, ReviewForm, ProductForm, CategoryForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import uuid
import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import random
import string
from django.views.decorators.csrf import csrf_exempt
from .fondy_payment import create_payment, verify_callback

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:4]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)

def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    
    # Получаем все отзывы к товару
    reviews = Review.objects.filter(product=product, is_published=True).select_related('user')
    
    # Рассчитываем среднюю оценку товара
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)
    
    # Считаем количество отзывов с каждой оценкой (от 1 до 5 звезд)
    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = reviews.filter(rating=i).count()
    
    # Проверяем, может ли пользователь оставить отзыв на этот товар
    can_review = False
    if request.user.is_authenticated:
        # Пользователь может оставить отзыв, если он купил товар и заказ доставлен
        delivered_orders = Order.objects.filter(user=request.user, product=product, status='Delivered')
        
        # Для каждого заказа проверяем, оставил ли пользователь отзыв
        can_review_orders = []
        for order in delivered_orders:
            review_exists = Review.objects.filter(user=request.user, product=product, order=order).exists()
            if not review_exists:
                can_review_orders.append(order)
        
        can_review = bool(can_review_orders)
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'rating_counts': rating_counts,
        'can_review': can_review,
    }
    return render(request, 'store/detail.html', context)

def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories': categories})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'store/category_products.html', context)

def cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart_products = Cart.objects.filter(user=user)
        
        # Рассчитываем общую сумму
        amount = 0
        for p in cart_products:
            amount += p.quantity * p.product.price
        
        context = {
            'cart_products': cart_products,
            'amount': amount,
        }
    else:
        # Для неавторизованных пользователей показываем пустую корзину
        context = {
            'cart_products': [],
            'amount': 0,
        }
    
    return render(request, 'store/cart.html', context)

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        # Если пользователь не авторизован, перенаправляем на страницу входа
        if not request.user.is_authenticated:
            messages.warning(request, "Пожалуйста, войдите в систему, чтобы добавить товар в корзину")
            return redirect('store:login')
        
        product = get_object_or_404(Product, id=product_id)
        user = request.user
        
        # Проверяем, есть ли уже такой товар в корзине
        item_already_in_cart = Cart.objects.filter(user=user, product=product).exists()
        if item_already_in_cart:
            cart_item = Cart.objects.get(user=user, product=product)
            cart_item.quantity += 1
            cart_item.save()
        else:
            Cart.objects.create(user=user, product=product)
        
        return redirect('store:cart')
    
    return redirect('store:home')

def remove_cart(request, cart_id):
    # Если пользователь не авторизован, перенаправляем на страницу входа
    if not request.user.is_authenticated:
        messages.warning(request, "Пожалуйста, войдите в систему, чтобы управлять корзиной")
        return redirect('store:login')
        
    cart_item = get_object_or_404(Cart, id=cart_id)
    cart_item.delete()
    return redirect('store:cart')

def plus_cart(request, cart_id):
    # Если пользователь не авторизован, перенаправляем на страницу входа
    if not request.user.is_authenticated:
        messages.warning(request, "Пожалуйста, войдите в систему, чтобы управлять корзиной")
        return redirect('store:login')
        
    cart_item = get_object_or_404(Cart, id=cart_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('store:cart')

def minus_cart(request, cart_id):
    # Если пользователь не авторизован, перенаправляем на страницу входа
    if not request.user.is_authenticated:
        messages.warning(request, "Пожалуйста, войдите в систему, чтобы управлять корзиной")
        return redirect('store:login')
        
    cart_item = get_object_or_404(Cart, id=cart_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('store:cart')

# Функция для генерации номера заказа
def generate_order_number():
    return str(uuid.uuid4()).split('-')[0].upper()

@login_required
def checkout(request):
    user = request.user
    addresses = Address.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    
    # Проверяем, есть ли товары в корзине
    if not cart_items:
        messages.warning(request, "В вашей корзине нет товаров")
        return redirect('store:cart')
    
    # Рассчитываем общую сумму
    amount = 0
    for item in cart_items:
        amount += item.quantity * item.product.price
    
    context = {
        'addresses': addresses,
        'cart_items': cart_items,
        'amount': amount,
    }
    return render(request, 'store/checkout.html', context)

@login_required
@require_POST
def place_order(request):
    """Обработка размещения заказа"""
    data = json.loads(request.body)
    
    # Получаем данные из запроса
    address_id = data.get('address_id')
    payment_method = data.get('payment_method')
    
    if not address_id:
        return JsonResponse({'status': 'error', 'message': 'Выберите адрес доставки'}, status=400)
    
    try:
        address = Address.objects.get(id=address_id, user=request.user)
    except Address.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Указанный адрес не найден'}, status=400)
    
    # Получаем товары из корзины
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        return JsonResponse({'status': 'error', 'message': 'Ваша корзина пуста'}, status=400)
    
    # Генерируем общий номер заказа для всех товаров
    order_number = generate_order_number()
    
    # Определяем статус оплаты в зависимости от метода
    payment_status = 'pending'
    if payment_method == 'cash':
        # При оплате наличными считаем заказ подтвержденным
        payment_status = 'pending'  # Ожидает оплаты при доставке
        
    # Создаем заказы для каждого товара
    orders = []
    for item in cart_items:
        order = Order(
            user=request.user,
            address=address,
            product=item.product,
            quantity=item.quantity,
            status='Pending',
            payment_method=payment_method,
            payment_status=payment_status,
            order_number=order_number
        )
        order.save()
        orders.append(order)
    
    # Очищаем корзину после создания заказа
    cart_items.delete()
    
    response_data = {
        'status': 'success',
        'message': 'Заказ успешно создан!'
    }
    
    # Если выбрана оплата картой, добавляем данные для перенаправления на страницу оплаты
    if payment_method == 'card':
        response_data['redirect'] = f'/payment/{order_number}/'
    else:
        # Для оплаты наличными перенаправляем на страницу с заказами
        response_data['redirect'] = '/orders/'
    
    return JsonResponse(response_data)

@login_required
def payment_page(request, order_number):
    """Страница оплаты для заказов"""
    try:
        # Получаем заказы с указанным номером
        orders = Order.objects.filter(order_number=order_number, user=request.user)
        
        if not orders:
            messages.error(request, "Заказ не найден")
            return redirect('store:orders')
        
        # Рассчитываем общую сумму заказа в тенге
        total_amount_kzt = 0
        for order in orders:
            total_amount_kzt += order.product.price * order.quantity
        
        # Конвертируем в USD для тестового режима Fondy (примерно 1 USD = 450 KZT)
        # В реальном приложении здесь должен быть API для получения актуального курса
        exchange_rate = 450
        total_amount_usd = round(total_amount_kzt / exchange_rate, 2)
        
        # Проверяем, включен ли режим тестирования локальной платежной страницы
        use_local_payment = request.GET.get('local') == '1'
        
        if not use_local_payment:
            # Формируем описание заказа
            products_list = ", ".join([f"{order.product.title} x {order.quantity}" for order in orders])
            description = f"Оплата заказа #{order_number}: {products_list}"
            
            # Абсолютные URL-адреса для обработки платежей Fondy
            base_url = request.build_absolute_uri('/').rstrip('/')
            redirect_url = f"{base_url}/fondy-success/"
            callback_url = f"{base_url}/fondy-callback/"
            
            # Логируем URL-адреса для отладки
            print(f"Payment URLs: redirect={redirect_url}, callback={callback_url}")
            
            # Создаем платеж в Fondy
            payment_result = create_payment(
                order_number=order_number,
                amount=total_amount_usd,  # Используем сумму в USD
                description=description,
                currency='USD',  # Используем USD для тестового режима
                redirect_url=redirect_url,
                callback_url=callback_url
            )
            
            if payment_result['status'] == 'success':
                # Перенаправляем на страницу оплаты Fondy
                return redirect(payment_result['checkout_url'])
            else:
                # Если произошла ошибка при создании платежа, показываем локальную страницу
                error_message = payment_result.get('message', 'Неизвестная ошибка')
                messages.warning(request, f"Не удалось подключиться к Fondy: {error_message}. Показываем локальную платежную страницу.")
                use_local_payment = True
        
        # Если используем локальную страницу оплаты
        if use_local_payment:
            context = {
                'order_number': order_number,
                'orders': orders,
                'total_amount': total_amount_kzt,
                'total_amount_usd': total_amount_usd,
                'is_local_payment': True
            }
            return render(request, 'store/payment.html', context)
            
    except Exception as e:
        # Добавляем обработку всех исключений
        messages.error(request, f"Произошла ошибка: {str(e)}")
        return redirect('store:orders')

@login_required
@require_POST
def process_payment(request, order_number):
    """Обработка платежа (используется для тестирования, в основном платежи обрабатываются через колбэк)"""
    orders = Order.objects.filter(order_number=order_number, user=request.user)
    
    if not orders:
        return JsonResponse({'status': 'error', 'message': 'Заказ не найден'}, status=404)
    
    # В случае тестирования можно вручную обновлять статус заказа
    for order in orders:
        order.payment_status = 'paid'
        order.save()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Оплата принята к обработке',
        'redirect': '/orders/'
    })

@login_required
def orders(request):
    """Отображение заказов пользователя"""
    # Для администраторов перенаправляем на страницу управления заказами
    if request.user.is_superuser:
        return redirect('store:admin-orders')
    
    orders = Order.objects.filter(user=request.user)
    
    # Проверяем наличие информации о платеже в сессии
    payment_success = request.session.pop('payment_success', False)
    payment_id = request.session.pop('payment_id', None)
    order_id = request.session.pop('order_id', None)
    
    # Если есть информация о платеже, добавляем сообщение
    if payment_success:
        messages.success(
            request, 
            f"Платеж успешно обработан! Номер заказа: {order_id}, ID платежа: {payment_id}"
        )
    
    return render(request, 'store/orders.html', {'orders': orders})

@csrf_exempt
def fondy_success(request):
    """Обработка успешного платежа от Fondy (страница перенаправления)"""
    # Этот метод вызывается, когда Fondy перенаправляет пользователя обратно после оплаты
    try:
        # Получаем данные от Fondy (могут быть в POST или GET)
        if request.method == 'POST':
            payment_id = request.POST.get('payment_id')
            order_id = request.POST.get('order_id')
        else:
            payment_id = request.GET.get('payment_id')
            order_id = request.GET.get('order_id')
            
        # Логирование полученных данных
        print(f"Fondy redirect received: method={request.method}, order_id={order_id}, payment_id={payment_id}")
        
        # Перенаправляем на страницу успешной оплаты с параметрами
        return redirect(f'/payment-success/?order_id={order_id}&payment_id={payment_id}')
    except Exception as e:
        # В случае ошибки логируем её и всё равно перенаправляем на страницу успеха
        print(f"Error in fondy_success: {str(e)}")
        return redirect('/payment-success/')

def payment_success(request):
    """Страница с сообщением об успешной оплате, доступная всем пользователям"""
    # Получаем параметры из URL, если они есть
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    
    # Логируем получение запроса
    print(f"Payment success page: order_id={order_id}, payment_id={payment_id}")
    
    # Если есть ID заказа, попробуем получить информацию о нем
    order_info = None
    if order_id:
        try:
            orders = Order.objects.filter(order_number=order_id)
            if orders.exists():
                # Берем первый заказ для показа базовой информации
                first_order = orders.first()
                order_info = {
                    'order_number': order_id,
                    'date': first_order.ordered_date,
                    'product_count': orders.count(),
                    'total_amount': sum(order.product.price * order.quantity for order in orders)
                }
                
                # Убедимся, что заказ отмечен как оплаченный
                for order in orders:
                    if order.payment_status != 'paid':
                        order.payment_status = 'paid'
                        order.save()
        except Exception as e:
            # В случае ошибки просто не показываем информацию о заказе
            print(f"Error getting order info: {str(e)}")
    
    context = {
        'order_id': order_id,
        'payment_id': payment_id,
        'order_info': order_info,
        'is_authenticated': request.user.is_authenticated
    }
    
    return render(request, 'store/payment_success.html', context)

def contacts(request):
    return render(request, 'store/contacts.html')

def about(request):
    return render(request, 'store/about.html')

def shipping(request):
    return render(request, 'store/shipping.html')

def privacy(request):
    return render(request, 'store/privacy.html')

def subscription(request):
    """Обработка подписки на рассылку новостей и контактной формы"""
    if request.method == 'POST':
        # Получаем email для подписки
        email = request.POST.get('email')
        
        # Проверяем, отправлена ли контактная форма
        if request.POST.get('contact_form') == 'true':
            name = request.POST.get('name')
            subject = request.POST.get('subject', 'Сообщение с сайта')
            message = request.POST.get('message')
            
            # Здесь можно добавить код для отправки email 
            # или сохранения сообщения в базе данных
            
            messages.success(request, 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.')
        else:
            # Здесь можно добавить логику сохранения email в базу данных
            # или интеграцию с сервисом email-рассылок
            
            messages.success(request, 'Вы успешно подписались на рассылку новостей!')
    
    # Перенаправляем пользователя обратно на страницу, с которой он отправил форму
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))

def test(request):
    return render(request, 'store/test.html')

def search(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', '')
    
    # Базовые запросы
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Получаем минимальную и максимальную цену для фильтров
    price_range = products.aggregate(Min('price'), Max('price'))
    min_price_available = price_range['price__min'] if price_range['price__min'] else 0
    max_price_available = price_range['price__max'] if price_range['price__max'] else 100000
    
    if query:
        # Поиск по названию и описанию товаров
        products = products.filter(
            Q(title__icontains=query) | 
            Q(short_description__icontains=query) | 
            Q(detail_description__icontains=query)
        )
        
        # Поиск по названию и описанию категорий 
        categories = categories.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Фильтрация по категории
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Фильтрация по цене
    if min_price:
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass
    
    # Сортировка
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('title')
    elif sort_by == 'name_desc':
        products = products.order_by('-title')
    
    # Пагинация
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 12)  # 12 товаров на страницу
    
    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'query': query,
        'products': products_paginated,
        'categories': categories,
        'selected_category': category_id,
        'min_price': min_price if min_price else min_price_available,
        'max_price': max_price if max_price else max_price_available,
        'min_price_available': min_price_available,
        'max_price_available': max_price_available,
        'sort_by': sort_by,
        'page_obj': products_paginated,  # Для пагинации
        'is_paginated': products_paginated.has_other_pages(),
    }
    
    return render(request, 'store/search.html', context)

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    
    # Для администраторов добавляем дополнительную статистику
    if request.user.is_superuser:
        all_orders = Order.objects.all()
        pending_orders = Order.objects.filter(status='Pending').count()
        recent_reviews = Review.objects.filter(created_at__gte=timezone.now()-timezone.timedelta(days=7)).count()
        
        context = {
            'orders': all_orders.order_by('-ordered_date'),
            'pending_orders': pending_orders,
            'recent_reviews': recent_reviews,
        }
    else:
        context = {
            'addresses': addresses,
            'orders': orders,
        }
    
    return render(request, 'store/profile.html', context)

@login_required
def my_reviews(request):
    """Отображение всех отзывов пользователя"""
    # Запрещаем доступ администраторам
    if request.user.is_superuser:
        return redirect('store:profile')
        
    reviews = Review.objects.filter(user=request.user).select_related('product', 'order')
    return render(request, 'store/my_reviews.html', {'reviews': reviews})

@login_required
def my_purchased_products(request):
    """Отображение товаров, которые пользователь купил и может оставить отзыв"""
    # Запрещаем доступ администраторам
    if request.user.is_superuser:
        return redirect('store:profile')
        
    # Получаем все заказы пользователя
    orders = Order.objects.filter(user=request.user, status="Delivered").select_related('product')
    
    # Создаем список уникальных товаров и заказов
    purchased_products = []
    for order in orders:
        # Проверяем, оставил ли пользователь отзыв на этот товар из этого заказа
        review_exists = Review.objects.filter(
            user=request.user, 
            product=order.product,
            order=order
        ).exists()
        
        purchased_products.append({
            'order': order,
            'product': order.product,
            'has_review': review_exists,
        })
    
    return render(request, 'store/my_purchased_products.html', {'purchased_products': purchased_products})

@login_required
def add_review(request, order_id):
    # Запрещаем доступ администраторам
    if request.user.is_superuser:
        return redirect('store:profile')
        
    order = get_object_or_404(Order, id=order_id, user=request.user)
    product = order.product
    
    # Проверяем, что заказ доставлен
    if order.status != 'Delivered':
        messages.error(request, 'Вы можете оставить отзыв только на доставленный товар.')
        return redirect('store:my-purchased-products')
    
    # Проверяем, нет ли уже отзыва на этот товар из этого заказа
    if Review.objects.filter(user=request.user, product=product, order=order).exists():
        messages.error(request, 'Вы уже оставили отзыв на этот товар из этого заказа.')
        return redirect('store:my-purchased-products')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.order = order
            review.save()
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('store:product-detail', slug=product.slug)  # Используем correct name
    else:
        form = ReviewForm()
    
    return render(request, 'store/add_review.html', {
        'form': form,
        'product': product,
        'order': order
    })

@login_required
def edit_review(request, review_id):
    """Редактирование отзыва"""
    # Запрещаем доступ администраторам
    if request.user.is_superuser:
        return redirect('store:profile')
        
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш отзыв успешно обновлен")
            return redirect('store:my-reviews')
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'product': review.product,
    }
    
    return render(request, 'store/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    """Удаление отзыва"""
    # Запрещаем неавторизованный доступ к отзывам других пользователей
    if request.user.is_superuser:
        review = get_object_or_404(Review, id=review_id)
    else:
        review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Отзыв успешно удален")
        
        if request.user.is_superuser:
            return redirect('store:admin-reviews')
        else:
            return redirect('store:my-reviews')
    
    return render(request, 'store/delete_review.html', {'review': review})

@login_required
def remove_address(request, id):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return redirect('store:profile')

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect('store:login')
        return render(request, 'account/register.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'store/add_address.html', {'form': form})
    
    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            
            Address.objects.create(user=user, locality=locality, city=city, state=state)
            messages.success(request, "Новый адрес успешно добавлен!")
            return redirect('store:profile')
        return render(request, 'store/add_address.html', {'form': form})

@login_required
def logout_view(request):
    """
    Выход пользователя из системы и перенаправление на главную страницу
    """
    logout(request)
    messages.success(request, "Вы успешно вышли из системы")
    return redirect('store:home')

class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    authentication_form = LoginForm
    
    def get(self, request, *args, **kwargs):
        # Очищаем все предыдущие сообщения при заходе на страницу логина
        storage = messages.get_messages(request)
        for message in storage:
            pass  # Просто итерируем сообщения, что помечает их как прочитанные
        storage.used = True  # Очищаем хранилище сообщений
        
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Добавляем сообщение об успешном входе
        messages.success(self.request, "Вы успешно вошли в систему!")
        return response
        
    def get_success_url(self):
        return reverse_lazy('store:profile')

@login_required
def admin_orders(request):
    """Управление заказами (только для администраторов)"""
    if not request.user.is_superuser:
        return redirect('store:profile')
    
    # Получаем параметры фильтрации из запроса
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    date_from = request.GET.get('date_from', '')
    
    # Базовый запрос
    orders = Order.objects.all().select_related('user', 'product', 'address')
    
    # Применяем фильтры, если они указаны
    if status:
        orders = orders.filter(status=status)
    
    if payment_status:
        orders = orders.filter(payment_status=payment_status)
    
    if date_from:
        try:
            date_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(ordered_date__date__gte=date_obj)
        except ValueError:
            pass  # Невалидная дата, игнорируем фильтр
    
    # Сортируем заказы по дате (сначала новые)
    orders = orders.order_by('-ordered_date')
    
    context = {
        'orders': orders,
        'status': status,
        'payment_status': payment_status,
        'date_from': date_from,
    }
    
    return render(request, 'store/admin_orders.html', context)

@login_required
def admin_reviews(request):
    """Управление отзывами (только для администраторов)"""
    if not request.user.is_superuser:
        return redirect('store:profile')
    
    # Получаем параметры фильтрации из запроса
    rating = request.GET.get('rating', '')
    is_published = request.GET.get('is_published', '')
    
    # Базовый запрос
    reviews = Review.objects.all().select_related('user', 'product', 'order')
    
    # Применяем фильтры, если они указаны
    if rating:
        try:
            reviews = reviews.filter(rating=int(rating))
        except ValueError:
            pass
    
    if is_published == 'True':
        reviews = reviews.filter(is_published=True)
    elif is_published == 'False':
        reviews = reviews.filter(is_published=False)
    
    # Сортируем отзывы по дате (сначала новые)
    reviews = reviews.order_by('-created_at')
    
    context = {
        'reviews': reviews,
        'rating': rating,
        'is_published': is_published,
    }
    
    return render(request, 'store/admin_reviews.html', context)

@login_required
@require_POST
def update_order_status(request, order_id):
    """Обновление статуса заказа администратором"""
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Доступ запрещен'}, status=403)
    
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    # Проверяем валидность статуса
    valid_statuses = [choice[0] for choice in STATUS_CHOICES]
    if new_status not in valid_statuses:
        messages.error(request, 'Некорректный статус заказа')
        return redirect('store:admin-orders')
    
    # Обновляем статус заказа
    order.status = new_status
    order.save()
    
    messages.success(request, f'Статус заказа #{order.order_number} изменен на "{dict(STATUS_CHOICES)[new_status]}"')
    return redirect('store:admin-orders')

@login_required
@require_POST
def update_payment_status(request, order_id):
    """Обновление статуса оплаты заказа администратором"""
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Доступ запрещен'}, status=403)
    
    order = get_object_or_404(Order, id=order_id)
    new_payment_status = request.POST.get('payment_status')
    
    # Проверяем валидность статуса оплаты
    valid_payment_statuses = [choice[0] for choice in PAYMENT_STATUS_CHOICES]
    if new_payment_status not in valid_payment_statuses:
        messages.error(request, 'Некорректный статус оплаты')
        return redirect('store:admin-orders')
    
    # Обновляем статус оплаты заказа
    order.payment_status = new_payment_status
    order.save()
    
    messages.success(request, f'Статус оплаты заказа #{order.order_number} изменен на "{dict(PAYMENT_STATUS_CHOICES)[new_payment_status]}"')
    return redirect('store:admin-orders')

@login_required
@require_POST
def toggle_review_status(request, review_id):
    """Переключение статуса публикации отзыва администратором"""
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Доступ запрещен'}, status=403)
    
    review = get_object_or_404(Review, id=review_id)
    
    # Переключаем статус публикации
    review.is_published = not review.is_published
    review.save()
    
    if review.is_published:
        messages.success(request, 'Отзыв опубликован')
    else:
        messages.success(request, 'Отзыв скрыт')
    
    return redirect('store:admin-reviews')

@login_required
def admin_products(request):
    """Отображает страницу управления товарами для администратора"""
    # Проверяем, что пользователь является администратором
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав доступа к этой странице!")
        return redirect('store:profile')
    
    # Получаем все категории для фильтра
    categories = Category.objects.all()
    
    # Фильтрация товаров
    products_list = Product.objects.all()
    
    # Фильтр по категории
    category_id = request.GET.get('category')
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    
    # Фильтр по статусу
    status = request.GET.get('status')
    if status:
        if status == 'active':
            products_list = products_list.filter(is_active=True)
        elif status == 'inactive':
            products_list = products_list.filter(is_active=False)
        elif status == 'featured':
            products_list = products_list.filter(is_featured=True)
    
    # Поиск по названию или SKU
    search = request.GET.get('search')
    if search:
        products_list = products_list.filter(
            Q(title__icontains=search) | Q(sku__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(products_list, 10)  # 10 товаров на страницу
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'categories': categories,
        'paginator': paginator,
    }
    
    return render(request, 'store/admin_products.html', context)

@login_required
def admin_categories(request):
    """Отображает страницу управления категориями для администратора"""
    # Проверяем, что пользователь является администратором
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав доступа к этой странице!")
        return redirect('store:profile')
    
    # Фильтрация категорий
    categories_list = Category.objects.all()
    
    # Поиск по названию
    search = request.GET.get('search')
    if search:
        categories_list = categories_list.filter(title__icontains=search)
    
    # Пагинация
    paginator = Paginator(categories_list, 10)  # 10 категорий на страницу
    page = request.GET.get('page')
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories,
        'paginator': paginator,
    }
    
    return render(request, 'store/admin_categories.html', context)

@login_required
def add_product(request):
    """Форма добавления нового товара"""
    # Проверяем, что пользователь является администратором
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав доступа к этой странице!")
        return redirect('store:profile')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем, но не выполняем запись в базу данных
            product = form.save(commit=False)
            
            # Генерируем SKU на основе категории и времени
            # Формат: JW-CAT{ID категории}-{timestamp}
            category_id = form.cleaned_data['category'].id
            timestamp = timezone.now().strftime('%Y%m%d%H%M')
            
            # Генерируем случайный суффикс (2 символа)
            suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
            
            # Собираем SKU
            product.sku = f"JW-CAT{category_id}-{timestamp}{suffix}"
            
            # Сохраняем товар с новым SKU
            product.save()
            
            messages.success(request, f'Товар успешно добавлен! Сгенерированный SKU: {product.sku}')
            return redirect('store:admin-products')
    else:
        form = ProductForm()
    
    context = {'form': form}
    return render(request, 'store/add_product.html', context)

@login_required
def edit_product(request, product_id):
    """Форма редактирования существующего товара"""
    # Проверяем, что пользователь является администратором
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав доступа к этой странице!")
        return redirect('store:profile')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен!')
            return redirect('store:admin-products')
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'product': product}
    return render(request, 'store/edit_product.html', context)

@login_required
def delete_product(request, product_id):
    """Удаление товара"""
    # Проверяем, что пользователь является администратором
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав доступа к этой странице!")
        return redirect('store:profile')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удален!')
        return redirect('store:admin-products')
    
    context = {'product': product}
    return render(request, 'store/delete_product.html', context)

@login_required
def add_category(request):
    """Форма добавления новой категории"""
    # Проверяем, что пользователь является администратором
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав доступа к этой странице!")
        return redirect('store:profile')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно добавлена!')
            return redirect('store:admin-categories')
    else:
        form = CategoryForm()
    
    context = {'form': form}
    return render(request, 'store/add_category.html', context)

@login_required
def edit_category(request, category_id):
    """Форма редактирования существующей категории"""
    # Проверяем, что пользователь является администратором
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав доступа к этой странице!")
        return redirect('store:profile')
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно обновлена!')
            return redirect('store:admin-categories')
    else:
        form = CategoryForm(instance=category)
    
    context = {'form': form, 'category': category}
    return render(request, 'store/edit_category.html', context)

@login_required
def delete_category(request, category_id):
    """Удаление категории"""
    # Проверяем, что пользователь является администратором
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав доступа к этой странице!")
        return redirect('store:profile')
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Категория успешно удалена!')
        return redirect('store:admin-categories')
    
    context = {'category': category}
    return render(request, 'store/delete_category.html', context)

@csrf_exempt
def fondy_callback(request):
    """Обработка колбэка от Fondy"""
    if request.method == 'POST':
        try:
            # Попытка декодировать JSON
            data = json.loads(request.body)
            
            # Логирование данных (в продакшене лучше использовать настоящее логирование)
            print("Received Fondy callback data:", data)
            
            # Данные могут быть в разных форматах, проверяем оба варианта
            order_data = data.get('order', {})
            if not order_data:
                order_data = data
            
            # Проверяем подпись
            if not verify_callback(order_data):
                return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
            
            # Получаем данные о платеже
            order_id = order_data.get('order_id')
            payment_status = order_data.get('order_status')
            
            if not order_id or not payment_status:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
            
            # Проверяем статус платежа
            if payment_status == 'approved':
                # Обновляем статус заказа в базе данных
                orders = Order.objects.filter(order_number=order_id)
                for order in orders:
                    order.payment_status = 'paid'
                    order.save()
                
                return JsonResponse({'status': 'success'})
            else:
                # Обновляем статус заказа в соответствии с полученным статусом
                orders = Order.objects.filter(order_number=order_id)
                for order in orders:
                    order.payment_status = 'failed'
                    order.save()
                
                return JsonResponse({'status': 'error', 'message': f'Payment failed with status: {payment_status}'})
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}, body: {request.body}")
            return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {str(e)}'}, status=400)
        except Exception as e:
            print(f"Exception in fondy_callback: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
