import logging
import traceback
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer
from .models import Config
from .serializers import ConfigSerializer

logger = logging.getLogger(__name__)

class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    permission_classes = [AllowAny]  # Allow all users to access, for testing only
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        logger.info("Processing GET request for config list")
        try:
            configs = self.get_queryset()
            logger.info(f"Found {configs.count()} configs")
            if configs.exists():
                config = configs.first()
                logger.info(f"Raw config data: {config.__dict__}")
                serializer = self.get_serializer(config)
                logger.info(f"Serialized data: {serializer.data}")
                
                # 根据请求的格式返回不同的响应
                if request.accepted_renderer.format == 'html':
                    return Response(
                        {'config': serializer.data},
                        template_name='config_form.html'
                    )
                return Response(serializer.data)
            else:
                logger.info("No config found")
                return Response({})
        except Exception as e:
            logger.error(f"Error in list method: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"error": f"An error occurred while fetching the configuration: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        logger.info(f"Processing POST request, received data: {request.data}")
        try:
            configs = Config.objects.all()
            if configs.exists():
                instance = configs.first()
                serializer = self.get_serializer(instance, data=request.data, partial=True)
            else:
                serializer = self.get_serializer(data=request.data)

            if not serializer.is_valid():
                logger.error(f"Serializer validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            config = serializer.save()
            logger.info(f"Saved config: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in create method: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({"error": f"An error occurred while creating/updating the configuration: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = super().get_queryset()
        logger.info(f"Queryset count: {queryset.count()}")
        return queryset

def some_view(request):
    configs = Config.objects.all()
    for config in configs:
        logger.info(f'Configuration: {config.id}')
    # Rest of the view...
