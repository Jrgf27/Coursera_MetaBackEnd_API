from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register('menu_items', views.MenuItemView, basename='menu_items')
urlpatterns =[
    path('groups/manager/users', views.GroupsManager.as_view({
        'get':'list',
        'post':'create'
    })),
    path('groups/manager/users/<int:pk>', views.GroupsManager.as_view({
        'delete':'destroy'
    })),
    path('groups/delivery_crew/users', views.GroupsDeliveryCrew.as_view({
        'get':'list',
        'post':'create'
    })),
    path('groups/delivery_crew/users/<int:pk>', views.GroupsDeliveryCrew.as_view({
        'delete':'destroy'
    })),
] + router.urls