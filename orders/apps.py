from django.apps import AppConfig


class OrdersConfig(AppConfig):
    # The default_auto_field attribute specifies the type of the primary key that Django should use for models
    # that do not specify a primary key type explicitly. In this case, we're using a BigAutoField as the default
    # type for the primary key field.
    default_auto_field: str = 'django.db.models.BigAutoField'
    # The name attribute specifies the name of the app that this configuration belongs to.
    name: str = 'orders'

    """
    we would normally wire the container here, but we are doing it from the main project file, after all apps have
    been loaded; this is because of a bug in the dependency injector when the dependency contains models from other apps
    and additionally we do not want to create a dependency to the main project file, keeping the app loosely coupled     
    def ready(self):
       from swd_django_demo import container  # <-- import the container here so further imports inside container.py like models can succeed
       container.wire(modules=[".views"])
    """
