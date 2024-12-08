from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuildViewSet, DeviceViewSet, RackViewSet

router = DefaultRouter()
router.register(r'build', BuildViewSet, basename='build')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'racks', RackViewSet, basename='rack')

urlpatterns = [
    path('', include(router.urls)),
]
