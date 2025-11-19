from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
import json
from apps.detection.models import Image, DetectionResult
from apps.reports.models import Report

@login_required
def home(request):
    """Dashboard home view"""
    user = request.user

    # Basic statistics
    total_images = Image.objects.filter(user=user).count()
    processed_images = Image.objects.filter(user=user, status='processed').count()
    cancer_detections = DetectionResult.objects.filter(user=user, prediction='Cancer').count()
    non_cancer_detections = DetectionResult.objects.filter(user=user, prediction='Non-Cancer').count()
    total_reports = Report.objects.filter(user=user).count()

    # Detection rate percentage
    total_detections = cancer_detections + non_cancer_detections
    detection_rate = round((cancer_detections / total_detections * 100), 1) if total_detections > 0 else 0

    # Average confidence score
    avg_confidence = DetectionResult.objects.filter(user=user).aggregate(
        avg=Avg('confidence_score')
    )['avg'] or 0
    avg_confidence = round(avg_confidence * 100, 1)

    # Average processing time
    avg_processing_time = DetectionResult.objects.filter(user=user).aggregate(
        avg=Avg('processing_time')
    )['avg'] or 0
    avg_processing_time = round(avg_processing_time, 2)

    # High confidence detections (>80%)
    high_confidence_count = DetectionResult.objects.filter(
        user=user, confidence_score__gte=0.80
    ).count()

    # Scans this week and month
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    scans_this_week = Image.objects.filter(user=user, upload_date__gte=week_ago).count()
    scans_this_month = Image.objects.filter(user=user, upload_date__gte=month_ago).count()

    # Model performance stats
    regnet_results = DetectionResult.objects.filter(user=user, model_name='RegNetY320')
    vgg16_results = DetectionResult.objects.filter(user=user, model_name='VGG16')

    regnet_cancer = regnet_results.filter(prediction='Cancer').count()
    regnet_total = regnet_results.count()
    regnet_avg_confidence = regnet_results.aggregate(avg=Avg('confidence_score'))['avg'] or 0

    vgg16_cancer = vgg16_results.filter(prediction='Cancer').count()
    vgg16_total = vgg16_results.count()
    vgg16_avg_confidence = vgg16_results.aggregate(avg=Avg('confidence_score'))['avg'] or 0

    # Weekly scan data for line chart (last 7 days)
    weekly_data = []
    weekly_labels = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        count = Image.objects.filter(
            user=user,
            upload_date__gte=day_start,
            upload_date__lte=day_end
        ).count()
        weekly_data.append(count)
        weekly_labels.append(day.strftime('%a'))

    # Get recent images with their detection results
    recent_images = Image.objects.filter(user=user).order_by('-upload_date')[:5]
    recent_images_with_results = []
    for image in recent_images:
        results = DetectionResult.objects.filter(image=image).order_by('-confidence_score')
        primary_result = results.first()
        recent_images_with_results.append({
            'image': image,
            'primary_result': primary_result,
            'all_results': results
        })

    # Recent activity timeline
    recent_detections = DetectionResult.objects.filter(user=user).order_by('-created_at')[:10]
    recent_reports = Report.objects.filter(user=user).order_by('-generated_at')[:5]

    context = {
        'total_images': total_images,
        'processed_images': processed_images,
        'cancer_detections': cancer_detections,
        'non_cancer_detections': non_cancer_detections,
        'total_reports': total_reports,
        'detection_rate': detection_rate,
        'avg_confidence': avg_confidence,
        'avg_processing_time': avg_processing_time,
        'high_confidence_count': high_confidence_count,
        'scans_this_week': scans_this_week,
        'scans_this_month': scans_this_month,
        'regnet_cancer': regnet_cancer,
        'regnet_total': regnet_total,
        'regnet_avg_confidence': round(regnet_avg_confidence * 100, 1),
        'vgg16_cancer': vgg16_cancer,
        'vgg16_total': vgg16_total,
        'vgg16_avg_confidence': round(vgg16_avg_confidence * 100, 1),
        'weekly_data': json.dumps(weekly_data),
        'weekly_labels': json.dumps(weekly_labels),
        'pie_data': json.dumps([cancer_detections, non_cancer_detections]),
        'recent_images': recent_images_with_results,
        'recent_detections': recent_detections,
        'recent_reports': recent_reports,
    }

    return render(request, 'dashboard/home.html', context)
