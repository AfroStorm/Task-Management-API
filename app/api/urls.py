from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tasks', views.TaskView)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view())
]
