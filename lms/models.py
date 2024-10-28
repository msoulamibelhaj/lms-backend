import json
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Custom User model
class School(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class User(AbstractUser):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    nickname = models.CharField(max_length=20, unique=True)
    
    # Validator to ensure the pin consists of only 4 digits
    pin_validator = RegexValidator(r'^\d{4}$', 'PIN must be a 4-digit number.')
    
    pin = models.CharField(max_length=4, validators=[pin_validator])  # 4-digit PIN for authentication
    
    role = models.CharField(max_length=10, choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ], default='student')  # Default role can be set as 'student'

    def __str__(self):
        return self.nickname

class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_classes")  # Teacher relationship
    students = models.ManyToManyField(User, related_name="student_classes")  # Students relationship

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Classes"

class Session(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_paused = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    stopped_at = models.DateTimeField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)

    def notify_students(self):
        # Check if the notification has already been sent
        if not self.notification_sent:
            # Get the channel layer
            channel_layer = get_channel_layer()
            group_name = f'session_{self.id}'  # Unique group for the session

            # Notify all students in the session
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'session.notification',
                    'message': f'Session "{self.title}" has started!',
                }
            )
            self.notification_sent = True  # Mark notification as sent
            self.save(update_fields=['notification_sent'])  # Save the change

    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()  # SCORM package metadata can be linked here
    lesson_class = models.CharField(max_length=255, default='General')  # Provide a sensible default
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='lessons')  # Use the correct reference
    def __str__(self):
        return self.title

class Progress(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    progress_data = models.JSONField(null=True, blank=True)  # SCORM progress tracking
    def __str__(self):
        return f"{self.student.nickname} - {self.lesson.title}"

    class Meta:
        verbose_name_plural = "Progress"