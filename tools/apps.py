from django.apps import AppConfig


class ToolsConfig(AppConfig):
    name = 'tools'

    def ready(self):
        import tools.admin