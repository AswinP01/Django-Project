from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q 

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Search for users by username or email
            users = UserModel.objects.filter(
                Q(username=username) | Q(email=username)
            )
            
            # Ensure we only get one user
            if users.count() == 1:
                user = users.first()
                if user.check_password(password):
                    return user
            elif users.count() > 1:
                # Handle the case where there are multiple users
                raise Exception("Multiple users found with the same username or email.")
        except Exception as e:
            # Optionally log the error
            print(f"Authentication error: {e}")
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None