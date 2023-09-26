from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register('menu_items', views.MenuItemView, basename='menu_items')
urlpatterns = router.urls