from rest_framework import serializers
from .models import CartItem, Cart
from book.models import Book
from events import ee
import logging

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


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
        ee.emit('update', instance, user, book, cart_item, count)
        return instance
