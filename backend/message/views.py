# backend\message\views.py:

import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import PasswordResetCode
from .serializers import PasswordResetInitSerializer, PasswordResetConfirmSerializer
from .tasks import send_reset_code

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~
# Set up logger
logger = logging.getLogger(__name__)

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_init(request):
    """
    Initiate password reset process
    """
    serializer = PasswordResetInitSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        delivery_method = serializer.validated_data["delivery_method"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.info(f"Password reset attempt for non-existent email: {email}")
            # We return a 200 OK to prevent email enumeration attacks
            return Response(
                {
                    "detail": "If your email exists in our system, you will receive a reset code."
                },
                status=status.HTTP_200_OK,
            )

        # Check if the requested delivery method is available for this user
        method_available = False

        if delivery_method == "telegram" and user.telegram_chat_id:
            method_available = True
        elif delivery_method == "sms" and user.phone_number:
            method_available = True
        elif delivery_method == "email":
            method_available = True

        if not method_available:
            logger.info(
                f"Password reset attempt using unavailable delivery method: {delivery_method} for user: {user.email}"
            )
            return Response(
                {
                    "detail": "The selected delivery method is not available for this account."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Invalidate any existing reset codes for this user
        PasswordResetCode.objects.filter(
            user=user, is_used=False, expires_at__gt=timezone.now()
        ).update(is_used=True)

        # Generate a new code
        code = PasswordResetCode.generate_code()
        reset_code = PasswordResetCode.objects.create(
            user=user, code=code, delivery_method=delivery_method
        )

        # Send the code via the selected method
        try:
            send_reset_code(user, code, delivery_method)
            logger.info(
                f"Password reset code sent successfully to {user.email} via {delivery_method}"
            )
        except Exception as e:
            logger.error(
                f"Error sending password reset code to {user.email} via {delivery_method}: {str(e)}"
            )
            reset_code.delete()  # Delete the code since it wasn't sent
            return Response(
                {
                    "detail": "Error sending reset code. Please try again or use a different method."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "detail": "If your email exists in our system, you will receive a reset code."
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    """
    Confirm password reset code and set new password
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.info(
                f"Password reset confirmation attempt for non-existent email: {email}"
            )
            return Response(
                {"detail": "Invalid or expired reset code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the most recent valid reset code for this user
        try:
            reset_code = PasswordResetCode.objects.filter(
                user=user, is_used=False, expires_at__gt=timezone.now()
            ).latest("created_at")
        except PasswordResetCode.DoesNotExist:
            logger.info(
                f"Password reset confirmation attempt with no valid codes for user: {user.email}"
            )
            return Response(
                {"detail": "Invalid or expired reset code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if maximum attempts exceeded
        if reset_code.attempts >= 3:
            logger.info(
                f"Password reset confirmation max attempts exceeded for user: {user.email}"
            )
            return Response(
                {
                    "detail": "Too many failed attempts. Please request a new reset code."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if code matches
        if reset_code.code != code:
            reset_code.attempts += 1
            reset_code.save()
            logger.info(
                f"Password reset confirmation with invalid code for user: {user.email}, attempt {reset_code.attempts}"
            )
            return Response(
                {"detail": "Invalid reset code."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Mark the code as used
        reset_code.is_used = True
        reset_code.save()

        # Set the new password
        user.set_password(new_password)
        user.save()

        logger.info(f"Password reset successful for user: {user.email}")
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
