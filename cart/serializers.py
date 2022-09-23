from rest_framework import serializers
from .models import CartItem, Cart
from book.models import Book
from pyee.base import EventEmitter
from django.db.models import Sum
import logging

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()

ee = EventEmitter()


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'price', 'quantity', 'book', 'user', 'cart']
        extra_kwargs = {'price': {'required': False},
                        'cart': {'required': False}}


class CartSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(write_only=True)
    book = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Book.objects.all())

    class Meta:
        model = Cart
        fields = ['id', 'total_price', 'total_quantity', 'status', 'user', 'quantity', 'book']
        extra_kwargs = {'status': {'required': False},
                        'total_price': {'required': False},
                        'total_quantity': {'required': False}}

    def create(self, validated_data):
        user = validated_data.get('user')
        book = validated_data.get('book')
        cart_list = Cart.objects.filter(user=user).values_list('status', flat=True).order_by('status')
        if 0 in cart_list:
            cart = Cart.objects.get(status=cart_list[0], user=user)
            ee.emit('add', cart, book, user, validated_data)
            return cart
        cart = Cart.objects.create(user=user)
        ee.emit('add', cart, book, user, validated_data)
        return cart

    def update(self, instance, validated_data):
        user = validated_data.get('user')
        book = validated_data.get('book')
        cart_item = CartItem.objects.filter(cart=instance.id, user_id=user, book=book.id)
        count = validated_data.get('quantity') - cart_item.count()
        if count > 0:
            for num in range(count):
                CartItem.objects.create(price=book.price, quantity=1, book=book, user=user, cart_id=instance.id)
            total_price = CartItem.objects.filter(cart_id=instance.id,
                                                  user=user).values_list('price', flat=True).aggregate(Sum('price'))
            instance.total_price = total_price.get('price__sum')
            instance.total_quantity = validated_data.get('quantity')
            instance.save()
        if count < 0:
            for num in range(abs(count)):
                cart_item[num].delete()
            total_price = CartItem.objects.filter(cart=instance.id,
                                                  user=user).values_list('price', flat=True).aggregate(Sum('price'))
            instance.total_price = total_price.get('price__sum')
            instance.total_quantity = validated_data.get('quantity')
            instance.save()
        return instance


@ee.on('add')
def add_cart(cart, book, user, validated_data):
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
        logger.exception(ex)
