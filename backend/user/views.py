# backend\user\views.py:

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    ChangePasswordSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "signup":
            return UserCreateSerializer
        elif self.action == "update_profile":
            return UserUpdateSerializer
        elif self.action == "change_password":
            return ChangePasswordSerializer
        return UserSerializer
    
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def delete_me(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Account successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def signup(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        response_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def get_users(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def get_user(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], permission_classes=[IsAuthenticated])
    def patch_me(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": ["Uncorrect password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Password successfully changed.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )

    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def remove_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
            return Response({"message": "Avatar successfully deleted."})
        return Response(
            {"message": "Нет аватара для удаления."}, status=status.HTTP_400_BAD_REQUEST
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
