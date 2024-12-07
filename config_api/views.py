import logging
import traceback
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer
from .models import Config, Build, BuildLog
from .serializers import ConfigSerializer, BuildSerializer, BuildLogSerializer
import sys
import os
from pathlib import Path
import uuid
import threading
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# 首先定义 logger
logger = logging.getLogger('config_api')

# 在文件顶部，logger定义后添加
logger.info("Views module loaded")

# 测试 logger
logger.info("Logger test from views.py")
logger.error("Logger error test from views.py")

# 直接写入文件测试
with open('logger_test.log', 'a') as f:
    f.write("Direct file write test\n")

# 然后导入本地升级库
try:
    sys.path.append(r'C:\NPTI_CLI\Lib')
    import ssh_cli
    logger.info("Successfully imported ssh_cli")
except Exception as e:
    logger.error(f"Failed to import ssh_cli: {str(e)}")

# 存储升级任务的状态和日志
upgrade_tasks = {}

class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    permission_classes = [AllowAny]  # Allow all users to access, for testing only
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        logger.info(f"Processing GET request for {self.basename} list")
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
        logger.info(f"Processing POST request for {self.basename}, received data: {request.data}")
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

    @action(detail=False, methods=['POST'], url_path='upgrade')
    def start_upgrade(self, request):
        try:
            task_id = str(uuid.uuid4())
            channel_layer = get_channel_layer()
            
            def send_log(message):
                logger.info(f"Sending log message: {message}")
                async_to_sync(channel_layer.group_send)(
                    f'upgrade_log_{task_id}',
                    {
                        'type': 'upgrade_log',
                        'message': message
                    }
                )

            # 获取升级参数
            upgrade_type = request.data.get('upgrade_type')
            work_type = request.data.get('work_type')
            ne_ip = request.data.get('ne_ip', [])
            version_path = request.data.get('version_path')
            
            logger.info(f"Starting upgrade with parameters: {request.data}")
            send_log(f"Starting upgrade with parameters: {request.data}")
            
            # 启动升级线程
            thread = threading.Thread(
                target=self._run_upgrade,
                args=(task_id, upgrade_type, work_type, ne_ip, version_path, send_log)
            )
            thread.start()
            
            return Response({
                'task_id': task_id,
                'message': 'Upgrade started'
            })
            
        except Exception as e:
            logger.error(f"Error starting upgrade: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _run_upgrade(self, task_id, upgrade_type, work_type, ne_ip, version_path, send_log):
        try:
            send_log("Starting upgrade process...")
            send_log(f"Upgrade type: {upgrade_type}")
            send_log(f"Work type: {work_type}")
            send_log(f"NE IP: {ne_ip}")
            send_log(f"Version path: {version_path}")
            
            # 导入本地升级脚本
            sys.path.append(r'C:\NPTI_CLI\Lib')
            import ssh_cli
            
            # 执行升级
            result = ssh_cli.upgrade(
                upgrade_type=upgrade_type,
                work_type=work_type,
                ne_ip=ne_ip,
                version_path=version_path,
                callback=send_log
            )
            
            send_log("Upgrade completed successfully" if result else "Upgrade failed")
            
        except Exception as e:
            error_msg = f"Error in upgrade task: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            send_log(error_msg)

    @action(detail=True, methods=['GET'])
    def upgrade_status(self, request, pk=None):
        """获取升级任务状态"""
        task_id = pk
        if task_id not in upgrade_tasks:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        task = upgrade_tasks[task_id]
        return Response({
            'status': task['status'],
            'logs': '\n'.join(task['logs'])
        })

def some_view(request):
    configs = Config.objects.all()
    for config in configs:
        logger.info(f'Configuration: {config.id}')
    # Rest of the view...

class BuildViewSet(viewsets.ModelViewSet):
    queryset = Build.objects.all()
    serializer_class = BuildSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # 在方法最开始添加一个文件写入测试
        with open('create_debug.log', 'a') as f:
            f.write(f"create method called at {datetime.now()}\n")
            f.write(f"request data: {request.data}\n")
            f.write("-" * 50 + "\n")
        
        logger.info("="*50)
        logger.info("BuildViewSet.create 方法被调用")
        logger.info(f"请求方法: {request.method}")
        logger.info(f"请求路径: {request.path}")
        logger.info(f"请求数据: {request.data}")
        logger.info("="*50)
        
        try:
            # 直接创建构建记录
            build = Build.objects.create(
                upgrade_type=request.data['upgrade_type'],
                work_type=request.data['work_type'],
                ne_ip=request.data['ne_ip'],
                ne_ip_input=request.data.get('ne_ip_input', ''),
                version_path=request.data['version_path'],
                status='in_progress'
            )
            logger.info(f"构建记录创建成功: ID={build.id}")

            # 创建初始日志
            initial_log = BuildLog.objects.create(
                build=build,
                message=f"开始升级任务\n"
                        f"升级类型: {build.upgrade_type}\n"
                        f"工作类型: {build.work_type}\n"
                        f"NE IP: {build.ne_ip}\n"
                        f"版本路径: {build.version_path}",
                log_type='info'
            )
            logger.info(f"初始日志创建成功: ID={initial_log.id}")

            # 返回响应
            response_data = {
                "id": build.id,
                "status": build.status,
                "message": "构建任务已创建",
                "upgrade_type": build.upgrade_type,
                "work_type": build.work_type,
                "ne_ip": build.ne_ip,
                "version_path": build.version_path,
                "created_at": build.created_at.isoformat()
            }
            logger.info(f"准备返回响应: {response_data}")

            # 启动升级线程
            thread = threading.Thread(
                target=self._run_upgrade,
                args=(build.id, build.upgrade_type, build.work_type, 
                      build.ne_ip, build.version_path)
            )
            thread.start()
            logger.info(f"升级线程已启动: build_id={build.id}")

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"创建构建记录失败: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def stop(self, request, pk=None):
        """停止升级任务"""
        logger.info(f"Processing stop request for build {pk}")
        try:
            try:
                build = self.get_object()
            except Build.DoesNotExist:
                logger.error(f"Build {pk} not found")
                return Response(
                    {'error': f'Build {pk} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 记录停止日志
            BuildLog.objects.create(
                build=build,
                message="升级任务已手动停止",
                log_type='warning'
            )
            
            # 更新状态
            build.status = 'stopped'
            build.save()
            
            return Response({
                'status': 'stopped',
                'message': '升级任务已停止'
            })
            
        except Exception as e:
            logger.error(f"Error stopping build: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['GET'])
    def logs(self, request, pk=None):
        """获取构建日志"""
        logger.info(f"获取日志请 build_id={pk}, last_log_id={request.query_params.get('last_log_id')}")
        try:
            try:
                build = self.get_object()
            except Build.DoesNotExist:
                logger.error(f"Build {pk} not found")
                return Response(
                    {'error': f'Build {pk} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            last_log_id = int(request.query_params.get('last_log_id', 0))
            
            # 只获取新的日志
            logs = build.logs.filter(id__gt=last_log_id).order_by('timestamp')
            
            # 序列化日志
            serializer = BuildLogSerializer(logs, many=True)
            
            # 返回日志和状态
            response_data = {
                'logs': serializer.data,
                'status': build.status,
                'last_log_id': max([log.id for log in logs], default=last_log_id)
            }
            
            logger.info(f"返回新日志数量: {len(logs)}")
            return Response(response_data)
        except Exception as e:
            logger.error(f"获取日志失败: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _run_upgrade(self, build_id, upgrade_type, work_type, ne_ip, version_path):
        """执行升级任务"""
        build = Build.objects.get(id=build_id)
        try:
            logger.info(f"开始执行升级任务 {build_id}")
            
            # 记录开始日志
            BuildLog.objects.create(
                build=build,
                message=f"开始升级任务\n"
                        f"升级类型: {upgrade_type}\n"
                        f"工作类型: {work_type}\n"
                        f"NE IP: {ne_ip}\n"
                        f"版本路径: {version_path}",
                log_type='info'
            )

            def log_callback(message):
                """接收升级脚本的日志"""
                logger.info(f"升级日志 [{build_id}]: {message}")
                try:
                    BuildLog.objects.create(
                        build=build,
                        message=message,
                        log_type='info'
                    )
                except Exception as e:
                    logger.error(f"保存日志失败: {str(e)}")

            # 测试日志回调是否工作
            log_callback("测试日志回调函数")

            # 检查 ssh_cli 模块
            logger.info(f"ssh_cli module location: {ssh_cli.__file__}")
            logger.info(f"ssh_cli.upgrade function: {getattr(ssh_cli, 'upgrade', None)}")

            # 执行升级脚本
            logger.info(f"准备调用升级脚本 {build_id}")
            logger.info(f"参数: upgrade_type={upgrade_type}, work_type={work_type}, ne_ip={ne_ip}, version_path={version_path}")
            
            try:
                result = ssh_cli.upgrade(
                    upgrade_type=upgrade_type,
                    work_type=work_type,
                    ne_ip=ne_ip,
                    version_path=version_path,
                    callback=log_callback
                )
                logger.info(f"升级脚本执行完成 {build_id}, result={result}")
            except Exception as script_error:
                logger.error(f"升级脚本执行误: {str(script_error)}")
                logger.error(traceback.format_exc())
                raise

            # 更新最终状态
            build.status = 'success' if result else 'failed'
            build.save()
            logger.info(f"更新构建状态为: {build.status}")

            BuildLog.objects.create(
                build=build,
                message="升级任务完成" if result else "升级任务失败",
                log_type='success' if result else 'error'
            )

        except Exception as e:
            logger.error(f"升级任务异常 {build_id}: {str(e)}")
            logger.error(traceback.format_exc())
            BuildLog.objects.create(
                build=build,
                message=f"升级失败: {str(e)}",
                log_type='error'
            )
            build.status = 'failed'
            build.save()

    def list(self, request, *args, **kwargs):
        """获取构建历史"""
        try:
            logger.info("正在获取构建历史...")
            # 获取最近6次构建记录
            builds = Build.objects.all().order_by('-created_at')[:6]
            logger.info(f"找到 {builds.count()} 条构建记录")
            
            serializer = self.get_serializer(builds, many=True)
            logger.info(f"序列化数据: {serializer.data}")
            
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"获取构建历史失败: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['GET'])
    def build_logs(self, request, pk=None):
        """获取指定构建的所有日志"""
        try:
            build = self.get_object()
            logs = build.logs.all().order_by('timestamp')
            serializer = BuildLogSerializer(logs, many=True)
            return Response({
                'logs': serializer.data,
                'status': build.status
            })
        except Exception as e:
            logger.error(f"Error fetching build logs: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
