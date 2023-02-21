from datetime import timedelta
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
import telegram
from django.db.models.signals import post_save

class Server(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Blocklist(models.Model):
    reason = models.CharField(max_length=64)
    ip = models.GenericIPAddressField()
    time_created = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return f'{self.reason} || {self.ip}'
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.ImageField(upload_to='product_photos')
    price = models.IntegerField()
    nickname = models.CharField(max_length=255)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_products_by_server_and_name_filter(server, name_filter):
        products = Product.objects.filter(server=server)
        if name_filter:
            products = products.filter(models.Q(name__icontains=name_filter) | models.Q(description__icontains=name_filter))
        return products
    
    def filter_product(self, server, name_filter):
        if self.server == server:
            if name_filter == 'skip' or None:
                return True
            if not name_filter in self.name:
                return False
            return True
        return False
    

class BotUser(models.Model):
    telegram_id = models.CharField(max_length=50, unique=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True)
    name_filter = models.CharField(max_length=100, blank=True, null=True)
    sent_products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f"{self.telegram_id}"

    def add_sent_product(self, product):
        self.sent_products.add(product)
        self.save()

    def set_selected_server(self, server):
        self.server = server
        self.save()

    def set_name_filter(self, name_filter):
        self.name_filter = name_filter
        self.save()
        
    def get_new_products_by_filter(self):
        five_hours_ago = timezone.now() - timedelta(hours=5)
        products = Product.get_products_by_server_and_name_filter(
            server=self.server,
            name_filter=self.name_filter,
        )
        new_products = products.exclude(id__in=self.sent_products.all())
        new_products = new_products.filter(created_at__gte=five_hours_ago)
        return new_products
