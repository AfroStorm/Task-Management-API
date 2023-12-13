from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tasks', views.TaskView)
router.register('task-groups', views.TaskGroupView)
router.register('position', views.PositionView)
router.register('category', views.CategoryView)
router.register('priority', views.PriorityView)
router.register('status', views.StatusView)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view())
]
