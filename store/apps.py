from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # Регистрация пользовательских тегов шаблона
        from django.template.defaulttags import register
        try:
            from store.templatetags import store_tags
        except ImportError:
            pass
