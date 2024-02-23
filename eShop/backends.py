from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    自定义的认证后端，支持使用电子邮件和密码进行认证。
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            print("username: ", username)
            user = UserModel.objects.get(email__iexact=username)
            print(user)
            print(user.check_password(password))
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except UserModel.DoesNotExist:
            UserModel().set_password(password)  # 密码散列，避免安全警告
        except MultipleObjectsReturned:
            return UserModel.objects.filter(email__iexact=username).order_by('id').first()