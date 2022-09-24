from django.shortcuts import render
from .models import User
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import JWT, TokenRole, verify_token
from events import ee
import logging

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class UserRegistration(APIView):
    """
    This class register user to the database
    """
    def post(self, request):
        try:
            serializer = RegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = JWT.encode({'user_id': serializer.data.get('id'), 'username': serializer.data.get('username'),
                                'role': TokenRole.verify_user.value})
            ee.emit('send_mail', {'token': token, 'recipient': serializer.data.get('email'),
                                  'role': TokenRole.verify_user.value})
            return Response({'message': 'User Created', 'status': 201, 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    """
    This class used to login the user
    """
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = JWT.encode({'user_id': serializer.data.get('id'), 'username': serializer.data.get('username'),
                                'role': TokenRole.auth.value})
            return Response({'message': 'Login Successful', 'status': 202, 'data': token},
                            status=status.HTTP_202_ACCEPTED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)


class UserVerification(APIView):
    """
    This class verify the user registration
    """
    def get(self, request, token):
        try:
            decode = JWT.decode(token)
            if decode.get('role') != TokenRole.verify_user.value:
                raise Exception('Invalid Token Role')
            user = User.objects.get(username=decode.get('username'))
            if user is not None:
                user.is_verified = 1
                user.save()
                return Response({'message': 'User Verified', 'status': 202, 'data': {}},
                                status=status.HTTP_202_ACCEPTED)
            return Response({'message': 'Invalid User', 'status': 406, 'data': {}},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
    """
    This class changes the password of a user
    """
    @verify_token
    def post(self, request):
        try:
            if request.data.get('new_password') != request.data.get('confirm_password'):
                raise Exception("""New passwords doesn't match""")
            user = User.objects.get(username=request.data.get('username'))
            if not user or not user.check_password(request.data.get('old_password')):
                raise Exception("""user and password doesn't match""")
            user.set_password(request.data.get('new_password'))
            user.save()
            return Response({'message': 'Password changed successfully', 'status': 202, 'data': {}},
                            status=status.HTTP_202_ACCEPTED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):
    """
    This class send a link to user's mail to reset the password
    """
    def post(self, request):
        try:
            user = User.objects.get(username=request.data.get('username'), email=request.data.get('email'))
            if not user:
                raise Exception('Invalid username or email')
            token = JWT.encode({'user_id': user.id, 'username': user.username, 'role': TokenRole.forgot_password.value})
            ee.emit('send_mail', {'token': token, 'recipient': user.email, 'role': TokenRole.forgot_password.value})
            return Response({'message': 'Password reset link sent to your mail', 'status': 200, 'data': {}},
                            status=status.HTTP_200_OK)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPassword(APIView):
    """
    This class verify the link and reset password with new one
    """
    def post(self, request, token):
        try:
            decode = JWT.decode(token)
            if decode.get('role') != TokenRole.forgot_password.value:
                raise Exception('Invalid Token Role')
            if request.data.get('new_password') != request.data.get('confirm_password'):
                raise Exception("""New passwords doesn't match""")
            user = User.objects.get(id=decode.get('user_id'), username=decode.get('username'))
            if not user:
                raise Exception('User not found')
            user.set_password(request.data.get('new_password'))
            user.save()
            return Response({"message": "Password Reset Successful", "status": 202, "data": {}},
                            status=status.HTTP_202_ACCEPTED)
        except Exception as ex:
            logger.exception(ex)
            return Response({'message': str(ex), 'status': 400, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

