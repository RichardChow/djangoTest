from django.contrib import admin
from .models import Build, BuildLog

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ['id', 'upgrade_type', 'work_type', 'ne_ip', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['ne_ip', 'version_path']

@admin.register(BuildLog)
class BuildLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'build', 'message', 'log_type', 'timestamp']
    list_filter = ['log_type', 'timestamp']
    search_fields = ['message']
