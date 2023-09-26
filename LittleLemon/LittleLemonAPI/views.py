from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Category, MenuItem
from .serializer import MenuItemSerializer

# Create your views here.

class MenuItemView(viewsets.ViewSet):
	
    def list(self,request):
        menuItemList= MenuItem.objects.all()
        serialized_menuItemList = MenuItemSerializer(menuItemList, many=True)
        return Response(serialized_menuItemList.data, status.HTTP_200_OK)
    
    def create(self, request):
        serialized_menuItem = MenuItemSerializer(data=request.data)
        serialized_menuItem.is_valid(raise_exception=True)
        if not Category.objects.filter(pk=serialized_menuItem.validated_data['category_id']).exists():
            return Response({"message":"Category_Id invalid"}, status.HTTP_400_BAD_REQUEST)
        
        serialized_menuItem.save()
        return Response(serialized_menuItem.data, status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        
        menuItem = get_object_or_404(MenuItem, pk=pk)
        serialized_menuItem = MenuItemSerializer(menuItem,data=request.data)
        serialized_menuItem.is_valid(raise_exception=True)
        serialized_menuItem.save()
        return Response(serialized_menuItem.data, status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        menuItem = get_object_or_404(MenuItem, pk=pk)
        serialized_menuItem= MenuItemSerializer(menuItem)
        return Response(serialized_menuItem.data, status.HTTP_200_OK)
    
    def partial_update(self, request, pk=None):
        menuItem = get_object_or_404(MenuItem, pk=pk)
        serialized_menuItem = MenuItemSerializer(menuItem,data=request.data)
        serialized_menuItem.is_valid(raise_exception=True)
        serialized_menuItem.save()
        return Response(serialized_menuItem.data, status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        menuItem = get_object_or_404(MenuItem, pk=pk)
        menuItem.delete()
        return Response({"message":"Deleting menu item"}, status.HTTP_200_OK)