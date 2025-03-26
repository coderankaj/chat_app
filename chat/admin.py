from django.contrib import admin

from .models import Team, Channel, ChannelMembership, Message


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'is_active')
    search_fields = ('name', 'description', 'created_by__username')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)


class ChannelMembershipInline(admin.TabularInline):
    model = ChannelMembership
    extra = 0
    fields = ('user', 'joined_at', 'is_admin', 'last_seen', 'is_typing')
    readonly_fields = ('joined_at', 'last_seen')


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'is_private', 'is_direct', 'created_by', 'created_at')
    search_fields = ('name', 'team__name', 'created_by__username')
    list_filter = ('is_private', 'is_direct', 'created_at')
    ordering = ('-created_at',)
    inlines = [ChannelMembershipInline]


@admin.register(ChannelMembership)
class ChannelMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'channel', 'joined_at', 'is_admin', 'last_seen', 'is_typing')
    search_fields = ('user__username', 'channel__name')
    list_filter = ('is_admin', 'is_typing')
    ordering = ('-joined_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'channel', 'timestamp', 'edited_at', 'is_deleted')
    search_fields = ('sender__username', 'content', 'channel__name')
    list_filter = ('is_deleted', 'timestamp')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'edited_at')
