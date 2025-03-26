from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class ChatRoomView(LoginRequiredMixin, TemplateView):
    template_name = "chat/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the channel ID via URL parameters, query string, or hardcode here for testing.
        # For a more robust implementation, retrieve the channel based on URL kwargs or user context.
        context['room_name'] = self.request.GET.get('channel', 1)

        # Pass the username for display purposes
        context['username'] = self.request.user.username
        return context
