from django.db import models
from core.models import TimestampedModel

class CustomerFeedback(TimestampedModel):
    """Feedback de clientes de todos los marketplaces"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='customer_feedback')
    marketplace_type = models.CharField(max_length=50, choices=[
        ('amazon', 'Amazon'),
        ('mercadolibre', 'Mercado Libre'),
        ('shopify', 'Shopify'),
        ('ebay', 'eBay'),
        ('walmart', 'Walmart'),
    ])
    feedback_type = models.CharField(max_length=50, choices=[
        ('review', 'Review'),
        ('question', 'Pregunta'),
        ('comment', 'Comentario'),
    ])
    marketplace_feedback_id = models.CharField(max_length=100, null=True, blank=True)
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    marketplace_product_id = models.CharField(max_length=100, null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    feedback_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('answered', 'Respondido'),
    ])
    answer_text = models.TextField(null=True, blank=True)
    answer_date = models.DateTimeField(null=True, blank=True)
    verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.IntegerField(default=0)
    total_votes = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'customer_feedback'
    
    def __str__(self):
        return f"{self.marketplace_type} - {self.feedback_type} - {self.customer_name}"
