from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import BookSerializer
from .models import Book
from rest_framework.response import Response
from rest_framework import status
from user.utils import verify_token
import logging

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class BooksApi(APIView):

    @verify_token
    def post(self, request):
        try:
            serializer = BookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Book Added', 'status': 201, 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

    @verify_token
    def get(self, request):
        try:
            books = Book.objects.filter(user_id=request.data.get('user'))
            serializer = BookSerializer(books, many=True)
            return Response({'message': 'Books Retrieved', 'status': 200, 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

    @verify_token
    def put(self, request):
        try:
            book = Book.objects.get(id=request.data.get('id'), user_id=request.data.get('user'))
            serializer = BookSerializer(book, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Book Updated', 'status': 201, 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

    @verify_token
    def delete(self, request):
        try:
            book = Book.objects.get(id=request.data.get('id'), user_id=request.data.get('user'))
            book.delete()
            return Response({'message': 'Book Deleted', 'status': 204, 'data': {}}, status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
