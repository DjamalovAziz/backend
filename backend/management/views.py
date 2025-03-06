# backend\management\views.py:

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password, make_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly

#
from management.permissions import IsOwnerOrReadOnly
from .models import Relation, User
from .serializers import RelationSerializer, UserSerializer, ChangePasswordSerializer


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


# views.py
from rest_framework_simplejwt.views import TokenRefreshView


# Встроенный класс уже достаточно безопасен, но мы можем переопределить при необходимости
class CustomTokenRefreshView(TokenRefreshView):
    """
    Обновление токена. Использует встроенный функционал SimpleJWT.
    """

    pass


from .serializers import LogoutSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


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


# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import SignupSerializer


class SignupView(APIView):
    @swagger_auto_schema(request_body=SignupSerializer)
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            # Создаем пользователя
            user = serializer.save()

            # Генерация токенов для нового пользователя
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SigninSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema


class SigninView(APIView):
    @swagger_auto_schema(request_body=SigninSerializer)
    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            # Аутентификация пользователя
            user = authenticate(email=email, password=password)
            if user is None:
                return Response(
                    {"error": "Неверный email или пароль."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Генерация токенов только в случае успешной аутентификации
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset
        return queryset.filter(pk=self.request.user.pk)

    def get_object(self):
        if self.request.method == "POST":
            return self.request.user
        return super().get_object()


# ~~~~~~~~~~~~~~~~~~~~ Relation ~~~~~~~~~~~~~~~~~~~~


class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
