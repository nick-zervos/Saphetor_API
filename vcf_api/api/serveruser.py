from django.contrib.auth.models import AnonymousUser

class ServerUser(AnonymousUser):

    @property
    def is_authenticated(self):
        # Always return True. This is a way to tell if
        # the user has been authenticated in permissions
        return True