from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User
import logging

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class RegistrationSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        """
       Create and return a new user instance, given the validated data.
       """
        try:
            return User.objects.create_user(**validated_data)
        except Exception as ex:
            logger.exception(ex)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'phone', 'location']
        extra_kwargs = {'password': {'write_only': True}}


class LoginSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)

    def create(self, validated_data):
        user = authenticate(**validated_data)
        if not user:
            raise Exception('Invalid Credentials')
        if user.is_verified == 0:
            raise Exception('Invalid User')
        return user
