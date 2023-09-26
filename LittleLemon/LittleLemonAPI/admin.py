from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Category,
                MenuItem,
                Cart,
                Order,
                OrderItem)

class Admin(admin.ModelAdmin):
    pass