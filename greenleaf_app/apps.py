from django.apps import AppConfig


class GreanleafAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'greenleaf_app'

    def ready(self):
        from greenleaf_app import signals  # Инициализация сигналов