from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register('menu_items', views.MenuItemView, basename='menu_items')
router.register('groups/manager/users', views.GroupsManagerView, basename='manager')
router.register('groups/delivery_crew/users', views.GroupsDeliveryCrewView, basename='delivery_crew')
router.register('orders', views.OrdersView, basename='orders')

urlpatterns =[
    path('cart/menu-items', views.CustomerCartView.as_view({
        'get':'list',
        'post':'create',
        'delete':'destroy',
    }))
] + router.urls