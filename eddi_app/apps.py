from django.apps import AppConfig


class EddiAppConfig(AppConfig):
    name = 'eddi_app'

    def ready(self):
        import eddi_app.signals
   

