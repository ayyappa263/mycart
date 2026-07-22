from django.contrib import admin
from .models import ChatMessage
# Register your models here.

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id','session_id', 'message', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['session_id']
