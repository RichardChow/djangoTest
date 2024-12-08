from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuildViewSet, DeviceViewSet, RackViewSet, Build3DPreviewView
from django.http import JsonResponse

router = DefaultRouter()
router.register(r'build', BuildViewSet, basename='build')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'racks', RackViewSet, basename='rack')

def handler500(request):
    return JsonResponse({'error': 'Internal server error'}, status=500)

def handler404(request, exception):
    return JsonResponse({'error': 'Not found'}, status=404)

urlpatterns = [
    path('', include(router.urls)),
    path('build/', Build3DPreviewView.as_view(), name='build-3d-preview'),
]

# 添加错误处理
handler500 = handler500
handler404 = handler404
