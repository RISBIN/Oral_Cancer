# CHAPTER 7: IMPLEMENTATION CODE

## Overview

Implementation code represents the practical realization of system design specifications, translating architectural diagrams, database schemas, and functional requirements into executable Python, JavaScript, HTML, and CSS that collectively deliver the OralCare AI platform. The implementation follows Django web framework conventions organizing code into reusable applications, models defining data structures, views implementing request handling logic, templates generating HTML presentations, and static assets providing styling and interactivity. The codebase emphasizes clean architecture principles including separation of concerns where each module addresses distinct responsibilities, dependency injection enabling testability and flexibility, defensive programming validating inputs and handling errors gracefully, and comprehensive documentation through docstrings and comments explaining complex logic. This chapter presents key implementation code segments demonstrating core functionality including user authentication, image upload and storage, AI model inference, results management, and report generation, providing concrete examples of how theoretical designs manifest in working software.

The implementation leverages Django's model-view-template architecture which separates data management in models from request processing in views and presentation in templates, enabling independent evolution of each layer while maintaining clean interfaces. Models inherit from Django's Model class gaining database abstraction through the ORM that generates SQL queries from Python method calls, manages relationships through foreign keys, and enforces data integrity through field validators and model constraints. Views implement request handlers as Python functions or class-based views that authenticate users, validate inputs, coordinate business logic, query databases through model managers, invoke AI inference pipelines, and return HTTP responses with rendered templates or JSON data. Templates use Django's template language combining HTML with template tags for control flow, filters for data transformation, and variable interpolation embedding dynamic content within static markup structures. The implementation also includes middleware for cross-cutting concerns like authentication, CSRF protection, and request logging, management commands for administrative tasks like data imports and cleanup operations, and signal handlers coordinating actions across models when specific events occur.

## User Authentication Implementation

### User Model Definition

The User model extends Django's AbstractUser base class adding healthcare-specific fields while inheriting authentication functionality including password hashing, permission management, and session handling. The model defines the database schema for the users table and implements business logic for user-related operations.

```python
# accounts/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with additional fields
    for healthcare professionals, administrators, researchers, and students.
    """

    # Use UUID as primary key for security and distributed system compatibility
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user"
    )

    # Role-based access control
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('doctor', 'Doctor/Healthcare Provider'),
        ('researcher', 'Researcher'),
        ('student', 'Student'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='doctor',
        help_text="User role determining access permissions"
    )

    # Professional information
    institution = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Affiliated institution or hospital"
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )

    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Professional biography"
    )

    profile_picture_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to profile picture in Supabase Storage"
    )

    # Email verification
    is_verified = models.BooleanField(
        default=False,
        help_text="Email verification status"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['institution']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'

    def is_doctor(self):
        """Check if user has doctor role."""
        return self.role == 'doctor'

    def is_researcher(self):
        """Check if user has researcher role."""
        return self.role == 'researcher'

    def is_student(self):
        """Check if user has student role."""
        return self.role == 'student'

    def can_upload_images(self):
        """Check if user has permission to upload images."""
        return self.role in ['doctor', 'student']

    def can_generate_reports(self):
        """Check if user has permission to generate reports."""
        return self.role in ['doctor', 'admin']

    def can_access_analytics(self):
        """Check if user has permission to access analytics."""
        return self.role in ['admin', 'researcher']
```

### Registration View and Form

The registration system implements account creation with validation, email verification, and role assignment.

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User

class RegistrationForm(UserCreationForm):
    """
    User registration form with additional fields and validation.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autocomplete': 'email'
        }),
        help_text='Required. Enter a valid email address.'
    )

    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'autocomplete': 'given-name'
        })
    )

    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name'
        })
    )

    role = forms.ChoiceField(
        required=True,
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select your role'
    )

    institution = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Institution (Optional)'
        })
    )

    phone_number = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (Optional)',
            'autocomplete': 'tel'
        })
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2', 'role', 'institution', 'phone_number'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'autocomplete': 'username'
            }),
        }

    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        """Validate username uniqueness and format."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_password2(self):
        """Validate password confirmation matches."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        # Additional password strength validation
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if password1.isdigit():
            raise ValidationError("Password cannot be entirely numeric.")

        return password2

    def save(self, commit=True):
        """Save user with normalized email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()

        if commit:
            user.save()

        return user


# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .forms import RegistrationForm
from .models import User

def register_view(request):
    """
    Handle user registration with email verification.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            # Create user but don't activate yet
            user = form.save(commit=False)
            user.is_active = True  # Active but not verified
            user.is_verified = False
            user.save()

            # Send verification email
            send_verification_email(request, user)

            messages.success(
                request,
                'Registration successful! Please check your email to verify your account.'
            )

            return redirect('login')
        else:
            messages.error(
                request,
                'Please correct the errors below.'
            )
    else:
        form = RegistrationForm()

    context = {
        'form': form,
        'title': 'Register - OralCare AI'
    }

    return render(request, 'accounts/register.html', context)


def send_verification_email(request, user):
    """
    Send email verification link to user.
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    verification_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Verify Your OralCare AI Account'
    message = f"""
    Hello {user.get_full_name()},

    Thank you for registering with OralCare AI!

    Please click the link below to verify your email address:
    {verification_link}

    This link will expire in 24 hours.

    If you did not create this account, please ignore this email.

    Best regards,
    OralCare AI Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def verify_email(request, uidb64, token):
    """
    Verify user email address using token.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()

        messages.success(
            request,
            'Email verified successfully! You can now log in.'
        )
        return redirect('login')
    else:
        messages.error(
            request,
            'Verification link is invalid or has expired.'
        )
        return redirect('register')


def login_view(request):
    """
    Handle user login with email or username.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        # Try to authenticate with username first, then email
        user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            # Try authenticating with email
            try:
                user_obj = User.objects.get(email=username_or_email.lower())
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)

            # Set session expiry based on remember_me
            if not remember_me:
                request.session.set_expiry(0)  # Session expires on browser close
            else:
                request.session.set_expiry(1209600)  # 2 weeks

            messages.success(request, f'Welcome back, {user.get_full_name()}!')

            # Redirect to next page or dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username/email or password.')

    context = {
        'title': 'Login - OralCare AI'
    }

    return render(request, 'accounts/login.html', context)


@login_required
def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Display user dashboard with role-specific content.
    """
    from detection.models import Image, DetectionResult
    from reports.models import Report

    # Get user statistics
    total_images = Image.objects.filter(user=request.user).count()
    processed_images = Image.objects.filter(user=request.user, status='processed').count()
    total_reports = Report.objects.filter(user=request.user).count()

    # Get recent images
    recent_images = Image.objects.filter(user=request.user).order_by('-upload_date')[:5]

    # Get detection statistics
    cancer_detections = DetectionResult.objects.filter(
        user=request.user,
        prediction='Cancer'
    ).count()

    non_cancer_detections = DetectionResult.objects.filter(
        user=request.user,
        prediction='Non-Cancer'
    ).count()

    context = {
        'title': 'Dashboard - OralCare AI',
        'total_images': total_images,
        'processed_images': processed_images,
        'total_reports': total_reports,
        'recent_images': recent_images,
        'cancer_detections': cancer_detections,
        'non_cancer_detections': non_cancer_detections,
    }

    return render(request, 'accounts/dashboard.html', context)
```

## Image Upload and Storage Implementation

### Image Model and Upload Handling

The image management system handles file uploads, validation, storage in Supabase, and metadata persistence.

```python
# detection/models.py
import uuid
from django.db import models
from django.conf import settings
from accounts.models import User

class Image(models.Model):
    """
    Model representing uploaded oral lesion images.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="User who uploaded the image"
    )

    filename = models.CharField(
        max_length=255,
        help_text="Original filename"
    )

    file_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Supabase Storage public URL"
    )

    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Storage path/key"
    )

    file_size = models.IntegerField(
        blank=True,
        null=True,
        help_text="File size in bytes"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Processing status"
    )

    upload_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Upload timestamp"
    )

    processed_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Processing completion timestamp"
    )

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="User notes about the image"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'images'
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['user', '-upload_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.filename} - {self.user.get_full_name()}"

    def get_detection_results(self):
        """Get all detection results for this image."""
        return self.detection_results.all()

    def has_results(self):
        """Check if image has detection results."""
        return self.detection_results.exists()

    def get_consensus_prediction(self):
        """
        Get consensus prediction if both models agree.
        Returns prediction if consensus, None if disagreement.
        """
        results = self.detection_results.all()

        if results.count() < 2:
            return None

        predictions = [r.prediction for r in results]

        if len(set(predictions)) == 1:
            return predictions[0]

        return None


# detection/storage.py
from supabase import create_client
from django.conf import settings
import os
from datetime import datetime

class SupabaseStorage:
    """
    Handler for Supabase Storage operations.
    """

    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.bucket_name = settings.SUPABASE_BUCKET_NAME

    def generate_file_path(self, user_id, filename):
        """
        Generate organized storage path for file.
        Format: {user_id}/{year}/{month}/{day}/{uuid}_{filename}
        """
        now = datetime.now()
        unique_filename = f"{uuid.uuid4()}_{filename}"

        path = f"{user_id}/{now.year}/{now.month:02d}/{now.day:02d}/{unique_filename}"
        return path

    def upload_file(self, file, user_id, filename):
        """
        Upload file to Supabase Storage.

        Args:
            file: File object to upload
            user_id: User UUID
            filename: Original filename

        Returns:
            tuple: (file_path, public_url)
        """
        try:
            # Generate storage path
            file_path = self.generate_file_path(user_id, filename)

            # Read file data
            file.seek(0)
            file_data = file.read()

            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket_name).upload(
                file_path,
                file_data,
                file_options={
                    "content-type": file.content_type,
                    "cache-control": "3600"
                }
            )

            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)

            return file_path, public_url

        except Exception as e:
            raise Exception(f"Failed to upload file to Supabase: {str(e)}")

    def download_file(self, file_path):
        """
        Download file from Supabase Storage.

        Args:
            file_path: Storage path

        Returns:
            bytes: File data
        """
        try:
            response = self.client.storage.from_(self.bucket_name).download(file_path)
            return response
        except Exception as e:
            raise Exception(f"Failed to download file from Supabase: {str(e)}")

    def delete_file(self, file_path):
        """
        Delete file from Supabase Storage.

        Args:
            file_path: Storage path

        Returns:
            bool: Success status
        """
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            raise Exception(f"Failed to delete file from Supabase: {str(e)}")


# detection/forms.py
from django import forms
from .models import Image

class ImageUploadForm(forms.ModelForm):
    """
    Form for image upload with validation.
    """

    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png',
            'id': 'imageInput'
        }),
        help_text='Supported formats: JPEG, PNG. Max size: 10MB'
    )

    class Meta:
        model = Image
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this image'
            })
        }

    def clean_image(self):
        """Validate uploaded image."""
        image = self.cleaned_data.get('image')

        if not image:
            raise forms.ValidationError("No image provided.")

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png']
        if image.content_type not in allowed_types:
            raise forms.ValidationError(
                "Invalid file type. Only JPEG and PNG images are allowed."
            )

        # Validate file size (10MB max)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if image.size > max_size:
            raise forms.ValidationError(
                f"File size exceeds 10MB limit. Your file is {image.size / (1024*1024):.2f}MB."
            )

        return image


# detection/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Image, DetectionResult
from .forms import ImageUploadForm
from .storage import SupabaseStorage
from .ai_inference import detect_oral_cancer

@login_required
def upload_image_view(request):
    """
    Handle image upload and initiate AI detection.
    """
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                uploaded_file = request.FILES['image']

                # Create Image instance
                image = form.save(commit=False)
                image.user = request.user
                image.filename = uploaded_file.name
                image.file_size = uploaded_file.size
                image.status = 'pending'

                # Upload to Supabase Storage
                storage = SupabaseStorage()
                file_path, public_url = storage.upload_file(
                    uploaded_file,
                    str(request.user.id),
                    uploaded_file.name
                )

                image.file_path = file_path
                image.file_url = public_url
                image.save()

                # Initiate AI detection
                image.status = 'processing'
                image.save()

                try:
                    # Run AI inference
                    results = detect_oral_cancer(image)

                    image.status = 'processed'
                    image.processed_date = timezone.now()
                    image.save()

                    messages.success(
                        request,
                        'Image uploaded and analyzed successfully!'
                    )

                    return redirect('detection_results', image_id=image.id)

                except Exception as e:
                    image.status = 'failed'
                    image.save()

                    messages.error(
                        request,
                        f'Image uploaded but AI detection failed: {str(e)}'
                    )

                    return redirect('upload_image')

            except Exception as e:
                messages.error(
                    request,
                    f'Failed to upload image: {str(e)}'
                )
        else:
            messages.error(
                request,
                'Please correct the errors below.'
            )
    else:
        form = ImageUploadForm()

    context = {
        'form': form,
        'title': 'Upload Image - OralCare AI'
    }

    return render(request, 'detection/upload.html', context)


@login_required
def image_gallery_view(request):
    """
    Display user's uploaded images gallery.
    """
    images = Image.objects.filter(user=request.user).order_by('-upload_date')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        images = images.filter(status=status_filter)

    context = {
        'images': images,
        'title': 'My Images - OralCare AI',
        'status_filter': status_filter
    }

    return render(request, 'detection/gallery.html', context)


@login_required
def delete_image_view(request, image_id):
    """
    Delete image and associated data.
    """
    image = get_object_or_404(Image, id=image_id, user=request.user)

    if request.method == 'POST':
        try:
            # Delete from Supabase Storage
            storage = SupabaseStorage()
            storage.delete_file(image.file_path)

            # Delete from database (cascade deletes detection results)
            filename = image.filename
            image.delete()

            messages.success(
                request,
                f'Image "{filename}" deleted successfully.'
            )
        except Exception as e:
            messages.error(
                request,
                f'Failed to delete image: {str(e)}'
            )

        return redirect('image_gallery')

    context = {
        'image': image,
        'title': 'Delete Image - OralCare AI'
    }

    return render(request, 'detection/delete_confirm.html', context)
```

## AI Detection Implementation

### Model Loading and Inference

The AI detection module loads TensorFlow models and performs inference on uploaded images.

```python
# detection/ai_inference.py
import tensorflow as tf
import numpy as np
from PIL import Image as PILImage
import io
from django.conf import settings
from .models import DetectionResult
from .storage import SupabaseStorage
import time

# Global model cache
_models = {}

def load_models():
    """
    Load AI models at startup.
    Returns dict of model_name -> model
    """
    global _models

    if _models:
        return _models

    try:
        # Load RegNetY320 model
        regnety_path = settings.REGNETY320_MODEL_PATH
        _models['RegNetY320'] = tf.keras.models.load_model(regnety_path)

        # Load VGG16 model
        vgg16_path = settings.VGG16_MODEL_PATH
        _models['VGG16'] = tf.keras.models.load_model(vgg16_path)

        print("AI models loaded successfully")

    except Exception as e:
        print(f"Error loading AI models: {str(e)}")
        raise

    return _models


def preprocess_image(image_data, target_size=(224, 224)):
    """
    Preprocess image for AI model inference.

    Args:
        image_data: Image bytes
        target_size: Target image dimensions

    Returns:
        numpy.ndarray: Preprocessed image array
    """
    try:
        # Open image from bytes
        img = PILImage.open(io.BytesIO(image_data))

        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize to target size using high-quality resampling
        img = img.resize(target_size, PILImage.LANCZOS)

        # Convert to numpy array
        img_array = np.array(img)

        # Normalize pixel values to [0, 1]
        img_array = img_array.astype('float32') / 255.0

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    except Exception as e:
        raise Exception(f"Image preprocessing failed: {str(e)}")


def run_inference(model, preprocessed_image):
    """
    Run model inference on preprocessed image.

    Args:
        model: Loaded TensorFlow model
        preprocessed_image: Preprocessed image array

    Returns:
        tuple: (prediction, confidence_score, inference_time)
    """
    try:
        start_time = time.time()

        # Run prediction
        predictions = model.predict(preprocessed_image, verbose=0)

        inference_time = time.time() - start_time

        # Get confidence score for positive class (Cancer)
        confidence_score = float(predictions[0][0])

        # Classify based on threshold (0.5)
        prediction = 'Cancer' if confidence_score >= 0.5 else 'Non-Cancer'

        return prediction, confidence_score, inference_time

    except Exception as e:
        raise Exception(f"Model inference failed: {str(e)}")


def detect_oral_cancer(image_instance):
    """
    Perform oral cancer detection on uploaded image.

    Args:
        image_instance: Image model instance

    Returns:
        list: DetectionResult instances
    """
    try:
        # Load models
        models = load_models()

        # Download image from Supabase Storage
        storage = SupabaseStorage()
        image_data = storage.download_file(image_instance.file_path)

        # Preprocess image
        preprocessed_image = preprocess_image(image_data)

        results = []

        # Run inference with both models
        for model_name, model in models.items():
            prediction, confidence, proc_time = run_inference(
                model,
                preprocessed_image
            )

            # Create DetectionResult
            result = DetectionResult.objects.create(
                image=image_instance,
                user=image_instance.user,
                model_name=model_name,
                prediction=prediction,
                confidence_score=confidence,
                processing_time=proc_time,
                model_version='1.0'
            )

            results.append(result)

        return results

    except Exception as e:
        raise Exception(f"AI detection failed: {str(e)}")


# detection/models.py (DetectionResult model)
class DetectionResult(models.Model):
    """
    Model representing AI detection results.
    """

    PREDICTION_CHOICES = [
        ('Cancer', 'Cancer'),
        ('Non-Cancer', 'Non-Cancer'),
    ]

    MODEL_CHOICES = [
        ('RegNetY320', 'RegNetY320'),
        ('VGG16', 'VGG16'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name='detection_results',
        help_text="Associated image"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='detection_results',
        help_text="User who requested detection"
    )

    model_name = models.CharField(
        max_length=50,
        choices=MODEL_CHOICES,
        help_text="AI model used"
    )

    prediction = models.CharField(
        max_length=20,
        choices=PREDICTION_CHOICES,
        help_text="Classification result"
    )

    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="Confidence score (0.0000-1.0000)"
    )

    processing_time = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Inference time in seconds"
    )

    model_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Model version identifier"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'detection_results'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['image', 'model_name']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['prediction']),
        ]

    def __str__(self):
        return f"{self.model_name}: {self.prediction} ({self.confidence_score:.2%})"

    def get_confidence_percentage(self):
        """Return confidence as percentage string."""
        return f"{float(self.confidence_score) * 100:.2f}%"


# detection/views.py (Results view)
@login_required
def detection_results_view(request, image_id):
    """
    Display detection results for an image.
    """
    image = get_object_or_404(Image, id=image_id, user=request.user)

    # Get detection results
    results = DetectionResult.objects.filter(image=image).order_by('model_name')

    # Calculate consensus
    consensus = None
    if results.count() >= 2:
        predictions = [r.prediction for r in results]
        if len(set(predictions)) == 1:
            consensus = predictions[0]

    context = {
        'image': image,
        'results': results,
        'consensus': consensus,
        'title': f'Detection Results - {image.filename}'
    }

    return render(request, 'detection/results.html', context)
```

## Report Generation Implementation

### PDF Report Creation

The report system generates professional PDF documents from detection results.

```python
# reports/models.py
import uuid
from django.db import models
from accounts.models import User
from detection.models import DetectionResult

class Report(models.Model):
    """
    Model representing generated PDF reports.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        help_text="User who generated report"
    )

    detection_result = models.ForeignKey(
        DetectionResult,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reports',
        help_text="Associated detection result"
    )

    patient_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Patient name (optional)"
    )

    patient_age = models.IntegerField(
        blank=True,
        null=True,
        help_text="Patient age"
    )

    patient_gender = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Patient gender"
    )

    medical_record_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Hospital/clinic MRN"
    )

    clinical_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Clinical observations"
    )

    report_pdf_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Supabase Storage URL for PDF"
    )

    report_pdf_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Storage path for PDF"
    )

    generated_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Report generation timestamp"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-generated_date']
        indexes = [
            models.Index(fields=['user', '-generated_date']),
            models.Index(fields=['patient_name']),
        ]

    def __str__(self):
        return f"Report for {self.patient_name or 'Anonymous'} - {self.generated_date}"


# reports/pdf_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import requests

class OralCareReportGenerator:
    """
    PDF report generator for OralCare AI detection results.
    """

    def __init__(self):
        self.buffer = BytesIO()
        self.page_size = letter
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#2C3E50')
        ))

    def generate_report(self, report_data):
        """
        Generate PDF report from data.

        Args:
            report_data: Dict containing report information

        Returns:
            BytesIO: PDF file buffer
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        story = []

        # Header
        story.extend(self._create_header(report_data))

        # Patient Information
        if report_data.get('patient_name'):
            story.extend(self._create_patient_info(report_data))

        # Clinical Image
        story.extend(self._create_image_section(report_data))

        # AI Detection Results
        story.extend(self._create_results_section(report_data))

        # Clinical Notes
        if report_data.get('clinical_notes'):
            story.extend(self._create_notes_section(report_data))

        # Recommendations
        story.extend(self._create_recommendations(report_data))

        # Disclaimer
        story.extend(self._create_disclaimer())

        # Footer
        story.extend(self._create_footer(report_data))

        # Build PDF
        doc.build(story)

        self.buffer.seek(0)
        return self.buffer

    def _create_header(self, data):
        """Create report header."""
        elements = []

        # Title
        title = Paragraph("OralCare AI Detection Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Report metadata
        report_date = data.get('generated_date', datetime.now())
        metadata = f"<b>Report Generated:</b> {report_date.strftime('%B %d, %Y at %I:%M %p')}"
        elements.append(Paragraph(metadata, self.styles['BodyText']))
        elements.append(Spacer(1, 20))

        return elements

    def _create_patient_info(self, data):
        """Create patient information section."""
        elements = []

        elements.append(Paragraph("Patient Information", self.styles['SectionHeader']))

        # Patient info table
        patient_data = [
            ['Patient Name:', data.get('patient_name', 'N/A')],
            ['Age:', str(data.get('patient_age', 'N/A'))],
            ['Gender:', data.get('patient_gender', 'N/A')],
            ['Medical Record #:', data.get('medical_record_number', 'N/A')]
        ]

        table = Table(patient_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _create_image_section(self, data):
        """Create image display section."""
        elements = []

        elements.append(Paragraph("Clinical Image", self.styles['SectionHeader']))

        # Download and embed image
        try:
            image_url = data.get('image_url')
            if image_url:
                response = requests.get(image_url)
                img_buffer = BytesIO(response.content)

                img = Image(img_buffer, width=4*inch, height=3*inch)
                elements.append(img)
                elements.append(Spacer(1, 12))
        except Exception as e:
            elements.append(Paragraph(f"Image unavailable: {str(e)}", self.styles['BodyText']))

        elements.append(Spacer(1, 20))

        return elements

    def _create_results_section(self, data):
        """Create AI detection results section."""
        elements = []

        elements.append(Paragraph("AI Detection Results", self.styles['SectionHeader']))

        results = data.get('detection_results', [])

        if results:
            # Results table
            table_data = [['Model', 'Prediction', 'Confidence', 'Processing Time']]

            for result in results:
                table_data.append([
                    result['model_name'],
                    result['prediction'],
                    f"{result['confidence_score']:.2%}",
                    f"{result['processing_time']:.3f}s"
                ])

            table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
            ]))

            elements.append(table)
            elements.append(Spacer(1, 12))

            # Consensus
            consensus = data.get('consensus')
            if consensus:
                consensus_text = f"<b>Model Consensus:</b> Both models agree on <b>{consensus}</b> prediction."
                elements.append(Paragraph(consensus_text, self.styles['BodyText']))
            else:
                disagreement_text = "<b>Note:</b> Models produced different predictions. Further clinical evaluation recommended."
                elements.append(Paragraph(disagreement_text, self.styles['BodyText']))

        elements.append(Spacer(1, 20))

        return elements

    def _create_notes_section(self, data):
        """Create clinical notes section."""
        elements = []

        elements.append(Paragraph("Clinical Notes", self.styles['SectionHeader']))

        notes = data.get('clinical_notes', '')
        elements.append(Paragraph(notes, self.styles['BodyText']))
        elements.append(Spacer(1, 20))

        return elements

    def _create_recommendations(self, data):
        """Create recommendations section."""
        elements = []

        elements.append(Paragraph("Recommendations", self.styles['SectionHeader']))

        # Determine recommendations based on results
        results = data.get('detection_results', [])
        cancer_predictions = [r for r in results if r['prediction'] == 'Cancer']

        if cancer_predictions:
            recommendation = """
            Based on AI detection indicating potential cancerous lesion:
            <br/><br/>
            1. <b>Immediate Action:</b> Schedule biopsy for definitive diagnosis<br/>
            2. <b>Specialist Referral:</b> Refer to oral surgeon or oncologist<br/>
            3. <b>Follow-up:</b> Ensure patient compliance with referral<br/>
            4. <b>Documentation:</b> Maintain detailed records of findings
            """
        else:
            recommendation = """
            Based on AI detection indicating non-cancerous lesion:
            <br/><br/>
            1. <b>Monitoring:</b> Continue routine oral cancer screening<br/>
            2. <b>Patient Education:</b> Educate on risk factors and prevention<br/>
            3. <b>Follow-up:</b> Schedule regular check-ups as appropriate<br/>
            4. <b>Documentation:</b> Record findings in patient chart
            """

        elements.append(Paragraph(recommendation, self.styles['BodyText']))
        elements.append(Spacer(1, 20))

        return elements

    def _create_disclaimer(self):
        """Create disclaimer section."""
        elements = []

        disclaimer = """
        <b>IMPORTANT DISCLAIMER:</b> This report presents AI-assisted analysis for screening purposes only.
        The predictions provided by OralCare AI models are not definitive diagnoses and should not replace
        professional clinical judgment. Healthcare providers must interpret results in context of complete
        patient history, physical examination, and other diagnostic findings. Biopsy remains the gold
        standard for definitive oral cancer diagnosis. The AI models have limitations and may produce
        false positive or false negative results.
        """

        disclaimer_style = ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['BodyText'],
            fontSize=9,
            textColor=colors.HexColor('#7F8C8D'),
            borderColor=colors.HexColor('#95A5A6'),
            borderWidth=1,
            borderPadding=10,
            spaceAfter=20
        )

        elements.append(Paragraph(disclaimer, disclaimer_style))

        return elements

    def _create_footer(self, data):
        """Create report footer."""
        elements = []

        footer_text = f"""
        <b>Provider:</b> {data.get('provider_name', 'N/A')}<br/>
        <b>Institution:</b> {data.get('institution', 'N/A')}<br/>
        <b>AI Models Used:</b> RegNetY320 (v1.0), VGG16 (v1.0)<br/>
        <b>Report ID:</b> {data.get('report_id', 'N/A')}
        """

        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['BodyText'],
            fontSize=9,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#7F8C8D')
        )

        elements.append(Paragraph(footer_text, footer_style))

        return elements


# reports/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from .models import Report
from .forms import ReportGenerationForm
from .pdf_generator import OralCareReportGenerator
from detection.models import Image, DetectionResult
from detection.storage import SupabaseStorage
import uuid

@login_required
def generate_report_view(request, image_id):
    """
    Generate PDF report for detection results.
    """
    image = get_object_or_404(Image, id=image_id, user=request.user)
    results = DetectionResult.objects.filter(image=image)

    if not results.exists():
        messages.error(request, 'No detection results found for this image.')
        return redirect('image_gallery')

    if request.method == 'POST':
        form = ReportGenerationForm(request.POST)

        if form.is_valid():
            try:
                # Create Report instance
                report = form.save(commit=False)
                report.user = request.user
                report.detection_result = results.first()

                # Prepare report data
                report_data = {
                    'report_id': str(uuid.uuid4()),
                    'generated_date': datetime.now(),
                    'patient_name': form.cleaned_data.get('patient_name'),
                    'patient_age': form.cleaned_data.get('patient_age'),
                    'patient_gender': form.cleaned_data.get('patient_gender'),
                    'medical_record_number': form.cleaned_data.get('medical_record_number'),
                    'clinical_notes': form.cleaned_data.get('clinical_notes'),
                    'image_url': image.file_url,
                    'detection_results': [
                        {
                            'model_name': r.model_name,
                            'prediction': r.prediction,
                            'confidence_score': float(r.confidence_score),
                            'processing_time': float(r.processing_time or 0)
                        }
                        for r in results
                    ],
                    'consensus': image.get_consensus_prediction(),
                    'provider_name': request.user.get_full_name(),
                    'institution': request.user.institution or 'N/A'
                }

                # Generate PDF
                generator = OralCareReportGenerator()
                pdf_buffer = generator.generate_report(report_data)

                # Upload to Supabase Storage
                storage = SupabaseStorage()
                filename = f"report_{uuid.uuid4()}.pdf"

                pdf_buffer.seek(0)
                file_path, public_url = storage.upload_file(
                    pdf_buffer,
                    str(request.user.id),
                    filename
                )

                report.report_pdf_path = file_path
                report.report_pdf_url = public_url
                report.save()

                messages.success(request, 'Report generated successfully!')
                return redirect('download_report', report_id=report.id)

            except Exception as e:
                messages.error(request, f'Failed to generate report: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReportGenerationForm()

    context = {
        'form': form,
        'image': image,
        'results': results,
        'title': 'Generate Report - OralCare AI'
    }

    return render(request, 'reports/generate.html', context)


@login_required
def download_report_view(request, report_id):
    """
    Download generated PDF report.
    """
    report = get_object_or_404(Report, id=report_id, user=request.user)

    try:
        storage = SupabaseStorage()
        pdf_data = storage.download_file(report.report_pdf_path)

        response = FileResponse(
            BytesIO(pdf_data),
            content_type='application/pdf',
            as_attachment=True,
            filename=f"OralCare_Report_{report.id}.pdf"
        )

        return response

    except Exception as e:
        messages.error(request, f'Failed to download report: {str(e)}')
        return redirect('report_history')


@login_required
def report_history_view(request):
    """
    Display user's generated reports.
    """
    reports = Report.objects.filter(user=request.user).order_by('-generated_date')

    context = {
        'reports': reports,
        'title': 'Report History - OralCare AI'
    }

    return render(request, 'reports/history.html', context)
```

The implementation code demonstrates practical application of the OralCare AI system architecture, showing how Django models, views, forms, and business logic coordinate to deliver user authentication, image management with Supabase Storage integration, AI-powered oral cancer detection using TensorFlow models, and professional PDF report generation. The code follows Django conventions, implements comprehensive validation and error handling, maintains security through proper authentication and authorization checks, and provides clean separation of concerns enabling maintainability and testability.
