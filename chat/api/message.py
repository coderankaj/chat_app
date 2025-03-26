from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Message, Channel
from chat.serializers import MessageSerializer


class MessageListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        messages = Message.objects.all().order_by('-timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Expect the channel id in request.data as "channel"
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            channel_id = request.data.get('channel')
            # If a channel is provided, ensure it exists
            if channel_id:
                channel = get_object_or_404(Channel, pk=channel_id)
                serializer.save(sender=request.user, channel=channel)
            else:
                serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Message, pk=pk)

    def get(self, request, pk):
        message = self.get_object(pk)
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    def put(self, request, pk):
        message = self.get_object(pk)
        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Update message; consider checking sender permissions
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        message = self.get_object(pk)
        message.soft_delete()  # Soft delete instead of full removal
        return Response(status=status.HTTP_204_NO_CONTENT)
