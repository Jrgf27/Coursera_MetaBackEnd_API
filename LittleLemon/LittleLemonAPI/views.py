from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Category, MenuItem, Cart
from .serializer import MenuItemSerializer, UserSerializer, CartSerializer
from .permissions import *

# Create your views here.

class MenuItemView(viewsets.ViewSet):

    def get_permissions(self):
        if(self.request.method=='GET'): 
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(),IsManager()]

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
    
class GroupsManagerView(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated(),IsManager()]

    def list(self,request):
        userManagers = User.objects.filter(groups__name = 'Manager')
        serialized_userManagers = UserSerializer(userManagers, many=True)
        return Response(serialized_userManagers.data, status.HTTP_200_OK)
    
    def create(self, request):
        serialized_userManager = UserSerializer(data=request.data)
        serialized_userManager.is_valid(raise_exception=True)
        user = get_object_or_404(User, id=request.data['id'])
        group_manager=get_object_or_404(Group, name='Manager')
        group_manager.user_set.add(user)
        return Response({"message":"Added user to Manager group"}, status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        group_manager=get_object_or_404(Group, name='Manager')
        group_manager.user_set.remove(user)
        return Response({"message":"Removed user from Manager group"}, status.HTTP_200_OK)
    
class GroupsDeliveryCrewView(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated(),IsManager()]

    def list(self,request):
        user = User.objects.filter(groups__name = 'Delivery Crew')
        serialized_user = UserSerializer(user, many=True)
        return Response(serialized_user.data, status.HTTP_200_OK)
    
    def create(self, request):
        serialized_user = UserSerializer(data=request.data)
        serialized_user.is_valid(raise_exception=True)
        user = get_object_or_404(User, id=request.data['id'])
        group_deliveryCrew=get_object_or_404(Group, name='Delivery Crew')
        group_deliveryCrew.user_set.add(user)
        return Response({"message":"Added user to Delivery Crew group"}, status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        group_deliveryCrew=get_object_or_404(Group, name='Delivery Crew')
        group_deliveryCrew.user_set.remove(user)
        return Response({"message":"Removed user from Delivery Crew group"}, status.HTTP_200_OK)
    
class CustomerCartView(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated(),IsCustomer()]

    def list(self,request):
        cart = Cart.objects.filter(user = request.user)
        serialized_cart = CartSerializer(cart, many=True)
        return Response(serialized_cart.data, status.HTTP_200_OK)
    
    def create(self, request):
        serialized_cart = CartSerializer(data=request.data, context={'request': request})
        serialized_cart.is_valid(raise_exception=True)
        menuitem = get_object_or_404(MenuItem, pk=serialized_cart.validated_data['menuitem_id'])
        serialized_cart.save(
            user = request.user,
            menuitem = menuitem,
            unit_price = menuitem.price,
            price = menuitem.price * serialized_cart.validated_data['quantity']
        )
        return Response(serialized_cart.data, status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        Cart.objects.filter(user=request.user).delete()
        return Response({"message":"Deleted all carts for user"}, status.HTTP_200_OK)