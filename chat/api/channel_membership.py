from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChannelMembership
from chat.serializers import ChannelMembershipSerializer


class ChannelMembershipListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        memberships = ChannelMembership.objects.all()
        serializer = ChannelMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ChannelMembershipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Expect request.data to contain valid channel and user info
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChannelMembershipDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(ChannelMembership, pk=pk)

    def get(self, request, pk):
        membership = self.get_object(pk)
        serializer = ChannelMembershipSerializer(membership)
        return Response(serializer.data)

    def put(self, request, pk):
        membership = self.get_object(pk)
        serializer = ChannelMembershipSerializer(membership, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        membership = self.get_object(pk)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
