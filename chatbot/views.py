from django.shortcuts import render
from chatbot.models import ChatMessage
from shop.models import Product
from rest_framework.decorators import api_view, parser_classes
from rest_framework import generics
from .serializers import ChatMessageSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from chatbot.ml_models.rag.ragchatbot import State, graph
import uuid
from rest_framework.filters import SearchFilter
import django_filters
import base64
from io import BytesIO
from PIL import Image
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json

@api_view(['GET','POST'])
@parser_classes([MultiPartParser, FormParser])
def sendmessage(request):
    if not request.session.session_key:
        request.session.create()
        request.session['initiated'] = True
        request.session.modified = True
    session_id = request.session.session_key
    message = request.data.get('message')
    role = request.data.get('role')
    user_uploaded_image = request.FILES.get('user_image')
    if user_uploaded_image:
        store_chat = ChatMessage.objects.create(session_id=session_id, message=message, role=role, user_image=user_uploaded_image)
    else:
        store_chat = ChatMessage.objects.create(session_id=session_id, message=message, role=role)
    serializer = ChatMessageSerializer(store_chat)
    return Response(serializer.data)

@api_view(['GET','POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def ragchat(request):
    session_id = request.session.session_key
    if request.method == 'GET':
        return Response({
            'message': 'Send a POST request with a "message" field to get RAG response.',
            'status': 'idle'
        })
    message = request.data.get('message') or ''
    user_uploaded_image = request.FILES.get('user_image')
    photo_bytes = user_uploaded_image.read() if user_uploaded_image else None

    input_data = {
        'query':message,
        'photo':photo_bytes,
        'user_id': session_id
    }
    config = {"configurable": {"thread_id": session_id}}
    result = graph.invoke(input_data, config=config)
    
    serialised_context = json.dumps(result, default=str)
    product_id = result.get('product_ids', [])
    ai_answer = result.get('answer', 'No answer provided.')
    store_assistant_chat = ChatMessage.objects.create(session_id=session_id, message=ai_answer, role='assistant', rag_context=serialised_context, product_ids=product_id)
    serializer = ChatMessageSerializer(store_assistant_chat)
    return Response(serializer.data)

class ChatFilter(django_filters.FilterSet):
    class Meta:
        model = ChatMessage
        fields = ['session_id','role']

class ShowMessageView(generics.ListAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ChatFilter
    search_fields = ['message']

@api_view(['GET'])
def chathistory(request):
    if not request.session.session_key:
        request.session.create()
        request.session['initiated'] = True

    session_id = request.session.session_key

    print(session_id)
    chats = ChatMessage.objects.filter(session_id=session_id).order_by('id')
    serializer = ChatMessageSerializer(chats, many=True)
    return Response(serializer.data)
