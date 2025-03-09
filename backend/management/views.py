# backend\management\views.py:

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password, make_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError

#
from management.permissions import IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
from .models import Relation, User
from .serializers import (
    RelationSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    LogoutSerializer,
    SignupSerializer,
    SigninSerializer,
)


# ~~~~~~~~~~~~~~~~~~~~ User ~~~~~~~~~~~~~~~~~~~~


class ChangePasswordView(APIView):
    """
    Эндпоинт для изменения пароля пользователя.
    """

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def put(self, request, *args, **kwargs):
        user_uuid = kwargs.get("pk")  # Получаем UUID пользователя из URL
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data.get("old_password")
        new_password = serializer.validated_data.get("new_password")

        try:
            user = User.objects.get(uuid=user_uuid)  # Использование uuid
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND
            )

        if not check_password(old_password, user.password):
            return Response(
                {"error": "Старый пароль указан неверно."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.password = make_password(new_password)
        user.save()

        return Response(
            {"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK
        )


class CustomTokenRefreshView(TokenRefreshView):
    """
    Обновление токена. Использует встроенный функционал SimpleJWT.
    """

    pass


class LogoutView(APIView):
    @swagger_auto_schema(request_body=LogoutSerializer)
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh"]
            try:
                # Добавляем токен в черный список
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Вы успешно вышли из системы."},
                    status=status.HTTP_200_OK,
                )
            except TokenError:
                return Response(
                    {"error": "Токен недействителен или уже отозван."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupView(APIView):
    @swagger_auto_schema(request_body=SignupSerializer)
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SigninView(APIView):
    @swagger_auto_schema(request_body=SigninSerializer)
    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = authenticate(email=email, password=password)
            if user is None:
                return Response(
                    {"error": "Неверный email или пароль."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_permissions(self):
        """
        Переопределяем разрешения в зависимости от метода:
        - GET-запросы доступны всем
        - Для опасных операций (PUT, PATCH, DELETE) нужны особые разрешения
        """
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Для неаутентифицированных пользователей возвращаем ограниченную информацию,
        для аутентифицированных - только их собственную информацию
        """
        queryset = User.objects.all()
        if self.request.user.is_authenticated:
            return queryset.filter(pk=self.request.user.pk)
        return queryset


# ~~~~~~~~~~~~~~~~~~~~ Relation ~~~~~~~~~~~~~~~~~~~~


class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated]
