from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'detection_result', 'patient_name', 'is_finalized', 'generated_at')
    list_filter = ('is_finalized', 'generated_at')
    search_fields = ('user__email', 'patient_name', 'patient_id')
    ordering = ('-generated_at',)
    readonly_fields = ('id', 'generated_at', 'updated_at', 'report_title')
