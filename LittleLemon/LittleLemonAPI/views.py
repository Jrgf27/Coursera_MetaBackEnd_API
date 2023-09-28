from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage
import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializer import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import *

# Create your views here.

class MenuItemView(viewsets.ViewSet):

    def get_permissions(self):
        if(self.request.method=='GET'): 
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(),IsManager()]

    def list(self,request):
        menuItemList= MenuItem.objects.select_related('category').all().order_by('category')
        category_name = request.query_params.get('category')
        featured = request.query_params.get('featured')
        to_price=request.query_params.get('to_price')
        search = request.query_params.get('search')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        if category_name:
            menuItemList = menuItemList.filter(category__title = category_name)
        if to_price:
            menuItemList = menuItemList.filter(price__lte=to_price)
        if featured:
            menuItemList = menuItemList.filter(featured=featured)
        if search:
            menuItemList = menuItemList.filter(title__icontains = search)

        paginator = Paginator(menuItemList, per_page=perpage)

        try:
            menuItemList = paginator.page(number=page)
        except EmptyPage:
            menuItemList = []

        serialized_menuItemList = MenuItemSerializer(menuItemList, many=True)
        return Response(serialized_menuItemList.data, status.HTTP_200_OK)
    
    def create(self, request):       
        serialized_menuItem = MenuItemSerializer(data=request.data)
        serialized_menuItem.is_valid(raise_exception=True)
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

        menuitem = request.query_params.get('menuitem')
        to_price = request.query_params.get('price')
        search = request.query_params.get('search')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        if menuitem:
            cart = cart.filter(menuitem = menuitem)
        if to_price:
            cart = cart.filter(price__lte=to_price)

        if search:
            cart = cart.filter(user__username__icontains = search)
        paginator = Paginator(cart, per_page=perpage)
        try:
            cart = paginator.page(number=page)
        except EmptyPage:
            cart = []


        serialized_cart = CartSerializer(cart, many=True)
        return Response(serialized_cart.data, status.HTTP_200_OK)

    def create(self, request):
        serialized_cart = CartSerializer(data=request.data, context={'request': request})
        serialized_cart.is_valid(raise_exception=True)
        menuitem = get_object_or_404(MenuItem, pk=serialized_cart.validated_data['menuitem_id'])
        serialized_cart.save(
            user = request.user,
            unit_price = menuitem.price,
            price = menuitem.price * serialized_cart.validated_data['quantity']
        )
        
        return Response(serialized_cart.data, status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        Cart.objects.filter(user=request.user).delete()
        return Response({"message":"Deleted all carts for user"}, status.HTTP_200_OK)
    
class OrdersView(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated()]

    def list(self,request):
        if IsCustomer():
            orders= Order.objects.filter(user=request.user).order_by('date')
        elif IsManager():
            orders= Order.objects.all().order_by('date')
        elif IsDeliveryCrew():
            orders= Order.objects.filter(deliver_crew = request.user).order_by('date')

        to_date = request.query_params.get('date')
        status=request.query_params.get('status')
        delivery_crew= request.query_params.get('delivery_crew')
        search = request.query_params.get('search')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        if to_date:
            orders = orders.filter(date__lte = to_date)
        if status:
            orders = orders.filter(status=status)
        if delivery_crew:
            orders = orders.filter(delivery_crew=delivery_crew)
        if search:
            orders = orders.filter(user__username__icontains = search)
        paginator = Paginator(orders, per_page=perpage)
        try:
            orders = paginator.page(number=page)
        except EmptyPage:
            orders = []

        serialized_order = OrderSerializer(orders, many=True)
        return Response(serialized_order.data, status.HTTP_200_OK)
    
    def create(self, request):
        if not (request.user.groups.filter(name='Manager').exists() or\
                request.user.groups.filter(name='Delivery Crew').exists()):

            serialized_menuItem = OrderItemSerializer(data=request.data)
            serialized_menuItem.is_valid(raise_exception=True)
            cart = Cart.objects.filter(user=request.user)
            newOrder = Order(
                user = request.user,
                total = 0,
                date = datetime.date.today()
            )
            newOrder.save()
            for item in cart:
                orderitem = OrderItem(
                    order = newOrder,
                    menuitem = item.menuitem,
                    quantity = item.quantity,
                    unit_price = item.unit_price,
                    price = item.price
                )
                orderitem.save()
                newOrder.total += item.price

            newOrder.save()
            cart.delete()
            orderItemsAll = OrderItem.objects.filter(order=newOrder)
            serialized_order = OrderSerializer(newOrder, many=False)
            serialized_orderItem = OrderItemSerializer(orderItemsAll, many=True)
            return Response({'order_data':serialized_order.data,'order_item_data':serialized_orderItem.data}, status.HTTP_201_CREATED)
        
        else:
            return Response({'message':'Unauthorized User'},status.HTTP_401_UNAUTHORIZED)
    
    def update(self, request, pk=None):      
        if request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order, pk=pk)
            serialized_order = OrderSerializer(order, data=request.data)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save(
                status = serialized_order.validated_data['status']
            )
            return Response(serialized_order.data, status.HTTP_200_OK)
        
        else:
            return Response({'message':'Unauthorized User'},status.HTTP_401_UNAUTHORIZED)
    
    def retrieve(self, request, pk=None):
        if not (request.user.groups.filter(name='Manager').exists() or\
                request.user.groups.filter(name='Delivery Crew').exists()):
            
            order = get_object_or_404(Order, pk=pk)
            if order.user != request.user:
                return Response({'message':'Unauthorized User'},status.HTTP_401_UNAUTHORIZED)
            
            serialized_order= OrderSerializer(order)
            return Response(serialized_order.data, status.HTTP_200_OK)
        
        else:
            return Response({'message':'Unauthorized User'},status.HTTP_401_UNAUTHORIZED)
    
    def partial_update(self, request, pk=None):
        if request.user.groups.filter(name='Delivery Crew').exists():
            order = get_object_or_404(Order, pk=pk)
            if order.delivery_crew != request.user:
                return Response({'message':'Unauthorized User'},status.HTTP_401_UNAUTHORIZED)
            serialized_order = OrderSerializer(order, data=request.data)
            serialized_order.is_valid(raise_exception=True)
            order.status = serialized_order.validated_data['status']
            order.save()
            return Response(serialized_order.data, status.HTTP_200_OK)
        
        elif request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order, pk=pk)
            serialized_order = OrderSerializer(order, data=request.data)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status.HTTP_200_OK)
        
        else:
            return Response({'message':'Unauthorized User'},status.HTTP_401_UNAUTHORIZED)
    
    def destroy(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order, pk=pk)
            order.delete()
            return Response({"message":"Deleting order"}, status.HTTP_200_OK)
        
        else:
            return Response({'message':'Unauthorized User'},status.HTTP_401_UNAUTHORIZED)