from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    list_editable = ("price", "stock", "is_active")

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "status", "created_at")
    list_filter = ("status",)
    list_editable = ("status",)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "price", "quantity")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "status")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "pincode")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating")
    list_filter = ("rating",)
    
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject","message", "created_at")