from rest_framework import serializers
from .models import User, School, Class, Session, Lesson, Progress

# User serializer for nickname and PIN authentication
class UserSerializer(serializers.ModelSerializer):
    school = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'nickname', 'school', 'is_staff', 'is_active']

# School Serializer
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name']

# Class Serializer
class ClassSerializer(serializers.ModelSerializer):
    teacher = UserSerializer()
    students = UserSerializer(many=True)  # Include students

    class Meta:
        model = Class
        fields = ['id', 'name', 'teacher', 'students']  # Adjust fields as necessary

# Lesson Serializer
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'lesson_class']

# Session Serializer
class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'title', 'teacher', 'is_active', 'is_paused', 'created_at', 'started_at', 'stopped_at']

# Progress Serializer
class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['id', 'student', 'lesson', 'score', 'completed', 'progress_data']
