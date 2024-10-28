from django.core.management.base import BaseCommand
from config_api.models import Config

class Command(BaseCommand):
    help = 'Display all configurations'

    def handle(self, *args, **options):
        configs = Config.objects.all()
        self.stdout.write(f"Total {configs.count()} configuration records:")
        for config in configs:
            self.stdout.write(f"ID: {config.id}")
            self.stdout.write(f"Upgrade Types: {config.get_upgrade_type()}")
            self.stdout.write(f"Work Types: {config.get_work_type()}")
            self.stdout.write(f"Environment-IP Map: {config.get_env_ip_map()}")
            self.stdout.write("---")
