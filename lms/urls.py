from django.urls import path, include
from .views import LoginView, ClassListView, CreateSessionView, AddLessonView, StartSessionView, PauseSessionView, StopSessionView, ProgressView, websocket_view, index_view
from channels.routing import ProtocolTypeRouter, URLRouter

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/classes/', ClassListView.as_view(), name='classes'),
    path('api/session/create/', CreateSessionView.as_view(), name='create-session'),
    path('api/session/addLesson/', AddLessonView.as_view(), name='add-lesson'),
    path('api/session/start/', StartSessionView.as_view(), name='start-session'),
    path('api/session/pause/', PauseSessionView.as_view(), name='pause-session'),
    path('api/session/stop/', StopSessionView.as_view(), name='stop-session'),
    path('api/results/', ProgressView.as_view(), name='progress'),
    path('websocket/', websocket_view, name='websocket'),
    path('index/', index_view, name='index'),
]

