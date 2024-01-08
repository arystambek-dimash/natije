from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Role, User, Profile


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'role']
        read_only_fields = ['role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'profile_picture', 'test_limit', 'user']
        read_only_fields = ['user', 'test_limit']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        profile = Profile.objects.create(user=user, **validated_data)
        return profile


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
            'password': {'required': False, 'write_only': True},
        }

        def validate_email(self, value):
            """
            Check if the email is already in use.
            """
            user = self.instance
            if user and user.email == value:
                return value
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('This email is already in use.')
            return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer(required=False)

    class Meta:
        model = Profile
        fields = ['id', 'profile_picture', 'test_limit', 'user']
        read_only_fields = ['test_limit']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user_instance = instance.user
        user_instance.first_name = user_data.get('first_name', user_instance.first_name)
        user_instance.last_name = user_data.get('last_name', user_instance.last_name)
        user_instance.email = user_data.get('email', user_instance.email)
        new_password = user_data.get('password')
        if new_password:
            user_instance.set_password(new_password)

        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.save()
        user_instance.save()

        return instance
