from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate using email
    instead of username. Email comparison is case-insensitive.
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Use case-insensitive email lookup
            if email:
                email = email.lower().strip()
                user = CustomUser.objects.get(email__iexact=email)
            else:
                return None
        except CustomUser.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
