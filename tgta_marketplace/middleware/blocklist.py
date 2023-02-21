from django.conf import settings
from django import http
from products.models import Blocklist
from products.views import get_user_ip

    
class BlockedIpMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
        
    def process_view(self, request, gax, dsa, dac):
        print(get_user_ip(request))
        if Blocklist.objects.filter(ip=get_user_ip(request)).exists():
            return http.HttpResponseForbidden('{"detail": "Authentication credentials were not provided."}')
        return None