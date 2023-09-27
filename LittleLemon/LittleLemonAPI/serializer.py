from rest_framework import serializers
from .models import Category, MenuItem, Cart
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['slug','title']

class MenuItemSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['title','price','featured','category','category_id']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields = ['id','name']

class UserSerializer(serializers.ModelSerializer):

    username=serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields=['id','username']

class CartSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    unit_price = serializers.DecimalField(read_only=True, max_digits=6, decimal_places=2)
    price = serializers.DecimalField(read_only=True, max_digits=6, decimal_places=2)
    
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Cart
        fields = ['user', 'menuitem','menuitem_id', 'quantity', 'unit_price', 'price']