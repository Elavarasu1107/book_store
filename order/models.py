from django.db import models
from user.models import User
from book.models import Book
from cart.models import Cart


class Order(models.Model):
    total_quantity = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
