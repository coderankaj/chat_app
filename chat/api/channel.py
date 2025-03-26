from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Channel
from chat.serializers import ChannelSerializer


class ChannelListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        channels = Channel.objects.all()
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ChannelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChannelDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Channel, pk=pk)

    def get(self, request, pk):
        channel = self.get_object(pk)
        serializer = ChannelSerializer(channel)
        return Response(serializer.data)

    def put(self, request, pk):
        channel = self.get_object(pk)
        serializer = ChannelSerializer(channel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        channel = self.get_object(pk)
        channel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
