# backend\message\serializers.py:

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~


class PasswordResetInitSerializer(serializers.Serializer):
    # email = serializers.EmailField(required=True)
    # delivery_method = serializers.ChoiceField(
    #     choices=["telegram", "sms", "email"], required=True
    # )
    # email = serializers.EmailField(required=True)
    delivery_method = "telegram"


class PasswordResetConfirmSerializer(serializers.Serializer):
    # email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
