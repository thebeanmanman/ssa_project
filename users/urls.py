from django.urls import path
from . import views

urlpatterns = [
    path("", views.user, name="user"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path('register/', views.register, name='register'),
    path('top_up/', views.top_up, name='top_up') # Creates a path for the top_up page
]