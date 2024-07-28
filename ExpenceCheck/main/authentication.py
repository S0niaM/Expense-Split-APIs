from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        UserModel = get_user_model()
        try:
            if '@' in username:
                user = UserModel.objects.get(email=username)
            else:
                user = UserModel.objects.get(phone=username)
        except UserModel.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None
