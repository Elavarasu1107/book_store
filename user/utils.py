import jwt
from enum import Enum
from django.conf import settings
import logging

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
