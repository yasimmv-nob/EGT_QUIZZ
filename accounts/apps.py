"""
AppConfig de `accounts`: perfiles de estudiante y (futuro) lógica de auth.

Misma idea que trivia.apps: registra la app ante el framework Django.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
