from django.core.management.base import BaseCommand
from config_api.models import Config
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate configs'

    def handle(self, *args, **options):
        duplicates = Config.objects.values('upgrade_type', 'work_type', 'env_ip_map').annotate(count=Count('id')).filter(count__gt=1)
        for duplicate in duplicates:
            configs = Config.objects.filter(**{k: v for k, v in duplicate.items() if k != 'count'})
            configs.exclude(pk=configs.first().pk).delete()
        self.stdout.write(self.style.SUCCESS('Duplicate configs removed'))
