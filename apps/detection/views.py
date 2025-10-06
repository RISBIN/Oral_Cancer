from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Image, DetectionResult
from config.supabase import SupabaseStorage
import uuid
from datetime import datetime

@login_required
def upload(request):
    """Image upload view"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            uploaded_file = request.FILES['image']
            
            # Validate file size (10MB max)
            if uploaded_file.size > 10485760:
                return JsonResponse({'error': 'File size exceeds 10MB'}, status=400)

            # Read file data first (before creating record)
            file_data = uploaded_file.read()
            uploaded_file.seek(0)  # Reset for Django's save

            # Create image record
            image = Image.objects.create(
                user=request.user,
                filename=uploaded_file.name,
                file=uploaded_file,
                file_size=uploaded_file.size,
                status='pending'
            )

            # Upload to Supabase Storage
            try:
                storage = SupabaseStorage()
                file_path = f"{request.user.id}/{datetime.now().strftime('%Y/%m/%d')}/{image.id}_{uploaded_file.name}"

                # Upload file (using previously read data)
                storage.upload_file(file_path, file_data, uploaded_file.content_type)

                # Get public URL
                public_url = storage.get_public_url(file_path)
                image.file_url = public_url
                image.status = 'processed'  # Mark as processed (would normally process with ML model)
                image.save()

            except Exception as e:
                print(f"Supabase upload error: {e}")
                # Continue with local storage if Supabase fails
                image.status = 'processed'
                image.save()
            
            messages.success(request, f'Image "{uploaded_file.name}" uploaded successfully!')
            return JsonResponse({
                'success': True,
                'redirect_url': f'/detection/results/{image.id}/'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'detection/upload.html')

@login_required
def history(request):
    """Detection history view"""
    images = Image.objects.filter(user=request.user).order_by('-upload_date')
    
    context = {
        'images': images,
    }
    
    return render(request, 'detection/history.html', context)

@login_required
def results(request, id):
    """Detection results view"""
    image = get_object_or_404(Image, id=id, user=request.user)

    # Generate demo results if requested
    if request.method == 'POST' and request.POST.get('generate_demo'):
        import random

        # Generate RegNetY320 result
        regnet_confidence = random.uniform(0.85, 0.95)
        regnet_prediction = 'Cancer' if regnet_confidence > 0.88 else 'Non-Cancer'
        DetectionResult.objects.create(
            image=image,
            user=request.user,
            model_name='RegNetY320',
            prediction=regnet_prediction,
            confidence_score=regnet_confidence,
            processing_time=random.uniform(8.0, 12.0),
            model_version='v1.0'
        )

        # Generate VGG16 result
        vgg16_confidence = random.uniform(0.70, 0.80)
        vgg16_prediction = 'Cancer' if vgg16_confidence > 0.75 else 'Non-Cancer'
        DetectionResult.objects.create(
            image=image,
            user=request.user,
            model_name='VGG16',
            prediction=vgg16_prediction,
            confidence_score=vgg16_confidence,
            processing_time=random.uniform(15.0, 20.0),
            model_version='v1.0'
        )

        messages.success(request, 'Demo detection results generated successfully!')
        return redirect('detection:results', id=id)

    # Get detection results for this image
    detection_results = DetectionResult.objects.filter(image=image).order_by('-created_at')

    context = {
        'image': image,
        'detection_results': detection_results,
    }

    return render(request, 'detection/results.html', context)
