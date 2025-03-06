# backend\management\serializers.py:

from rest_framework import serializers
from django.contrib.auth.hashers import make_password

#
from .models import Relation, User

# ~~~~~~~~~~~~~~~~~~~~ User ~~~~~~~~~~~~~~~~~~~~


from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователей.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["email", "password", "phone_number"]

        extra_kwargs = {
            "email": {"required": True, "write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone_number=validated_data["phone_number"],
        )
        return user


class SigninSerializer(serializers.Serializer):
    """
    Сериализатор для входа (получения токенов).
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass


class LogoutSerializer(serializers.Serializer):
    """
    Сериализатор для выхода (logout) — принимает refresh токен.
    """

    refresh = serializers.CharField(required=True)

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        try:
            RefreshToken(attrs["refresh"])
        except Exception as e:
            raise serializers.ValidationError("Токен недействителен или уже отозван.")
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "email", "phone_number", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        """Шифруем пароль при сериализации."""
        return make_password(value)


# ~~~~~~~~~~~~~~~~~~~~ Relation ~~~~~~~~~~~~~~~~~~~~


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = [
            "uuid",
            "organization",
            "branch",
            "user",
            "user_role",
            "relation_type",
        ]
