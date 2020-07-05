from rest_framework import viewsets, generics

from .models import (
    Batch,
    ResearchField,
    Document,
    Group,
    Mark,
    Message,
    MessageChannel,
)
from .serializers import (
    BatchSerializer,
    DocumentSerializer,
    GroupSerializer,
    MarkSerializer,
    MessageChannelSerializer,
    MessageSerializer,
    ResearchFieldSerializer,
)


class BatchViewset(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    queryset = Batch.objects.all()


class ResearchFieldViewset(viewsets.ModelViewSet):
    serializer_class = ResearchFieldSerializer
    queryset = ResearchField.objects.all()


class DocumentViewset(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()


class GroupViewset(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class MessageAPI(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all().order_by('-created_at')

    def get_queryset(self):
        message_channel_id = self.kwargs.get('message_channel')
        return Message.objects.filter(message_channel_id=message_channel_id)


class MessageChannelViewset(viewsets.ModelViewSet):
    serializer_class = MessageChannelSerializer
    queryset = MessageChannel.objects.all().order_by('id')


class MarkViewset(viewsets.ModelViewSet):
    serializer_class = MarkSerializer
    queryset = Mark.objects.all().order_by(
        'student__user__username',
        'graded_by__user__username',
    )
