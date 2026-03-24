from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.user_list, name='user_list'),
    path('<int:user_id>/', views.user_detail, name='user_detail'),
    path('authors/', include('author.urls')),
]
