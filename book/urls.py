from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.BooksApi.as_view(), name='books'),
]
