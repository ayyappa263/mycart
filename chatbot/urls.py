from django.urls import path, include
from . import views

app_name = 'chatbot'

urlpatterns = [
    path("", views.sendmessage, name='sendmessages'),
    path("chathistory/", views.chathistory, name='chathistory'),
    path("ragchat/", views.ragchat, name='ragchat'),
]