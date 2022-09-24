from django.db.models import Sum
from cart.models import CartItem
from order.models import Order, OrderItem
from pyee.base import EventEmitter
from book.models import Book
from django.conf import settings
from user.utils import TokenRole
from rest_framework.reverse import reverse
from django.core.mail import send_mail
import logging

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()

ee = EventEmitter()


@ee.on('error')
def errors(ex):
    logger.exception(ex)


@ee.on('send_mail')
def send_email(payload):
    """
    Sends mail to the user to register and reset password
    """
    try:
        subject, link = '', ''
        if payload.get('role') == TokenRole.verify_user.value:
            subject = 'Book Store Registration'
            link = settings.BASE_URL + reverse('verify_user', kwargs={'token': payload.get('token')})
        if payload.get('role') == TokenRole.forgot_password.value:
            subject = 'Reset Password Link'
            link = settings.BASE_URL + reverse('verify_password', kwargs={'token': payload.get('token')})
        send_mail(subject=subject,
                  message=f'Link will get expired after one hour of generation\n' + link,
                  from_email=None,
                  recipient_list=[payload.get('recipient')])
    except Exception as ex:
        ee.emit('error', ex)


@ee.on('add')
def add_cart(cart, book, user, validated_data):
    """
    Creates cart items for the given quantity
    """
    try:
        cart_items_data = []
        for items in range(validated_data.get('quantity')):
            cart_items_data.append(CartItem(price=book.price, quantity=1, book=book, user=user, cart=cart))
        CartItem.objects.bulk_create(cart_items_data)
        cart.total_quantity += validated_data.get('quantity')
        total_price = CartItem.objects.filter(cart=cart).values_list('price', flat=True).aggregate(Sum('price'))
        cart.total_price = total_price.get('price__sum')
        cart.save()
    except Exception as ex:
        ee.emit('error', ex)


@ee.on('update')
def update_cart(instance, user, book, cart_item, count):
    """
    Updates the cart items for the given quantity
    """
    try:
        if count > 0:
            for num in range(count):
                CartItem.objects.create(price=book.price, quantity=1, book=book, user=user, cart_id=instance.id)
            total_price = CartItem.objects.filter(cart_id=instance.id,
                                                  user=user).values_list('price', flat=True).aggregate(Sum('price'))
            instance.total_price = total_price.get('price__sum')
            instance.total_quantity += count
            instance.save()
        if count < 0:
            for num in range(abs(count)):
                cart_item[num].delete()
            total_price = CartItem.objects.filter(cart_id=instance.id,
                                                  user=user).values_list('price', flat=True).aggregate(Sum('price'))
            instance.total_price = total_price.get('price__sum')
            instance.total_quantity += count
            instance.save()
    except Exception as ex:
        ee.emit('error', ex)


@ee.on('orders')
def order_items(validated_data):
    """
    Creates order items for the given cart id
    """
    try:
        order_items_data = []
        for i in range(validated_data.get('quantity')):
            book_id = validated_data.get('cart_items')
            book = Book.objects.get(id=book_id[i])
            order_items_data.append(OrderItem(user=validated_data.get('user'), book=book,
                                              order=validated_data.get('order')))
        OrderItem.objects.bulk_create(order_items_data)
    except Exception as ex:
        ee.emit('error', ex)


@ee.on('cart_status')
def cart_status(cart):
    """
    Updates the cart status if cart is ordered
    """
    try:
        cart.status = 1
        cart.save()
    except Exception as ex:
        ee.emit('error', ex)
