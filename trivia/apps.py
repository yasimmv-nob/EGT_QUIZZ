"""
AppConfig de `trivia`: metadatos de la aplicación Django.

Django descubre cada app listada en INSTALLED_APPS; esta clase define
el nombre Python del paquete y el tipo de PK por defecto (BigAutoField).
"""

from django.apps import AppConfig


class TriviaConfig(AppConfig):
    # PK por defecto para modelos de esta app (BIGINT autoincremental).
    default_auto_field = "django.db.models.BigAutoField"
    name = "trivia"  # debe coincidir con el paquete / entrada en INSTALLED_APPS
