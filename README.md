# OralCare AI - Oral Cancer Detection System

A web-based application that uses deep learning (RegNetY320 algorithm) to detect oral cancer from medical images with 89.4% accuracy.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **AI-Powered Detection**: RegNetY320 and VGG16 models for binary classification
- **User Authentication**: Secure login/registration with role-based access
- **Image Upload**: Drag-and-drop upload with Supabase Storage integration
- **Real-time Results**: Instant detection with confidence scores
- **Dashboard Analytics**: Comprehensive statistics and visualizations
- **PDF Reports**: Generate professional medical reports
- **Premium UI**: Clean white medical interface
- **Cloud Storage**: Supabase PostgreSQL database and file storage

## Tech Stack

### Backend
- **Django 5.2**: Web framework
- **PostgreSQL**: Database (Supabase Cloud)
- **TensorFlow/Keras**: ML models
- **Supabase**: Authentication & Storage

### Frontend
- **Django Templates**: Server-side rendering
- **Bootstrap 5**: CSS framework
- **JavaScript (Vanilla)**: Client-side interactivity
- **Font Awesome**: Icons

### ML Models
- **RegNetY320**: Primary model (89.4% accuracy)
- **VGG16**: Comparison model (73.7% accuracy)

## Project Structure

```
oral_cancer/
├── apps/
│   ├── accounts/          # User authentication & profiles
│   ├── detection/         # Image upload & ML detection
│   ├── dashboard/         # Analytics dashboard
│   └── reports/           # PDF report generation
├── config/                # Django settings
├── ml_models/             # Trained ML models
├── static/                # CSS, JS, images
├── templates/             # HTML templates
├── media/                 # User uploads
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── manage.py              # Django management
├── PRD.md                 # Product Requirements Document
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL (or Supabase account)
- pip
- virtualenv

### Step 1: Clone Repository
```bash
cd /home/user/Desktop/oral_cancer
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Supabase

1. Create a Supabase account at https://supabase.com
2. Create a new project
3. Go to Project Settings > Database and copy connection string
4. Go to Project Settings > API and copy URL and Keys
5. Create a storage bucket named `oral-cancer-images`

### Step 5: Configure Environment Variables

Create `.env` file in root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

### Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 9: Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000

## ML Models Setup

### Download Pre-trained Models

**Download from Kaggle Dataset:**

1. Visit: https://www.kaggle.com/datasets/shibinbj/oral-cancer-pretrained-models
2. Download the dataset (contains `regnet_y320_best.pth` and `vgg16_best.pth`)
3. Extract and move the `.pth` files to `ml_models/` directory:

```bash
# After downloading from Kaggle
ml_models/
├── regnet_y320_best.pth  (547 MB)
├── vgg16_best.pth         (464 MB)
└── README.md
```

### Training Your Own Models (Optional)

Use the provided Jupyter notebook `oral_cancer_detection_kaggle.ipynb`:

1. Prepare your oral cancer dataset (cancer and normal images)
2. Update dataset paths in the notebook
3. Run all cells to train RegNetY320 and VGG16 models
4. Models will be saved as `.pth` files automatically

**Model Details:**
- RegNetY320: 89.4% accuracy (timm library)
- VGG16: 73.7% accuracy (torchvision)
- Binary classification: Cancer vs Normal

## Usage

### For Doctors/Researchers

1. **Register**: Create an account with your institution email
2. **Login**: Access your dashboard
3. **Upload Image**: Upload oral pathology images
4. **View Results**: Get instant AI-powered detection results
5. **Generate Report**: Create professional PDF reports
6. **Download**: Export results and reports

### For Administrators

1. Access Django Admin at http://localhost:8000/admin
2. Manage users, images, and detection results
3. View system analytics
4. Configure settings

## API Endpoints

### Authentication
- `POST /accounts/register/` - User registration
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `GET /accounts/profile/` - View profile

### Detection
- `POST /detection/upload/` - Upload image
- `POST /detection/process/<id>/` - Process image
- `GET /detection/results/<id>/` - View results
- `GET /detection/history/` - View history

### Dashboard
- `GET /dashboard/` - Main dashboard
- `GET /dashboard/stats/` - Get statistics

### Reports
- `GET /reports/generate/<id>/` - Generate PDF
- `GET /reports/download/<id>/` - Download report

## Database Schema

### Users
- id (UUID)
- email, username, password
- role (admin, doctor, researcher, student)
- institution, profile_picture_url

### Images
- id (UUID)
- user_id, filename, file_url
- file_size, status
- upload_date

### DetectionResults
- id (UUID)
- image_id, user_id
- model_name (RegNetY320, VGG16)
- prediction (Cancer, Non-Cancer)
- confidence_score, processing_time

### Reports
- id (UUID)
- detection_result_id, user_id
- patient_name, patient_age
- clinical_notes, doctor_notes
- report_pdf_url

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts
python manage.py test apps.detection

# With coverage
coverage run manage.py test
coverage report
```

## Deployment

### Production Settings

1. Set `DEBUG=False` in `.env`
2. Update `ALLOWED_HOSTS`
3. Set secure `SECRET_KEY`
4. Enable HTTPS
5. Configure production database

### Deploy to Cloud

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Performance

- **Model Accuracy**: RegNetY320 - 89.4%, VGG16 - 73.7%
- **Image Processing**: < 10 seconds
- **Page Load Time**: < 2 seconds
- **Supported Users**: 100+ concurrent

## Security

- HTTPS encryption
- Password hashing (PBKDF2)
- CSRF protection
- SQL injection prevention
- XSS protection
- Role-based access control

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Authors

- **Arepalli CharmiSri** - Research Scholar
- **Balasubramani** - Research Guide

## Acknowledgments

- Saveetha School of Engineering
- Saveetha Institute of Medical and Technical Sciences
- Saveetha University, Chennai

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/oral_cancer/issues
- Email: 192124017.sse@saveetha.com

## Disclaimer

**IMPORTANT**: This system is for research and educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.

## Citation

If you use this work in research, please cite:

```
@article{charmisri2025oral,
  title={Binary Classification of detecting Oral Cancer using RegNetY320 Algorithm in Comparison with VGG16},
  author={CharmiSri, Arepalli and Balasubramani},
  journal={Research Paper},
  year={2025},
  institution={Saveetha University}
}
```

## Roadmap

- [ ] Multi-class classification
- [ ] Mobile app (iOS/Android)
- [ ] Real-time collaboration
- [ ] Telemedicine integration
- [ ] 3D image analysis
- [ ] Multi-language support

---

**Made with ❤️ for advancing oral cancer detection research**
