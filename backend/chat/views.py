# backend\chat\views.py:

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Channel, Group, Message
from .serializers import ChannelSerializer, GroupSerializer, MessageSerializer

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Получить каналы, доступные пользователю через его группы"""
        user = self.request.user
        return Channel.objects.filter(groups__members=user).distinct()
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Получить сообщения конкретного канала"""
        channel = self.get_object()
        messages = channel.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Получить группы, в которых состоит пользователь"""
        user = self.request.user
        return Group.objects.filter(members=user)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Добавить пользователя в группу"""
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        from user.models import User
        try:
            user = User.objects.get(uuid=user_id)
            group.members.add(user)
            return Response({"status": "User added to group"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Получить сообщения из каналов, доступных пользователю"""
        user = self.request.user
        return Message.objects.filter(channel__groups__members=user).distinct()
    
    def perform_create(self, serializer):
        """Создать новое сообщение с автоматическим указанием отправителя"""
        serializer.save(sender=self.request.user)