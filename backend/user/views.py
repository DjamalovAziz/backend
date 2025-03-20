# backend\user\views.py:

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings

#
from .models import Avatar

#
from .serializers import (
    AvatarCreateSerializer,
    AvatarSerializer,
    AvatarUpdateSerializer,
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
        elif self.action == "patch_me":
            return UserUpdateSerializer
        elif self.action == "change_password":
            return ChangePasswordSerializer
        return UserSerializer

    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def delete_me(self, request):
        user = request.user
        user.delete()
        return Response(
            {"message": "Account successfully deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )

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

    # SINGLE AVATAR SCENARIO
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def delete_my_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
            return Response({"avatar_url": "/media/avatars/default/PROFILE.jpg"})
        return Response(
            {"message": "No avatar to delete."}, status=status.HTTP_400_BAD_REQUEST
        )

    # MULTIPLE AVATAR SCENARIO
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_my_avatars(self, request):
        """Get list of user's avatars"""
        avatars = Avatar.objects.filter(user=request.user)
        serializer = AvatarSerializer(avatars, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def post_me_avatar(self, request):
        # Check if avatar limit is reached
        avatar_count = Avatar.objects.filter(user=request.user).count()
        if avatar_count >= 50:
            return Response(
                {"error": "Avatar limit reached (50 maximum)."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AvatarCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar = serializer.save(user=request.user)
        return Response(AvatarSerializer(avatar).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticated],
        url_path="avatars/(?P<avatar_id>[^/.]+)",
    )
    def update_avatar(self, request, avatar_id=None):
        try:
            avatar = Avatar.objects.get(uuid=avatar_id, user=request.user)
        except Avatar.DoesNotExist:
            return Response(
                {"error": "Avatar not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AvatarUpdateSerializer(avatar, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        avatar = serializer.save()

        return Response(AvatarSerializer(avatar).data)

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[IsAuthenticated],
        url_path="avatars/(?P<avatar_id>[^/.]+)",
    )
    def delete_avatar(self, request, avatar_id=None):
        try:
            avatar = Avatar.objects.get(uuid=avatar_id, user=request.user)
        except Avatar.DoesNotExist:
            return Response(
                {"error": "Avatar not found."}, status=status.HTTP_404_NOT_FOUND
            )

        was_primary = avatar.is_primary
        avatar.delete()

        # If the deleted avatar was primary, set the next avatar as primary
        if was_primary:
            next_avatar = (
                Avatar.objects.filter(user=request.user).order_by("-created_at").first()
            )
            if next_avatar:
                next_avatar.is_primary = True
                next_avatar.save()
                return Response(AvatarSerializer(next_avatar).data)
            else:
                # No avatars left, return default avatar
                return Response({"avatar_url": "/media/avatars/default/PROFILE.jpg"})

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["get"], permission_classes=[AllowAny], url_path="avatars"
    )
    def get_user_avatars(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            avatars = Avatar.objects.filter(user=user)
            serializer = AvatarSerializer(avatars, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    # @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    # def get_avatars(self, request):
    #     if settings.AVATAR_MULTIPLE_MODE:
    #         # Multiple Avatar сценарий
    #         avatars = Avatar.objects.filter(user=request.user)
    #         serializer = AvatarSerializer(avatars, many=True)
    #         return Response(serializer.data)
    #     else:
    #         # Single Avatar сценарий - возвращаем один аватар
    #         return Response({"avatar_url": request.user.get_avatar_url()})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
