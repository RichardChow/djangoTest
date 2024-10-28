from rest_framework import serializers
from .models import Config
import logging
import json

logger = logging.getLogger(__name__)

class ConfigSerializer(serializers.ModelSerializer):
    upgrade_type = serializers.CharField(required=False, help_text='每行一个类型')
    work_type = serializers.CharField(required=False, help_text='每行一个类型')
    environments = serializers.CharField(required=False, help_text='JSON格式的环境配置')

    class Meta:
        model = Config
        fields = ['id', 'upgrade_type', 'work_type', 'environments']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['upgrade_type'] = instance.get_upgrade_type() or []
        data['work_type'] = instance.get_work_type() or []
        env_ip_map = instance.get_env_ip_map() or {}
        data['environments'] = [{'ne_env': k, 'ne_ip_list': v} for k, v in env_ip_map.items()]
        return data

    def to_internal_value(self, data):
        internal_data = {}
        
        # 处理 upgrade_type
        if 'upgrade_type' in data:
            if isinstance(data['upgrade_type'], str):
                internal_data['upgrade_type'] = [t.strip() for t in data['upgrade_type'].split('\n') if t.strip()]
            else:
                internal_data['upgrade_type'] = data['upgrade_type']
        
        # 处理 work_type
        if 'work_type' in data:
            if isinstance(data['work_type'], str):
                internal_data['work_type'] = [t.strip() for t in data['work_type'].split('\n') if t.strip()]
            else:
                internal_data['work_type'] = data['work_type']
        
        # 处理 environments
        if 'environments' in data:
            if isinstance(data['environments'], str):
                try:
                    environments = json.loads(data['environments'])
                    env_ip_map = {}
                    for env in environments:
                        if 'ne_env' in env and 'ne_ip_list' in env:
                            env_ip_map[env['ne_env']] = env['ne_ip_list']
                    internal_data['env_ip_map'] = env_ip_map
                except json.JSONDecodeError:
                    raise serializers.ValidationError({'environments': 'Invalid JSON format'})
            else:
                env_ip_map = {}
                for env in data['environments']:
                    if 'ne_env' in env and 'ne_ip_list' in env:
                        env_ip_map[env['ne_env']] = env['ne_ip_list']
                internal_data['env_ip_map'] = env_ip_map
        
        return internal_data

    def create(self, validated_data):
        upgrade_type = validated_data.get('upgrade_type', [])
        work_type = validated_data.get('work_type', [])
        env_ip_map = validated_data.get('env_ip_map', {})
        instance = Config()
        instance.set_upgrade_type(upgrade_type)
        instance.set_work_type(work_type)
        instance.set_env_ip_map(env_ip_map)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if 'upgrade_type' in validated_data:
            instance.set_upgrade_type(validated_data['upgrade_type'])
        if 'work_type' in validated_data:
            instance.set_work_type(validated_data['work_type'])
        if 'env_ip_map' in validated_data:
            instance.set_env_ip_map(validated_data['env_ip_map'])
        instance.save()
        return instance
