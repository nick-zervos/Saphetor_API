from .serveruser import ServerUser
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from vcf_api import settings


#Create a custom authentication class to use as a decorator for our views.
class PredefinedSecret(authentication.BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')

        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        token = auth[1].decode()

        if not (settings.CUSTOM_SERVER_AUTH_TOKEN == token):
            raise exceptions.AuthenticationFailed('You do not have permission to access this resource or you entered an invalid token')

        user = ServerUser()

        return user, None