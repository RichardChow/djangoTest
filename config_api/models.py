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
