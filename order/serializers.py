from rest_framework import serializers
from pyee.base import EventEmitter
from .models import Order, OrderItem
from book.models import Book
import logging

ee = EventEmitter()
logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class GetSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField('get_order_items')

    def get_order_items(self, order):
        details = order.orderitem_set.filter(user_id=order.user, order_id=order.id).distinct('book_id')
        item_list = []
        for item in details:
            count = order.orderitem_set.filter(user_id=order.user, book_id=item.book, order_id=order.id).count()
            item_list.append({'book_id': item.book.id, 'book_name': item.book.title, 'quantity': count})
        return item_list

    class Meta:
        model = Order
        fields = ['id', 'items']
        read_only_fields = ['items']


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'total_quantity', 'total_price', 'user', 'cart']

    def create(self, validated_data):
        cart = validated_data.get('cart')
        cart_items = cart.cartitem_set.filter(cart=validated_data.get('cart')).values_list('book', flat=True)
        order = Order.objects.create(cart=cart, user=validated_data.get('user'))
        validated_data.update({'cart_items': cart_items, 'order': order, 'quantity': len(cart_items)})
        ee.emit('orders', validated_data)
        order.total_quantity = cart.total_quantity
        order.total_price = cart.total_price
        order.save()
        ee.emit('cart_status', cart)
        return order


@ee.on('orders')
def order_items(validated_data):
    try:
        order_items_data = []
        for i in range(validated_data.get('quantity')):
            book_id = validated_data.get('cart_items')
            book = Book.objects.get(id=book_id[i])
            order_items_data.append(OrderItem(user=validated_data.get('user'), book=book,
                                              order=validated_data.get('order')))
        OrderItem.objects.bulk_create(order_items_data)
    except Exception as ex:
        logger.exception(ex)


@ee.on('cart_status')
def cart_status(cart):
    try:
        cart.status = 1
        cart.save()
    except Exception as ex:
        logger.exception(ex)
