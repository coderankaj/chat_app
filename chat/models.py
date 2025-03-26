import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Team(models.Model):
    """
    Represents a team in the collaboration platform.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_teams',
        related_query_name='team_creator'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'

    def deactivate(self):
        """Soft delete the team."""
        self.is_active = False
        self.save()


class Channel(models.Model):
    """
    Channels are where team members communicate.
    For direct messages, a channel is created with is_direct=True.
    """
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='channels',
        related_query_name='channel',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    is_private = models.BooleanField(default=False)
    is_direct = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_channels',
        related_query_name='channel_creator'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # Many-to-many relationship using a through model for additional metadata.
    users = models.ManyToManyField(
        User,
        through='ChannelMembership',
        related_name='channels',
        related_query_name='channel'
    )

    def __str__(self):
        return f"{self.team.name if self.team else 'Direct'} - {self.name}"

    class Meta:
        unique_together = (('team', 'name'),)
        ordering = ['created_at']
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'


class ChannelMembership(models.Model):
    """
    Through model to track channel memberships with extra fields.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='channel_memberships',
        related_query_name='membership'
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='memberships',
        related_query_name='membership'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=now)
    is_typing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} in {self.channel}"

    class Meta:
        unique_together = ('user', 'channel')
        ordering = ['joined_at']
        verbose_name = 'Channel Membership'
        verbose_name_plural = 'Channel Memberships'

    def update_last_seen(self):
        self.last_seen = now()
        self.save()


class Message(models.Model):
    """
    Stores chat messages for both channels and direct messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='messages',
        related_query_name='message'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        related_query_name='message_sender'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    class Meta:
        indexes = [models.Index(fields=['timestamp'])]
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def edit(self, new_content):
        """Edit the message content and record the edit timestamp."""
        self.content = new_content
        self.edited_at = now()
        self.save()

    def soft_delete(self):
        """Soft delete the message."""
        self.is_deleted = True
        self.save()
