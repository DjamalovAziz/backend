# backend\user\serializers.py:

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

#
from .models import Avatar, User


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "uuid",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "avatar_url",
        )
        read_only_fields = ("uuid", "avatar_url")

    def get_avatar_url(self, obj):
        if hasattr(obj, "avatar") and obj.avatar:
            return obj.get_avatar_url()
        # For Multiple Avatar scenario, get primary avatar
        return obj.get_primary_avatar_url()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone_number",
            "avatar",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data.update({"user": UserSerializer(self.user).data})

        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs


class AvatarSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ("uuid", "image_url", "is_primary", "created_at")
        read_only_fields = ("uuid", "image_url", "created_at")

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class AvatarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ("image", "is_primary")


class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ("image", "is_primary")


class UserUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "avatar",
        )
