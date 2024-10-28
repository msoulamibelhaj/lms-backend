from django.apps import AppConfig

class LmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms'

    def ready(self):
        # Avoid import errors by importing models here
        from django.contrib.auth.models import Group
        from django.db.models.signals import post_migrate

        # Create groups and roles after migrations are complete
        def create_roles(sender, **kwargs):
            # Create Admin, Teacher, and Student groups
            Group.objects.get_or_create(name='Admin')
            Group.objects.get_or_create(name='Teacher')
            Group.objects.get_or_create(name='Student')

        post_migrate.connect(create_roles, sender=self)
