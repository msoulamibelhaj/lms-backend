from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from .models import User, Session, Lesson, Class, Progress
from .serializers import SessionSerializer, LessonSerializer, ProgressSerializer, ClassSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from .permissions import IsTeacher, IsSchoolAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

User = get_user_model()

# Login View
class LoginView(APIView):
    def post(self, request):
        nickname = request.data.get('nickname')
        pin = request.data.get('pin')

        user = User.objects.filter(nickname=nickname).first()

        # Check if user exists and PIN matches
        if user and user.pin == pin:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'nickname': user.nickname,
                    'school': user.school.name if user.school else None,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# Fetch Classes Enrolled in
class ClassListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filter classes by the user's school
        user_classes = request.user.student_classes.filter(school=request.user.school)
        serialized_classes = ClassSerializer(user_classes, many=True).data
        return Response(serialized_classes)

# Create Session (Teachers Only)
class CreateSessionView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        teacher = request.user
        title = request.data.get('title')

        # Ensure session is created under the teacher's school
        session = Session.objects.create(teacher=teacher, title=title, school=teacher.school)
        return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)


# Add Lesson to Session (Teachers Only)
class AddLessonView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        session_id = request.data.get('session_id')
        title = request.data.get('title')
        content = request.data.get('content')

        try:
            # Ensure session is from the same school as the teacher
            session = Session.objects.get(id=session_id, teacher=request.user, school=request.user.school)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the lesson is created under the teacher's school
        lesson = Lesson.objects.create(session=session, title=title, content=content, school=request.user.school)
        return Response(LessonSerializer(lesson).data, status=status.HTTP_201_CREATED)


# Start Session (Teachers Only)
class StartSessionView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        session_id = request.data.get('session_id')

        # Ensure session belongs to the teacher and their school
        session = Session.objects.get(id=session_id, teacher=request.user, school=request.user.school)
        session.is_active = True
        session.started_at = timezone.now()  # Use timezone to set the current time
        session.save()
        
        # Notify students through WebSocket
        session.notify_students()  # This will trigger the WebSocket notification
        return Response({'message': 'Session started'}, status=status.HTTP_200_OK)


# Pause Session (Teachers Only)
class PauseSessionView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        session_id = request.data.get('session_id')

        # Ensure session belongs to the teacher and their school
        session = Session.objects.get(id=session_id, teacher=request.user, school=request.user.school)
        if session.is_active:
            session.is_paused = True
            session.save()
            return Response({'message': 'Session paused'}, status=status.HTTP_200_OK)
        return Response({'error': 'Session is not active'}, status=status.HTTP_400_BAD_REQUEST)


# Stop Session (Teachers Only)
class StopSessionView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        session_id = request.data.get('session_id')

        # Ensure session belongs to the teacher and their school
        session = Session.objects.get(id=session_id, teacher=request.user, school=request.user.school)
        session.is_active = False
        session.stopped_at = now()
        session.save()
        return Response({'message': 'Session stopped'}, status=status.HTTP_200_OK)


# Get Progress for SCORM Lessons
class ProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure progress is filtered by the student's school
        progress = Progress.objects.filter(student=request.user, lesson__school=request.user.school)
        return Response(ProgressSerializer(progress, many=True).data)

#NO URLS FOR THESE SO FAR
# Admin: List all users in the admin's school (Admin Only)
class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get(self, request):
        # Get all users from the admin's school
        users = User.objects.filter(school=request.user.school)
        return Response(UserSerializer(users, many=True).data)


# Admin: Create new user in the admin's school (Admin Only)
class AdminCreateUserView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def post(self, request):
        # Create a new user in the same school as the admin
        nickname = request.data.get('nickname')
        pin = request.data.get('pin')
        role = request.data.get('role')  # Either 'student' or 'teacher'

        user = User.objects.create(nickname=nickname, pin=pin, school=request.user.school)

        if role == 'teacher':
            user.groups.add(Group.objects.get(name='Teacher'))
        elif role == 'student':
            user.groups.add(Group.objects.get(name='Student'))

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

from django.shortcuts import render

def websocket_view(request):
    return render(request, 'lms/websocket.html')

def index_view(request):
    return render(request, 'lms/index.html')