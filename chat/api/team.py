from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Team
from chat.serializers import TeamSerializer


class TeamListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Team, pk=pk)

    def get(self, request, pk):
        team = self.get_object(pk)
        serializer = TeamSerializer(team)
        return Response(serializer.data)

    def put(self, request, pk):
        team = self.get_object(pk)
        serializer = TeamSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        team = self.get_object(pk)
        team.deactivate()  # Soft delete
        return Response(status=status.HTTP_204_NO_CONTENT)
