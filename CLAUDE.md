# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OralCare AI is a Django-based medical web application for oral cancer detection from images. It uses dual PyTorch models (RegNetY320 at 89.4% accuracy, VGG16 at 73.7%), Supabase cloud infrastructure, and generates professional PDF reports.

## Commands

### Development
```bash
# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts
python manage.py test apps.detection

# Collect static files (production)
python manage.py collectstatic --noinput
```

### ML Model Debugging
```bash
python manage.py shell
>>> from ml_models import get_model_info
>>> get_model_info()  # Shows model paths, existence, file sizes, device
```

## Architecture

### Tech Stack
- **Backend**: Django 4.2.11, Python 3.12
- **Database**: PostgreSQL (Supabase) / SQLite (local)
- **ML**: PyTorch with timm (RegNetY320) and torchvision (VGG16)
- **Storage**: Supabase Storage with local fallback
- **PDF**: ReportLab
- **Auth**: Custom User model with email login

### App Structure
```
apps/
├── accounts/     # Auth, registration, profiles (Custom User model)
├── detection/    # Image upload, ML inference, results
├── dashboard/    # User analytics and statistics
└── reports/      # PDF report generation
```

### Key Files
- `config/settings.py` - Django configuration
- `config/supabase.py` - SupabaseStorage class for cloud operations
- `ml_models/inference.py` - `predict_with_both_models(image_path)` function
- `ml_models/*.pth` - Model weights (RegNet: 547MB, VGG16: 464MB)

### Database Models
- **User** (`apps/accounts/models.py`): Custom model using EMAIL as login field, with roles (admin/doctor/researcher/student)
- **Image** (`apps/detection/models.py`): Uploaded images with status tracking and dual storage (local + Supabase URL)
- **DetectionResult** (`apps/detection/models.py`): ML predictions with confidence scores and processing times
- **Report** (`apps/reports/models.py`): Generated PDF metadata and patient info
- **UserActivity** (`apps/accounts/models.py`): Audit logging

All models use UUID primary keys.

### ML Inference Flow
1. Image uploaded via `/detection/upload/` → stored in Supabase and locally
2. POST to `/detection/results/<uuid>/` triggers ML
3. `predict_with_both_models()` runs both models
4. Two DetectionResult records created (one per model)
5. Results displayed with PDF report generation option

### URL Patterns
```
/accounts/       # register, login, logout, profile, settings
/detection/      # upload, history, results/<uuid>
/dashboard/      # home (statistics)
/reports/        # generate/<uuid>, download/<uuid>
```

## Configuration

### Environment Variables (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://... (or sqlite:///db.sqlite3)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=anon-key
SUPABASE_SERVICE_KEY=service-role-key
```

### Image Upload Constraints
- Max size: 10MB (`MAX_UPLOAD_SIZE`)
- Allowed types: JPEG, PNG
- Storage path: `{user_id}/{YYYY/MM/DD}/{image_id}_{filename}`

## Important Patterns

### Custom User Model
- Login uses **email**, not username
- Create users with `User.objects.create_user()` for proper password hashing
- Reference as `settings.AUTH_USER_MODEL` in ForeignKeys

### Storage Fallback
Supabase operations gracefully fall back to local storage if unavailable. Both `file` (local) and `file_url` (Supabase) fields are populated.

### PDF Generation
Uses ReportLab with in-memory BytesIO buffer. Custom `NumberedCanvas` handles headers/footers. Returns HTTP attachment response.

### View Protection
All user-facing views use `@login_required` decorator. Images/results are filtered by `user=request.user`.

## External Dependencies

Key packages beyond standard Django:
- `torch`, `torchvision`, `timm` - ML inference
- `supabase` - Cloud storage/database
- `reportlab` - PDF generation
- `dj-database-url` - Database configuration
- `django-crispy-forms`, `crispy-bootstrap5` - Form styling
