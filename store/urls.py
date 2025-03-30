from store.forms import LoginForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import RegistrationView, AddressView, CustomLoginView


app_name = 'store'


urlpatterns = [
    path('', views.home, name="home"),
    # URL for Cart and Checkout
    path('add-to-cart/', views.add_to_cart, name="add-to-cart"),
    path('remove-cart/<int:cart_id>/', views.remove_cart, name="remove-cart"),
    path('plus-cart/<int:cart_id>/', views.plus_cart, name="plus-cart"),
    path('minus-cart/<int:cart_id>/', views.minus_cart, name="minus-cart"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('place-order/', views.place_order, name="place-order"),
    path('payment/<str:order_number>/', views.payment_page, name="payment"),
    path('process-payment/<str:order_number>/', views.process_payment, name="process-payment"),
    path('orders/', views.orders, name="orders"),

    # URL для поиска
    path('search/', views.search, name='search'),

    # Статические страницы
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    path('shipping/', views.shipping, name='shipping'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Подписка на рассылку
    path('subscription/', views.subscription, name='subscription'),
    
    # Используем нашу функцию для выхода из системы
    path('logout/', views.logout_view, name='logout'),

    #URL for Products
    path('product/<slug:slug>/', views.detail, name="product-detail"),
    path('categories/', views.all_categories, name="all-categories"),
    
    # URL for Authentication
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', views.profile, name="profile"),
    path('add-address/', AddressView.as_view(), name="add-address"),
    path('remove-address/<int:id>/', views.remove_address, name="remove-address"),
    
    # URL для отзывов
    path('my-reviews/', views.my_reviews, name='my-reviews'),
    path('my-purchased-products/', views.my_purchased_products, name='my-purchased-products'),
    path('add-review/<int:order_id>/', views.add_review, name='add-review'),
    path('edit-review/<int:review_id>/', views.edit_review, name='edit-review'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete-review'),
    
    # Административные URL
    path('admin-orders/', views.admin_orders, name='admin-orders'),
    path('admin-reviews/', views.admin_reviews, name='admin-reviews'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update-order-status'),
    path('update-payment-status/<int:order_id>/', views.update_payment_status, name='update-payment-status'),
    path('toggle-review-status/<int:review_id>/', views.toggle_review_status, name='toggle-review-status'),
    
    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(template_name='account/password_change.html', form_class=PasswordChangeForm, success_url='/accounts/password-change-done/'), name="password-change"),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'), name="password-change-done"),

    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html', form_class=PasswordResetForm, success_url='/accounts/password-reset/done/'), name="password-reset"), # Passing Success URL to Override default URL, also created password_reset_email.html due to error from our app_name in URL
    path('accounts/password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name="password_reset_done"),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html', form_class=SetPasswordForm, success_url='/accounts/password-reset-complete/'), name="password_reset_confirm"), # Passing Success URL to Override default URL
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name="password_reset_complete"),

    path('product/test/', views.test, name="test"),

    # Этот URL должен быть в самом конце, так как он использует переменную slug
    path('<slug:slug>/', views.category_products, name="category-products"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
