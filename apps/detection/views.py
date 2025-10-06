from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Image, DetectionResult
from config.supabase import SupabaseStorage
from ml_models import predict_with_both_models
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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

    # Run ML inference if requested
    if request.method == 'POST' and request.POST.get('run_detection'):
        print(f"[DEBUG] POST request received with run_detection")
        print(f"[DEBUG] POST data: {request.POST}")
        try:
            # Get image path
            image_path = image.file.path if image.file else None
            print(f"[DEBUG] Image path: {image_path}")

            if not image_path:
                messages.error(request, 'Image file not found. Please re-upload the image.')
                return redirect('detection:results', id=id)

            # Run prediction with both models
            print(f"[INFO] Running ML inference on image: {image_path}")
            logger.info(f"Running ML inference on image: {image_path}")
            predictions = predict_with_both_models(image_path)
            print(f"[DEBUG] Predictions: {predictions}")

            # Save RegNetY320 results
            if predictions.get('regnet'):
                regnet_result = predictions['regnet']
                DetectionResult.objects.create(
                    image=image,
                    user=request.user,
                    model_name='RegNetY320',
                    prediction=regnet_result['prediction'],
                    confidence_score=regnet_result['confidence'],
                    processing_time=regnet_result['processing_time'],
                    model_version='v1.0'
                )
                logger.info(f"RegNet prediction: {regnet_result['prediction']} ({regnet_result['confidence']:.2%})")

            # Save VGG16 results
            if predictions.get('vgg16'):
                vgg16_result = predictions['vgg16']
                DetectionResult.objects.create(
                    image=image,
                    user=request.user,
                    model_name='VGG16',
                    prediction=vgg16_result['prediction'],
                    confidence_score=vgg16_result['confidence'],
                    processing_time=vgg16_result['processing_time'],
                    model_version='v1.0'
                )
                logger.info(f"VGG16 prediction: {vgg16_result['prediction']} ({vgg16_result['confidence']:.2%})")

            # Update image status
            image.status = 'processed'
            image.save()

            messages.success(request, 'Detection completed successfully!')

        except Exception as e:
            logger.error(f"Error during ML inference: {e}")
            messages.error(request, f'Error during detection: {str(e)}')
            image.status = 'failed'
            image.save()

        return redirect('detection:results', id=id)

    # Get detection results for this image
    detection_results = DetectionResult.objects.filter(image=image).order_by('-created_at')

    context = {
        'image': image,
        'detection_results': detection_results,
    }

    return render(request, 'detection/results.html', context)
