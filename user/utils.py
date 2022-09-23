import jwt
from enum import Enum
from django.conf import settings
import logging
from django.core.mail import send_mail
from rest_framework.reverse import reverse

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class TokenRole(Enum):
    default = 'null'
    auth = 'Auth'
    verify_user = 'VerifyUser'
    forgot_password = 'ForgotPassword'


class JWT:

    @staticmethod
    def encode(payload):
        try:
            if not isinstance(payload, dict):
                raise Exception('payload should be in dict')
            if 'exp' not in payload.keys():
                payload.update({'exp': settings.JWT_EXP})
            if 'role' not in payload.keys():
                payload.update({'role': TokenRole.default.value})
            return jwt.encode(payload, 'secret', algorithm='HS256')
        except Exception as ex:
            logger.exception(ex)

    @staticmethod
    def decode(token):
        try:
            return jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.exceptions.ExpiredSignatureError:
            raise Exception("Token Expired")
        except jwt.exceptions.InvalidTokenError:
            raise Exception("Invalid Token")
        except Exception as ex:
            logger.exception(ex)


def send_email(payload):
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
        logger.exception(ex)


def verify_token(function):
    def wrapper(self, request):
        token = request.headers.get('token')
        if not token:
            raise Exception('Auth token required')
        decode = JWT.decode(token)
        if decode.get('role') != TokenRole.auth.value:
            raise Exception('Invalid Token Role')
        user_id = decode.get('user_id')
        username = decode.get('username')
        if not user_id or not username:
            raise Exception('User not found')
        request.data.update({'user': user_id, 'username': username})
        return function(self, request)
    return wrapper
