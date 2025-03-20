# backend\chat\serializers.py:

from rest_framework import serializers

#
from .models import PersonalChat, GroupChat, Message
from user.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ("uuid", "sender", "content", "created_at", "is_read")
        read_only_fields = ("uuid", "sender", "created_at")


class PersonalChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = PersonalChat
        fields = ("uuid", "participants", "created_at", "updated_at", "last_message")
        read_only_fields = ("uuid", "created_at", "updated_at")

    def get_last_message(self, obj):
        last_message = obj.messages.order_by("-created_at").first()
        if last_message:
            return MessageSerializer(last_message).data
        return None


class GroupChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = GroupChat
        fields = (
            "uuid",
            "name",
            "description",
            "participants",
            "created_by",
            "created_at",
            "updated_at",
            "last_message",
        )
        read_only_fields = ("uuid", "created_by", "created_at", "updated_at")

    def get_last_message(self, obj):
        last_message = obj.messages.order_by("-created_at").first()
        if last_message:
            return MessageSerializer(last_message).data
        return None


class CreatePersonalChatSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    class Meta:
        model = PersonalChat
        fields = ("uuid", "participant_ids")
        read_only_fields = ("uuid",)

    def create(self, validated_data):
        participant_ids = validated_data.pop("participant_ids")
        chat = PersonalChat.objects.create()

        # Добавляем создателя чата и указанных участников
        from user.models import User

        chat.participants.add(self.context["request"].user)

        for user_id in participant_ids:
            try:
                user = User.objects.get(uuid=user_id)
                chat.participants.add(user)
            except User.DoesNotExist:
                pass

        return chat


class CreateGroupChatSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    class Meta:
        model = GroupChat
        fields = ("uuid", "name", "description", "participant_ids")
        read_only_fields = ("uuid",)

    def create(self, validated_data):
        participant_ids = validated_data.pop("participant_ids")

        chat = GroupChat.objects.create(
            name=validated_data["name"],
            description=validated_data.get("description", ""),
            created_by=self.context["request"].user,
        )

        from user.models import User

        chat.participants.add(self.context["request"].user)

        for user_id in participant_ids:
            try:
                user = User.objects.get(uuid=user_id)
                chat.participants.add(user)
            except User.DoesNotExist:
                pass

        return chat
