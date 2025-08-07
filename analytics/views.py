from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import ApiLog
from .serializers import ApiLogSerializer

class ApiLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApiLog.objects.all()
    serializer_class = ApiLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'user', 'status_code', 'method']
