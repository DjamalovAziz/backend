# backend\chat\admin.py:

from django.contrib import admin
from .models import Channel, Group, Message

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'is_private')
    search_fields = ('name', 'description')
    list_filter = ('is_private', 'created_at')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    filter_horizontal = ('members',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'content_preview', 'channel', 'created_at', 'is_read')
    search_fields = ('content', 'sender__username')
    list_filter = ('is_read', 'created_at')
    
    def content_preview(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    
    content_preview.short_description = 'Content'