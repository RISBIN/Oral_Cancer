from django.db import models
from django.conf import settings
import uuid


class Image(models.Model):
    """
    Model to store uploaded medical images
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    filename = models.CharField(max_length=255)
    file = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)  # Supabase Storage URL
    file_size = models.IntegerField(help_text="File size in bytes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    upload_date = models.DateTimeField(auto_now_add=True)

    # Image metadata
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    format = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'images'
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.filename} - {self.user.email}"

    @property
    def has_results(self):
        """Check if this image has detection results"""
        return self.detection_results.exists()


class DetectionResult(models.Model):
    """
    Model to store AI detection results
    """
    PREDICTION_CHOICES = (
        ('Cancer', 'Cancer'),
        ('Non-Cancer', 'Non-Cancer'),
    )

    MODEL_CHOICES = (
        ('RegNetY320', 'RegNetY320'),
        ('VGG16', 'VGG16'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='detection_results')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='detection_results')
    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES)
    prediction = models.CharField(max_length=50, choices=PREDICTION_CHOICES)
    confidence_score = models.FloatField(help_text="Confidence score (0-1)")
    processing_time = models.FloatField(help_text="Processing time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)

    # Additional detection metadata
    model_version = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'detection_results'
        verbose_name = 'Detection Result'
        verbose_name_plural = 'Detection Results'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prediction', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.model_name} - {self.prediction} ({self.confidence_score:.2%})"

    @property
    def confidence_percentage(self):
        """Return confidence as percentage"""
        return round(self.confidence_score * 100, 2)

    @property
    def is_high_confidence(self):
        """Check if confidence is above 80%"""
        return self.confidence_score >= 0.80
