from django.contrib.auth import authenticate
from django.shortcuts import render

# Create your views here.
from .serializers import UserSerializer
from django.core.cache import cache
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth import get_user_model

class SendVerificationCodeView(APIView):
    def post(self, request):
        """
        ### Verification Generator
        * Method: POST
        ### Request Body:
            - email:[user or manager's email]
        ### Success Response
            Message: "Verification code has been generated
        """
        email = request.data.get('email')
        if not email:
            return Response({"error": "E-mail is required."}, status=400)

        # 生成四位数的验证码
        code = random.randint(1000, 9999)
        # 使用邮箱作为键，将验证码存储到缓存中，设置过期时间为5分钟
        cache.set(f'v_code_{email}', code, timeout=300)
        print("code: ", code)

        return Response({"message": "Verification code has been generated."}, status=200)


class RegisterView(APIView):
    """
           ### Register
           * Method: POST
           ###  Request Body:
               - email: [user or manager's email]
               - password [password]
               - user_type [user or manager]
               - username [username]
               - v_code [manager's code]

           ### Success Response
               "message": "Registration successful",
                "user": {
                    "id": 6,
                    "email": "Albert.Zhang@gmail.com",
                    "username": "Albert",
                    "user_type": "manager"
                }
           """
    def post(self, request):
        data = request.data
        email = data.get('email')
        user_type = data.get('user_type')  # 提供默认值为'user'
        verification_code = data.get('v_code', None)
        stored_code = cache.get(f'v_code_{email}')

        # 如果是管理员类型，验证验证码
        if user_type == 'manager':
            if not verification_code or str(verification_code) != str(stored_code):
                return Response({"error": "无效或错误的验证码"}, status=status.HTTP_400_BAD_REQUEST)
            cache.delete(f'v_code_{email}')  # 验证码正确后清除

        # 使用序列化器进行数据验证和保存
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            # 注册成功后，可以根据需要返回用户的一些信息，但不应该返回密码
            return Response({"message": "注册成功。",
                             "user": {"id": user.id, "email": user.email, "username": user.username,
                                      "user_type": user.user_type}}, status=status.HTTP_201_CREATED)
        else:
            # 如果数据验证失败，返回错误
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, format=None):
        """
        ### Login
        * Method: POST
        ###  Request Body:
            - email: [user or manager's email]
            - password [password]
            - user_type [user or manager]
        ### Success Response
            "token": "**",
            "user_type": "manager",
            "email": "Albert.Zhang@gmail.com",
            "username": "Albert"
        """
        email = request.data.get('email')
        password = request.data.get('password')
        user_type = request.data.get('user_type')  # 默认为'user'
        user = authenticate(request, username=email, password=password)

        if user is not None and user.user_type == user_type:
            if not user.is_active:
                return Response({"error": "User account is not active."}, status=status.HTTP_401_UNAUTHORIZED)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "id": user.id,
                "user_type": user.user_type,
                "email": user.email,
                "username": user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials or user type."}, status=status.HTTP_401_UNAUTHORIZED)
