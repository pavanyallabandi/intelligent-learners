from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('group/create/', views.create_group, name='create_group'),
    path('group/search/', views.search_group, name='search_group'),
    path('group/<uuid:group_id>/', views.group_detail, name='group_detail'),
    path('group/<uuid:group_id>/add-video/', views.add_video, name='add_video'),
    path('group/<uuid:group_id>/manage/', views.manage_requests, name='manage_requests'),
    path('video/mark-completed/', views.mark_video, name='mark_video'),
]
