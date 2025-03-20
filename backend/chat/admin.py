# backend\chat\admin.py:

from django.contrib import admin

#
from .models import PersonalChat, GroupChat, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("uuid", "sender", "content", "created_at", "is_read")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PersonalChat)
class PersonalChatAdmin(admin.ModelAdmin):
    list_display = ("uuid", "created_at", "updated_at", "get_participants")
    readonly_fields = ("uuid", "created_at", "updated_at")
    filter_horizontal = ("participants",)
    inlines = [MessageInline]

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])

    get_participants.short_description = "Participants"

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "uuid",
        "created_at",
        "updated_at",
        "created_by",
        "get_participant_count",
    )
    readonly_fields = ("uuid", "created_at", "updated_at")
    filter_horizontal = ("participants",)
    inlines = [MessageInline]

    def get_participant_count(self, obj):
        return obj.participants.count()

    get_participant_count.short_description = "Participant Count"

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "sender",
        "get_chat",
        "content_preview",
        "created_at",
        "is_read",
    )
    readonly_fields = ("uuid", "sender", "personal_chat", "group_chat", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("content", "sender__username")

    def content_preview(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content

    content_preview.short_description = "Content"

    def get_chat(self, obj):
        if obj.personal_chat:
            return f"Personal: {obj.personal_chat.uuid}"
        return f"Group: {obj.group_chat.name}"

    get_chat.short_description = "Chat"
