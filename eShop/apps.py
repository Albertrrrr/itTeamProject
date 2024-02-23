from django.apps import AppConfig


class EshopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eShop"

    def ready(self):
        import eShop.signals

