from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ItemSerializer, CartSerializer
from .models import Cart, CartItem
from user.utils import verify_token
import logging

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class CartApi(APIView):

    @verify_token
    def post(self, request):
        """
        Adds the book to the cart
        """
        try:
            serializer = CartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Cart Created', 'status': 201, 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

    @verify_token
    def get(self, request):
        """
        Retrieves the cart data from the database
        """
        try:
            items = Cart.objects.filter(user=request.data.get('user'))
            serializer = CartSerializer(items, many=True)
            return Response({'message': 'Carts Retrieved', 'status': 200, 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

    @verify_token
    def put(self, request):
        """
        Updates the quantity of books in the cart
        """
        try:
            cart = Cart.objects.get(id=request.data.get('cart'))
            serializer = CartSerializer(cart, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Cart Updated', 'status': 201, 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

    @verify_token
    def delete(self, request):
        """
        Deletes the cart
        """
        try:
            cart = Cart.objects.get(id=request.data.get('id'), user_id=request.data.get('user'))
            cart.delete()
            return Response({'message': 'Cart Deleted', 'status': 204, 'data': {}}, status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
