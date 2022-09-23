from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartApi.as_view(), name='cart'),
]
