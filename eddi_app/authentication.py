import pytz
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from eddi_app.models import NonBuiltInUserToken


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Expiring token for mobile and desktop clients.
    It expires every {n} hrs requiring client to supply valid username 
    and password for new one to be created.
    """

    model = NonBuiltInUserToken

    def authenticate_credentials(self, key, request=None):
        models = self.get_model()

        try:
            token = models.objects.select_related("user").get(key=key)

        except models.DoesNotExist:
            raise AuthenticationFailed(
                {"error": "Invalid or Inactive Token", "is_authenticated": False}
            )

        if not token.user.status.id == 1:
            raise AuthenticationFailed(
                {"error": "Invalid user", "is_authenticated": False}
            )

        utc_now = timezone.now()
        utc_now = utc_now.replace(tzinfo=pytz.utc)

        if token.created < utc_now - settings.TOKEN_TTL:
            raise AuthenticationFailed(
                {"error": "Token has expired", "is_authenticated": False}
            )
        return token.user, token