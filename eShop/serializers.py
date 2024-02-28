from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'user_type']  # 根据你的模型自定义字段
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # 验证密码不少于8位
        if len(value) < 8:
            raise serializers.ValidationError("密码必须至少为8位长。")
        # 验证密码包含大小写
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("密码必须包含至少一个小写字母。")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("密码必须包含至少一个大写字母。")
        # 只验证密码复杂性，不在这里加密密码
        return value

    def create(self, validated_data):
        # 从validated_data中提取密码，并使用pop移除它
        password = validated_data.pop('password')
        # 创建用户实例
        user = CustomUser.objects.create(**validated_data)
        # 设置密码
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # 更新用户信息
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)  # 确保使用username而不是name
        password = validated_data.get('password')
        if password:
            # 设置新密码
            instance.set_password(password)
        instance.save()
        return instance

class PasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # 验证新密码的复杂性要求
        if len(value) < 8:
            raise serializers.ValidationError("密码必须至少为8位长。")
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("密码必须包含至少一个小写字母。")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("密码必须包含至少一个大写字母。")
        return value

    def update(self, instance, validated_data):
        # 验证旧密码是否正确
        old_password = validated_data.get('old_password')
        if not instance.check_password(old_password):
            raise serializers.ValidationError({"old_password": "The old password is incorrect."})
        # 设置新密码
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username']
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
        }