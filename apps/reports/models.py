from django.db import models
from django.conf import settings
from apps.detection.models import DetectionResult
import uuid


class Report(models.Model):
    """
    Model to store generated PDF reports for detection results
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    detection_result = models.ForeignKey(DetectionResult, on_delete=models.CASCADE, related_name='reports')

    # Patient Information (Optional)
    patient_name = models.CharField(max_length=255, blank=True, null=True)
    patient_age = models.IntegerField(blank=True, null=True)
    patient_gender = models.CharField(max_length=10, blank=True, null=True)
    patient_id = models.CharField(max_length=100, blank=True, null=True)

    # Clinical Information
    clinical_notes = models.TextField(blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)

    # Report File
    report_file = models.FileField(upload_to='reports/%Y/%m/%d/', blank=True, null=True)
    report_pdf_url = models.URLField(blank=True, null=True)  # Supabase Storage URL

    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_finalized = models.BooleanField(default=False)

    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-generated_at']

    def __str__(self):
        return f"Report {self.id} - {self.user.email} - {self.generated_at.date()}"

    @property
    def report_title(self):
        """Generate report title"""
        return f"Oral Cancer Detection Report - {self.generated_at.strftime('%Y-%m-%d')}"
