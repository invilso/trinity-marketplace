from django.urls import path
from . import views
import threading


urlpatterns = [
    # path('', views.ProductListView.as_view(), name='product_list'),
    path('', views.product_list, name='product_list'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('product/block/<int:pk>/', views.block_user_and_delete_products, name='block_product'),
    path('start_bot/', views.start_bot_view, name='start_bot'),
    path('rules/', views.rules_view, name='rules'),
]





# import asyncio

# loop = asyncio.get_event_loop()
# loop.run_until_complete(b.run_bot())