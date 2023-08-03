from datetime import timedelta
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from cinema_house.settings import TOKEN_LIFETIME


class TokenExpiredAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key=key)
        if (token.created + timedelta(seconds=TOKEN_LIFETIME)) < timezone.now():
            token.delete()
            raise exceptions.AuthenticationFailed('Token lifetime is over!')
        return user, token

