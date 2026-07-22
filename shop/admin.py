from django.contrib import admin

# Register your models here.
from .models import master_Category, Product, Contact, Orders

# admin.site.register(Product)
# admin.site.register(Contact)
# admin.site.register(Orders)

@admin.register(master_Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','product_name', 'slug', 'price', 'created_date']
    list_filter = ['created_date']
    list_editable = ['price']
    prepopulated_fields = {'slug': ('product_name',)}
    