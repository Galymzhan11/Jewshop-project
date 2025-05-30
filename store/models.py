from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, db_index=True)
    locality = models.CharField(max_length=150, verbose_name="Ближайшее местоположение")
    city = models.CharField(max_length=150, verbose_name="Город")
    state = models.CharField(max_length=150, verbose_name="Область")

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return self.locality


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название категории")
    slug = models.SlugField(max_length=55, verbose_name="URL категории", unique=True)
    description = models.TextField(blank=True, verbose_name="Описание категории")
    category_image = models.ImageField(upload_to='category', blank=True, null=True, verbose_name="Изображение категории")
    is_active = models.BooleanField(verbose_name="Активна?", default=True)
    is_featured = models.BooleanField(verbose_name="Рекомендуемая?", default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name_plural = 'Категории'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name="Название товара")
    slug = models.SlugField(max_length=160, verbose_name="URL товара", unique=True)
    sku = models.CharField(max_length=255, unique=True, verbose_name="Уникальный ID товара (SKU)")
    short_description = models.TextField(verbose_name="Краткое описание")
    detail_description = models.TextField(blank=True, null=True, verbose_name="Подробное описание")
    product_image = models.ImageField(upload_to='product', blank=True, null=True, verbose_name="Изображение товара")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(Category, verbose_name="Категория товара", on_delete=models.CASCADE, db_index=True)
    is_active = models.BooleanField(verbose_name="Активен?", default=True)
    is_featured = models.BooleanField(verbose_name="Рекомендуемый?", default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name_plural = 'Товары'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE, db_index=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return str(self.user)
    
    # Creating Model Property to calculate Quantity x Price
    @property
    def total_price(self):
        return self.quantity * self.product.price


STATUS_CHOICES = (
    ('Pending', 'В ожидании'),
    ('Accepted', 'Принят'),
    ('On The Way', 'В пути'),
    ('Delivered', 'Доставлен'),
    ('Cancelled', 'Отменен')
)

# Добавляем варианты способов оплаты
PAYMENT_METHOD_CHOICES = (
    ('cash', 'Наличными при получении'),
    ('card', 'Оплата картой'),
)

# Добавляем варианты статусов оплаты
PAYMENT_STATUS_CHOICES = (
    ('pending', 'Ожидает оплаты'),
    ('paid', 'Оплачено'),
    ('failed', 'Ошибка оплаты'),
)

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, db_index=True)
    address = models.ForeignKey(Address, verbose_name="Адрес доставки", on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE, db_index=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=50,
        default="Pending",
        verbose_name="Статус"
    )
    payment_method = models.CharField(
        choices=PAYMENT_METHOD_CHOICES,
        max_length=20,
        default="cash",
        verbose_name="Способ оплаты"
    )
    payment_status = models.CharField(
        choices=PAYMENT_STATUS_CHOICES,
        max_length=20,
        default="pending",
        verbose_name="Статус оплаты"
    )
    # Можно добавить номер заказа для идентификации транзакции
    order_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер заказа", unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['address']),
            models.Index(fields=['product']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['order_number']),
        ]


# Варианты оценок для отзывов
RATING_CHOICES = (
    (1, '1 звезда'),
    (2, '2 звезды'),
    (3, '3 звезды'),
    (4, '4 звезды'),
    (5, '5 звезд'),
)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Товар", db_index=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Заказ", db_index=True)
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
        # Пользователь может оставить только один отзыв на товар из одного заказа
        unique_together = ['user', 'product', 'order']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['order']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.title}"
