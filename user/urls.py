from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
   path('login/', ... , 'login'),
   path('logout/', ..., 'logout'),
   path('register/', ..., 'register')
]