from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # Authentication password not less than 8 digits
        if len(value) < 8:
            raise serializers.ValidationError("Passwords must be at least 8 digits in length.")
        # Verify that the password is case sensitive
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Passwords must contain at least one lowercase letter.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("The password must contain at least one uppercase letter.")

        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)  # 确保使用username而不是name
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class PasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 digits long.")
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Passwords must contain at least one lowercase letter.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("The password must contain at least one uppercase letter.")
        return value

    def update(self, instance, validated_data):
        old_password = validated_data.get('old_password')
        if not instance.check_password(old_password):
            raise serializers.ValidationError({"old_password": "The old password is incorrect."})
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