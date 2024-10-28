from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from .models import User, Lesson, Progress, School, Session
from rest_framework.authtoken.models import Token

class ProgressViewTestCase(TestCase):
    def setUp(self):
        # Create the Student group if it doesn't exist
        student_group, created = Group.objects.get_or_create(name='Student')

        # Create a test school
        self.school = School.objects.create(name='Test School')

        # Create a test user (student) using the custom fields (nickname, pin) instead of 'username'
        self.student_user = User.objects.create(
            nickname='test_student',
            pin='1234',
            school=self.school  # Assign the student to the school
        )
        
        # Set the password using set_password
        self.student_user.set_password('password123')
        self.student_user.save()

        # Assign the student role
        self.student_user.groups.add(student_group)
        self.student_user.save()

        # Create a test session for the lesson
        self.session = Session.objects.create(
            title='Test Session',
            teacher=self.student_user,  # Assuming the user is also the teacher for simplicity
            school=self.school
        )

        # Create a test lesson, making sure to assign the school and session
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            content='Sample content',
            school=self.school,  # Assign the lesson to the school
            session=self.session  # Assign the lesson to the session (fixes the session_id constraint)
        )

        # Create a progress entry for the student and lesson, making sure to assign the school
        self.progress = Progress.objects.create(
            student=self.student_user,
            lesson=self.lesson,
            score=85,
            completed=True,
            school=self.school  # Assign the school to the progress (fixes the school_id constraint)
        )

        # Set up the client and get the authentication token
        self.client = APIClient()
        
        # Login and get token
        response = self.client.post(reverse('login'), {
            'nickname': 'test_student', 
            'pin': '1234'
        })

        # Check that login was successful and set the token for authenticated requests
        if 'token' in response.data:
            self.token = response.data['token']
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        else:
            raise ValueError(f"Login failed: {response.data}")


    def test_progress_view(self):
        # Test fetching progress data
        response = self.client.get(reverse('progress'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['score'], 85)
        self.assertEqual(response.data[0]['completed'], True)
