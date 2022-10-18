from tokenize import Token
from rest_framework.permissions import BasePermission
from .models import NonBuiltInUserToken

class IsValid(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        # sourcery skip: assign-if-exp, boolean-if-exp-identity
        a = request.headers.get('Authorization')
        try:
            txt = a.split()
            model = NonBuiltInUserToken.objects.get(key = txt[1])
        except:
            model = None
        
        if model:
            return True
        else:
            return False