from django.contrib.auth.models import AnonymousUser


#used so that the client does not need to have a user in order to use the API
class ServerUser(AnonymousUser):

    @property
    def is_authenticated(self):
        # Always return True. This is a way to tell if
        # the user has been authenticated in permissions
        return True