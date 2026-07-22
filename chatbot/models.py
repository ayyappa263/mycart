from django.db import models
from shop.models import Product

class ChatMessage(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    message = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Product, related_name='chatmessages', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recommended_product = models.JSONField(default=list, blank=True)
    user_image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    rag_context = models.JSONField(default=dict, blank=True)
    product_ids = models.JSONField(default=list, blank=True)
    class Role(models.TextChoices):
        SYSTEM = 'system', 'System'
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'AI Assistant'

    role = models.CharField(max_length=15,choices=Role.choices,default=Role.USER)

    def __str__(self):
        return f"Session {self.session_id} - {self.role}"