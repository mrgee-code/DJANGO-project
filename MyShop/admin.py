from django.contrib import admin
from django.contrib import admin 
from .models import Category, Product, Order, OrderItem, ContactMessage, Profile

#Register your models here.
admin.site.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_low_stock']
    list_filter = ['category']
    search_fields = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


admin.site.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'total']
    inlines = [OrderItemInline]

admin.site.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'message_type', 'email', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['name', 'email', 'message']

admin.site.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'picture']