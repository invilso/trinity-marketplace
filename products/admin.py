from django.contrib import admin
from .models import Product, Server, BotUser, Blocklist

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'server', 'nickname', 'ip_address')
    list_filter = ('server',)
    search_fields = ('name', 'description', 'nickname', 'ip_address')
    ordering = ('server', 'name')

admin.site.register(Product, ProductAdmin)

class ServerAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Server, ServerAdmin)

class BotUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'server', 'name_filter')
    list_filter = ('server',)
    search_fields = ('telegram_id', 'name_filter')
    ordering = ('telegram_id', 'server')

admin.site.register(BotUser, BotUserAdmin)

class BlocklistAdmin(admin.ModelAdmin):
    list_display = ('ip', 'reason', 'time_created')
    search_fields = ('ip', 'reason')
    ordering = ('reason',)

admin.site.register(Blocklist, BlocklistAdmin)