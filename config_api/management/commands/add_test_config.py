from django.core.management.base import BaseCommand
from config_api.models import Config

class Command(BaseCommand):
    help = 'Add a test configuration'

    def handle(self, *args, **options):
        config = Config()
        config.set_upgrade_type(['force', 'force_sonet', 'cold-reset'])
        config.set_work_type(['multi_process', 'single_process'])
        config.set_env_ip_map({'CES': ['200.200.18.101', '200.200.18.102']})
        config.save()
        self.stdout.write(self.style.SUCCESS('Successfully added test configuration'))
