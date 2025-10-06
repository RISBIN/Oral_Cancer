from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.detection.models import Image, DetectionResult
from apps.reports.models import Report

@login_required
def home(request):
    """Dashboard home view"""
    user = request.user
    
    # Get statistics
    total_images = Image.objects.filter(user=user).count()
    processed_images = Image.objects.filter(user=user, status='processed').count()
    cancer_detections = DetectionResult.objects.filter(user=user, prediction='Cancer').count()
    total_reports = Report.objects.filter(user=user).count()
    
    # Get recent images
    recent_images = Image.objects.filter(user=user).order_by('-upload_date')[:5]
    
    context = {
        'total_images': total_images,
        'processed_images': processed_images,
        'cancer_detections': cancer_detections,
        'total_reports': total_reports,
        'recent_images': recent_images,
    }
    
    return render(request, 'dashboard/home.html', context)
