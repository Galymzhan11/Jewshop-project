import hashlib
import requests
import json
from django.conf import settings
from django.urls import reverse

# Тестовые данные Fondy
FONDY_MERCHANT_ID = '1396424'
FONDY_SECRET_KEY = 'test'  # Пароль для транзакций purchase и verification

# URL API Fondy
FONDY_API_URL = 'https://api.fondy.eu/api/checkout/url/'

def generate_signature(params, secret_key):
    """Генерирует подпись для запроса к Fondy"""
    # Сортируем параметры по ключу
    sorted_params = sorted(params.items())
    
    # Создаем строку для подписи
    signature_string = '|'.join([str(value) for key, value in sorted_params if key != 'signature'])
    signature_string = secret_key + '|' + signature_string
    
    # Возвращаем HMAC-SHA1 подпись
    return hashlib.sha1(signature_string.encode('utf-8')).hexdigest()

def create_payment(order_number, amount, description, currency='USD', callback_url=None, redirect_url=None):
    """Создает платеж в системе Fondy и возвращает URL для оплаты"""
    try:
        # Подготавливаем параметры для запроса
        params = {
            'order_id': order_number,
            'merchant_id': FONDY_MERCHANT_ID,
            'order_desc': description,
            'amount': str(int(amount * 100)),  # Сумма в копейках/центах
            'currency': currency,  # Используем USD для тестового режима
            'lang': 'ru',  # Добавляем язык интерфейса
            'required_rectoken': 'N',  # Не сохраняем токен карты
            'verification': 'Y',  # Включаем верификацию платежа
            'payment_systems': 'card',  # Только банковские карты
        }
        
        # Добавляем URL для переадресации, если они предоставлены
        if redirect_url:
            params['response_url'] = redirect_url
        else:
            # Используем URL для перенаправления на страницу успешной оплаты
            params['response_url'] = 'https://your-domain.com/fondy-success/'
            
        if callback_url:
            params['server_callback_url'] = callback_url
        else:
            # Используем URL для обработки колбэка от Fondy
            params['server_callback_url'] = 'https://your-domain.com/fondy-callback/'
        
        # Добавляем подпись
        params['signature'] = generate_signature(params, FONDY_SECRET_KEY)
        
        print("Sending params to Fondy:", params)  # Логирование для отладки
        
        # Формируем данные для запроса
        request_data = {
            'request': params
        }
        
        # Отправляем запрос к API Fondy
        response = requests.post(FONDY_API_URL, json=request_data)
        
        print("Fondy API response:", response.text)  # Логирование для отладки
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('response', {}).get('response_status') == 'success':
                return {
                    'status': 'success',
                    'checkout_url': response_data['response']['checkout_url'],
                    'payment_id': response_data['response'].get('payment_id'),
                }
            else:
                error_message = response_data.get('response', {}).get('error_message', 'Unknown error')
                error_code = response_data.get('response', {}).get('error_code', '')
                return {
                    'status': 'error',
                    'message': f'Ошибка Fondy {error_code}: {error_message}'
                }
        else:
            return {
                'status': 'error',
                'message': f'API request failed with status code {response.status_code}'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Exception during payment creation: {str(e)}'
        }

def verify_callback(data):
    """Проверяет подпись в колбэке от Fondy"""
    try:
        if 'signature' not in data:
            return False
        
        received_signature = data['signature']
        params = {k: v for k, v in data.items() if k != 'signature'}
        
        calculated_signature = generate_signature(params, FONDY_SECRET_KEY)
        
        return received_signature == calculated_signature
    except Exception:
        return False 