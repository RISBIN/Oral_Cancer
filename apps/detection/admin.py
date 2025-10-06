from django.contrib import admin
from .models import Image, DetectionResult


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'status', 'file_size', 'upload_date')
    list_filter = ('status', 'upload_date')
    search_fields = ('filename', 'user__email', 'user__username')
    ordering = ('-upload_date',)
    readonly_fields = ('id', 'upload_date')


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ('image', 'user', 'model_name', 'prediction', 'confidence_percentage', 'created_at')
    list_filter = ('model_name', 'prediction', 'created_at')
    search_fields = ('image__filename', 'user__email', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'confidence_percentage', 'is_high_confidence')
