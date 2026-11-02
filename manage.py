#!/usr/bin/env python
"""
Punto de entrada CLI de Django (`python manage.py …`).

Define DJANGO_SETTINGS_MODULE y delega en execute_from_command_line
(comandos: migrate, runserver, createsuperuser, check, shell, …).
"""
import os
import sys


def main():
    """Run administrative tasks. / Arranca el sistema de management commands."""
    # Indica qué módulo de settings cargar (config/settings.py).
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
