from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('config_api.urls')),
    path('device/generate3d', views.generate_3d_model, name='generate_3d_model'),
    path('device-types', views.device_types, name='device_types'),
    path('devices', views.devices_list, name='devices_list'),
    path('devices/<int:device_id>/model', views.device_model, name='device_model'),
] 