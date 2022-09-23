from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.OrderApi.as_view(), name='orders'),
]
