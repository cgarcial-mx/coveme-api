from django.db import models
from core.models import TimestampedModel

class ApiLog(TimestampedModel):
    """Logs de todas las llamadas a APIs externas"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='api_logs')
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=200, null=True, blank=True)
    method = models.CharField(max_length=10, null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.IntegerField(null=True, blank=True)  # en milisegundos
    quota_used = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client.name} - {self.endpoint} - {self.status_code}"
