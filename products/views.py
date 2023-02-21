from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from .models import Product, Blocklist
from django.contrib import messages
from django.views.generic import ListView
from django.db import models
from django.core.paginator import Paginator
import threading
from products.tasks import start_bot
from django.conf import settings


def get_user_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return forwarded_for.split(',')[-1].strip() if forwarded_for else request.META.get('REMOTE_ADDR')

# def product_list(request):
#     products = Product.objects.all()
#     return render(request, 'products/product_list.html', {'products': products, 'ip': request.META.get('REMOTE_ADDR')})

def product_list(request):
    products = Product.objects.all()
    

    server = request.GET.get('server', None)
    name_or_description = request.GET.get('name_or_description', '')
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)

    if server:
        products = products.filter(server__name=server)

    if name_or_description:
        products = products.filter(
            models.Q(name__icontains=name_or_description) |
            models.Q(description__icontains=name_or_description)
        )

    if min_price and max_price:
        products = products.filter(price__range=(min_price, max_price))
    elif min_price:
        products = products.filter(price__gte=min_price)
    elif max_price:
        products = products.filter(price__lte=max_price)

    products = products.order_by('price')
    
    paginator = Paginator(products, 5)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'ip': get_user_ip(request=request),
        'admin_ip': settings.ADMIN_IP,
        'filters': {
            'min_price': min_price, 
            'max_price': max_price, 
            'name_or_description': name_or_description,
            'server': server
        }
    }
    return render(request, 'products/product_list.html', context)

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        server = self.request.GET.get('server', None)
        name_or_description = self.request.GET.get('name_or_description', None)
        min_price = self.request.GET.get('min_price', None)
        max_price = self.request.GET.get('max_price', None)

        if server:
            queryset = queryset.filter(server__name=server)

        if name_or_description:
            queryset = queryset.filter(
                models.Q(name__icontains=name_or_description) |
                models.Q(description__icontains=name_or_description)
            )

        if min_price and max_price:
            queryset = queryset.filter(price__range=(min_price, max_price))
        elif min_price:
            queryset = queryset.filter(price__gte=min_price)
        elif max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset.order_by('price')

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.ip_address = get_user_ip(request=request)
            product.save()
            return redirect('products:product_list')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.ip_address == get_user_ip(request=request):
        product.delete()
        messages.success(request, 'Товар удален.')
    else:
        messages.error(request, 'Вы не можете удалить.')
    return redirect('products:product_list')

def block_user_and_delete_products(request, pk):
    if settings.ADMIN_IP != get_user_ip(request=request):
        print("Ошибка бана")
        messages.error(request, 'Вы не можете удалить.')
        return redirect('products:product_list')
    product_base = get_object_or_404(Product, pk=pk)
    products = Product.objects.filter(ip_address=product_base.ip_address)
    for product in products:
        product.delete()
    bl = Blocklist(ip=product_base.ip_address, reason='Remove content')
    bl.save()
    messages.success(request, 'Пользователь заблокирован')
    return redirect('products:product_list')


# def start_bot():
#     bot_thread = threading.Thread(target=b.run_bot)
#     bot_thread.start()
    
def start_bot_view(request):
    start_bot.apply_async()
    return HttpResponse(status=200)

def rules_view(request):
    return render(request, 'products/rules.html')