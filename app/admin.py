from django.contrib import admin
from .models import Product, Category, Review, Tag, ProductImage, Color, Brand, SiteSettings, Order, OrderItem, UserProfile


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Allows you to add one extra image at a time

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    filter_horizontal = ('tags', 'colors', 'brands')  # Displays tags, colors, and brands as horizontal checkboxes


class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title',)

    # Prevent adding more than one instance in the admin panel
    def has_add_permission(self, request):
        # Limit to only one instance of SiteSettings
        return not SiteSettings.objects.exists()
    
class OrderItemTabularInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemTabularInline]

admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Tag)
admin.site.register(ProductImage)
admin.site.register(Color)
admin.site.register(Brand)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(UserProfile)
