from django.contrib.sessions.models import Session
from .models import Cart as sessioncart

def get_session_key(request):
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    return session_key

def get_or_create_cart(request):
    session_key = get_session_key(request)
    cart, created = sessioncart.objects.get_or_create(session_key=session_key)
    return cart