from django.db import models
from user.models import User
from book.models import Book


class Cart(models.Model):
    total_quantity = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CartItem(models.Model):
    price = models.IntegerField()
    quantity = models.IntegerField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
