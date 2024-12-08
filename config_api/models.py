from django.db import models
import json
import logging

# Create your models here.

logger = logging.getLogger(__name__)

class Config(models.Model):
    upgrade_type = models.TextField(default='[]')
    work_type = models.TextField(default='[]')
    env_ip_map = models.TextField(default='{}')

    def set_upgrade_type(self, types_list):
        self.upgrade_type = json.dumps(types_list or [])

    def get_upgrade_type(self):
        try:
            return json.loads(self.upgrade_type)
        except json.JSONDecodeError:
            logger.error(f"Error decoding upgrade_type: {self.upgrade_type}")
            return []

    def set_work_type(self, types_list):
        self.work_type = json.dumps(types_list or [])

    def get_work_type(self):
        try:
            return json.loads(self.work_type)
        except json.JSONDecodeError:
            logger.error(f"Error decoding work_type: {self.work_type}")
            return []

    def set_env_ip_map(self, env_ip_dict):
        self.env_ip_map = json.dumps(env_ip_dict or {})

    def get_env_ip_map(self):
        try:
            return json.loads(self.env_ip_map)
        except json.JSONDecodeError:
            logger.error(f"Error decoding env_ip_map: {self.env_ip_map}")
            return {}

class Build(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('stopped', 'Stopped'),
    )

    upgrade_type = models.CharField(max_length=100)
    work_type = models.CharField(max_length=100)
    ne_ip = models.CharField(max_length=255)
    ne_ip_input = models.CharField(max_length=255, blank=True, null=True)
    version_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Build #{self.id} - {self.status}"

    def save(self, *args, **kwargs):
        # 添加日志记录
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"新建构建记录: {self.id}")
        else:
            logger.info(f"更新构建记录: {self.id}")

class BuildLog(models.Model):
    build = models.ForeignKey(Build, related_name='logs', on_delete=models.CASCADE)
    message = models.TextField()
    log_type = models.CharField(max_length=20, default='info')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.log_type}: {self.message[:50]}"

class Device(models.Model):
    """设备模型"""
    name = models.CharField(max_length=100, verbose_name='设备名称')
    ip_address = models.CharField(max_length=15, verbose_name='IP地址')
    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name='设备类型'
    )
    rack_number = models.CharField(max_length=50, verbose_name='机架编号')
    position = models.IntegerField(verbose_name='机架位置')
    status = models.CharField(max_length=20, verbose_name='设备状态')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    class Meta:
        verbose_name = '设备'
        verbose_name_plural = '设备列表'
        ordering = ['rack_number', 'position']

class Rack(models.Model):
    """机架模型"""
    number = models.CharField(max_length=50, unique=True, verbose_name='机架编号')
    row = models.IntegerField(verbose_name='排号')
    column = models.IntegerField(verbose_name='列号')
    total_units = models.IntegerField(default=42, verbose_name='总单元数')
    
    class Meta:
        verbose_name = '机架'
        verbose_name_plural = '机架列表'
        ordering = ['row', 'column']

class DeviceType(models.Model):
    """设备类型模型"""
    type_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    model_data = models.JSONField(default=dict)  # 存储3D模型数据

class RackConfiguration(models.Model):
    """机架配置模型"""
    rack_number = models.CharField(max_length=50)
    position = models.IntegerField()
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)

class DeviceModel(models.Model):
    image = models.ImageField(upload_to='device_images/')
    model_data = models.JSONField()  # 存储3D模型数据
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
