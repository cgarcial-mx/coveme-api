from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import CustomerFeedback
from .serializers import CustomerFeedbackSerializer

class CustomerFeedbackViewSet(viewsets.ModelViewSet):
    queryset = CustomerFeedback.objects.all()
    serializer_class = CustomerFeedbackSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'marketplace_type', 'feedback_type', 'status', 'product']
