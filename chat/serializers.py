from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, Channel, ChannelMembership, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class TeamSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'created_by', 'created_at', 'is_active')


class ChannelSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Channel
        fields = ('id', 'team', 'name', 'is_private', 'is_direct', 'created_by', 'created_at')


class ChannelMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    channel = ChannelSerializer(read_only=True)

    class Meta:
        model = ChannelMembership
        fields = ('id', 'user', 'channel', 'joined_at', 'is_admin', 'last_seen', 'is_typing')


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    channel = ChannelSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'channel', 'sender', 'content', 'timestamp', 'edited_at', 'is_deleted')

