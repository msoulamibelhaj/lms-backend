from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, School, Class, Session, Lesson, Progress

admin.site.register(User)
admin.site.register(School)
admin.site.register(Class)
admin.site.register(Session)
admin.site.register(Lesson)
admin.site.register(Progress)
