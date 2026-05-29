from django.contrib import admin

from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_id",
        "product_name",
        "category",
        "quantity",
        "buy_price",
        "sell_price",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active", "volume_unit")
    search_fields = ("product_id", "product_name", "hsn_code")
    inlines = [ProductImageInline]
