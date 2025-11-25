"""
Django App configuration for the API application.

This module configures the 'api' Django application, including
default settings for auto-generated primary keys.
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Configuration class for the API application.
    
    Sets the default auto field type for models and defines the
    application name for Django's app registry.
    
    Attributes:
        default_auto_field: Type of primary key to use (BigAutoField)
        name: Application name ('api')
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
