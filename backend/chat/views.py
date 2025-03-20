# backend\chat\views.py:

from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import PersonalChat, GroupChat, Message
from .serializers import (
    PersonalChatSerializer,
    GroupChatSerializer,
    MessageSerializer,
    CreatePersonalChatSerializer,
    CreateGroupChatSerializer,
)


class PersonalChatViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PersonalChat.objects.filter(participants=self.request.user).order_by(
            "-updated_at"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CreatePersonalChatSerializer
        return PersonalChatSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        chat = serializer.save()
        return Response(
            PersonalChatSerializer(chat).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        chat = self.get_object()
        messages = Message.objects.filter(personal_chat=chat).order_by("created_at")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_message(self, request, pk=None):
        chat = self.get_object()

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(sender=request.user, personal_chat=chat)
            return Response(
                MessageSerializer(message).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupChatViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroupChat.objects.filter(participants=self.request.user).order_by(
            "-updated_at"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CreateGroupChatSerializer
        return GroupChatSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        chat = serializer.save()
        return Response(GroupChatSerializer(chat).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        chat = self.get_object()
        messages = Message.objects.filter(group_chat=chat).order_by("created_at")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_message(self, request, pk=None):
        chat = self.get_object()

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(sender=request.user, group_chat=chat)
            return Response(
                MessageSerializer(message).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def add_participant(self, request, pk=None):
        chat = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from user.models import User

            user = User.objects.get(uuid=user_id)

            if user in chat.participants.all():
                return Response(
                    {"error": "User is already a participant"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            chat.participants.add(user)
            return Response({"success": f"User {user.username} added to the chat"})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["delete"])
    def remove_participant(self, request, pk=None):
        chat = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from user.models import User

            user = User.objects.get(uuid=user_id)

            if chat.created_by == user:
                return Response(
                    {"error": "Cannot remove the chat creator"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if user not in chat.participants.all():
                return Response(
                    {"error": "User is not a participant"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            chat.participants.remove(user)
            return Response({"success": f"User {user.username} removed from the chat"})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
