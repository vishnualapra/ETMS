"""etms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from api import urls as apiurls
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('project', views.Projects, basename='project')
router.register('user', views.Users, basename='user')
router.register('team', views.Team, basename='team')
router.register('task', views.Task, basename='task')
router.register('comment', views.Comment, basename='comment')
router.register('reports', views.GetReport, basename='report')
urlpatterns = router.urls
urlpatterns += [
    path('ping/', views.Ping.as_view()),
    path('login/',views.Login.as_view()),
    path('logout/', views.Logout.as_view()),
    path('listusers/', views.ListUsers.as_view()),
    path('gettask/<int:id>/', views.GetTask.as_view()),
    path('gettask/<int:id>/<str:status>/', views.GetTask.as_view()),
    path('projectstatus/<int:id>/', views.PStatus.as_view()),
    path('count/', views.DashCount.as_view()),
    path('report/', views.Report.as_view()),
]
