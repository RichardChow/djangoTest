import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

logger = logging.getLogger(__name__)

@csrf_exempt
def generate_3d_model(request):
    logger.info(f'收到请求: {request.method} {request.path}')
    logger.info(f'请求头: {request.headers}')
    
    if request.method != 'POST':
        logger.warning('非POST请求被拒绝')
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
    logger.info('收到3D模型生成请求')
    try:
        logger.info(f'FILES: {request.FILES}')
        logger.info(f'POST: {request.POST}')
        # 获取上传的图片
        images = request.FILES.getlist('image')
        device_type = request.POST.get('device_type')
        
        logger.info(f'处理设备类型: {device_type}, 图片数量: {len(images)}')
        
        # 这里添加您的3D模型生成逻辑
        # 示例返回数据
        model_data = {
            'width': 1,
            'height': 2,
            'depth': 0.5,
            'features': [
                {
                    'type': 'port',
                    'position': {'x': 0.1, 'y': 0.1, 'z': 0},
                    'size': 0.05
                },
                {
                    'type': 'led',
                    'position': {'x': -0.1, 'y': 0.1, 'z': 0},
                    'color': 0x00ff00
                }
            ]
        }
        
        logger.info('3D模型生成成功')
        return JsonResponse({
            'success': True, 
            'model': model_data
        })
    except Exception as e:
        logger.error(f'3D模型生成失败: {str(e)}')
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)

@csrf_exempt
def device_types(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f'创建设备类型: {data}')
            # 这里添加创建设备类型的逻辑
            return JsonResponse({'success': True, 'id': 1})
        except Exception as e:
            logger.error(f'创建设备类型失败: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

def devices_list(request):
    if request.method == 'GET':
        # 示例数据
        devices = [
            {
                'id': 1,
                'name': 'Device 1',
                'device_type': 'NPT1800'
            }
        ]
        return JsonResponse({'data': devices})
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

def device_model(request, device_id):
    if request.method == 'GET':
        try:
            # 这里添加获取设备3D模型的逻辑
            model_data = {
                'width': 1,
                'height': 2,
                'depth': 0.5
            }
            return JsonResponse({'model_data': model_data})
        except Exception as e:
            logger.error(f'获取设备模型失败: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405) 