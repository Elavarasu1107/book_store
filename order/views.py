from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import OrderSerializer, GetSerializer
from user.utils import verify_token
from .models import OrderItem, Order
import logging

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class OrderApi(APIView):

    @verify_token
    def post(self, request):
        """
        Place the order for the given cart id
        """
        try:
            serializer = OrderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Order Placed', 'status': 201, 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

    @verify_token
    def get(self, request):
        """
        Retrieves the order data from the database
        """
        try:
            orders = Order.objects.filter(user=request.data.get('user'))
            serializer = GetSerializer(orders, many=True)
            return Response({'message': 'Order Retrieved', 'status': 200, 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

    @verify_token
    def delete(self, request):
        """
        Cancels the order
        """
        try:
            order = Order.objects.get(id=request.data.get('id'), user_id=request.data.get('user'))
            order.delete()
            return Response({'message': 'Order Deleted', 'status': 204, 'data': {}}, status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
