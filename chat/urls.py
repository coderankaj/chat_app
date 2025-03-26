from django.urls import path

from .api import (
    TeamListAPIView, TeamDetailAPIView,
    ChannelListAPIView, ChannelDetailAPIView,
    ChannelMembershipListAPIView, ChannelMembershipDetailAPIView,
    MessageListAPIView, MessageDetailAPIView,
)

urlpatterns = [
    path('teams/', TeamListAPIView.as_view(), name='team-list'),
    path('teams/<int:pk>/', TeamDetailAPIView.as_view(), name='team-detail'),

    path('channels/', ChannelListAPIView.as_view(), name='channel-list'),
    path('channels/<int:pk>/', ChannelDetailAPIView.as_view(), name='channel-detail'),

    path('memberships/', ChannelMembershipListAPIView.as_view(), name='membership-list'),
    path('memberships/<int:pk>/', ChannelMembershipDetailAPIView.as_view(), name='membership-detail'),

    path('messages/', MessageListAPIView.as_view(), name='message-list'),
    path('messages/<uuid:pk>/', MessageDetailAPIView.as_view(), name='message-detail'),
]
