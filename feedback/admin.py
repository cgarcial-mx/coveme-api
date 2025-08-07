from django.contrib import admin
from .models import CustomerFeedback

@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ['marketplace_type', 'feedback_type', 'customer_name', 'rating', 'status', 'feedback_date']
    list_filter = ['marketplace_type', 'feedback_type', 'status', 'verified_purchase', 'client']
    search_fields = ['customer_name', 'title', 'content']
