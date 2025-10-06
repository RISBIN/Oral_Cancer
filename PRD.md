# Product Requirements Document (PRD)
## Oral Cancer Detection System using RegNetY320

---

## 1. Project Overview

### 1.1 Product Name
**OralCare AI - Oral Cancer Detection System**

### 1.2 Project Description
A web-based application that uses deep learning (RegNetY320 algorithm) to detect oral cancer from medical images. The system provides binary classification (Cancer/Non-Cancer) with high accuracy (89.4%) for early diagnosis and clinical decision support.

### 1.3 Target Users
- Healthcare professionals (Dentists, Oncologists, Pathologists)
- Medical students and researchers
- Diagnostic centers and hospitals

### 1.4 Core Technology Stack
- **Frontend**: Django Templates with HTML5, CSS3, JavaScript (Premium White UI)
- **Backend**: Django 5.x (Python)
- **Database**: PostgreSQL (Supabase Cloud)
- **ML Framework**: TensorFlow/Keras with RegNetY320
- **Authentication**: Django Authentication + Supabase Auth
- **Storage**: Supabase Storage (for medical images)
- **Deployment**: Cloud-ready architecture

---

## 2. Functional Requirements

### 2.1 User Authentication & Authorization

#### 2.1.1 User Registration
- Email-based registration
- Password strength validation
- Email verification (via Supabase)
- User roles: Admin, Doctor, Researcher, Student

#### 2.1.2 User Login
- Secure login with email/password
- Session management
- Remember me functionality
- Password reset via email

#### 2.1.3 User Profile
- Profile information (Name, Email, Role, Institution)
- Profile picture upload
- Account settings
- Change password

### 2.2 Image Upload & Management

#### 2.2.1 Image Upload
- Support formats: JPG, PNG, DICOM
- Max file size: 10MB
- Drag-and-drop interface
- Multiple image upload (batch processing)
- Image preview before upload

#### 2.2.2 Image Storage
- Secure storage in Supabase Storage
- Organized by user and date
- Image metadata (timestamp, user_id, filename)
- Automatic compression and optimization

#### 2.2.3 Image History
- View uploaded images history
- Filter by date, status, result
- Download original images
- Delete images

### 2.3 AI Detection System

#### 2.3.1 Model Integration
- RegNetY320 pre-trained model
- VGG16 comparison model
- Binary classification (Cancer/Non-Cancer)
- Confidence score percentage

#### 2.3.2 Detection Process
- Real-time image preprocessing
- Model inference
- Results display with confidence score
- Comparison between RegNetY320 and VGG16

#### 2.3.3 Results Management
- Save detection results to database
- Generate PDF reports
- Export results (CSV/Excel)
- Visualization (charts, graphs)

### 2.4 Dashboard & Analytics

#### 2.4.1 User Dashboard
- Total scans performed
- Detection statistics (Cancer/Non-Cancer ratio)
- Recent scans
- Model accuracy metrics

#### 2.4.2 Admin Dashboard
- Total users
- Total scans
- System performance metrics
- User activity logs

### 2.5 Reports & Export

#### 2.5.1 Detection Report
- Patient information (optional)
- Image details
- Detection results (RegNetY320 & VGG16)
- Confidence scores
- Timestamp
- Doctor's notes (optional)

#### 2.5.2 Export Options
- PDF report generation
- CSV/Excel export
- Image download with results

---

## 3. Non-Functional Requirements

### 3.1 Performance
- Image upload: < 5 seconds
- Model inference: < 10 seconds
- Page load time: < 2 seconds
- Support 100+ concurrent users

### 3.2 Security
- HTTPS encryption
- Password hashing (Django's PBKDF2)
- CSRF protection
- SQL injection prevention
- XSS protection
- Role-based access control (RBAC)
- Secure file upload validation

### 3.3 Scalability
- Cloud-based deployment
- Database connection pooling
- Caching (Redis/Memcached)
- CDN for static files

### 3.4 Reliability
- 99.5% uptime
- Automated backups (daily)
- Error logging and monitoring
- Graceful error handling

### 3.5 Usability
- Responsive design (mobile, tablet, desktop)
- Intuitive navigation
- Loading indicators
- Clear error messages
- Help documentation

---

## 4. UI/UX Design Requirements

### 4.1 Design Theme
**Premium White Medical UI**

### 4.2 Color Palette
```
Primary: #FFFFFF (White)
Secondary: #F8F9FA (Light Gray)
Accent: #4A90E2 (Medical Blue)
Success: #28A745 (Green)
Warning: #FFC107 (Amber)
Danger: #DC3545 (Red)
Text Primary: #2C3E50 (Dark Gray)
Text Secondary: #6C757D (Medium Gray)
```

### 4.3 Typography
- Primary Font: Inter / Poppins (Modern, Clean)
- Heading: 600-700 weight
- Body: 400-500 weight
- Font sizes: 14px (body), 16px-32px (headings)

### 4.4 Design Elements
- Clean white cards with subtle shadows
- Smooth transitions and animations
- Minimalist icons (Feather Icons / Font Awesome)
- Ample whitespace
- Professional medical imagery
- Blue accent for CTAs (Call-to-Actions)

### 4.5 Key Pages Design

#### 4.5.1 Landing Page
- Hero section with product overview
- Features section
- How it works (3-step process)
- Statistics/Metrics
- CTA buttons (Get Started, Learn More)
- Footer with links

#### 4.5.2 Login/Registration
- Centered card design
- Clean form fields
- Social login options (optional)
- Forgot password link
- Background: Subtle medical pattern

#### 4.5.3 Dashboard
- Sidebar navigation (collapsible)
- Top navbar with user profile
- Grid layout for stats cards
- Charts and graphs
- Recent activity feed

#### 4.5.4 Upload Page
- Large drag-drop zone
- Upload progress bar
- Image preview grid
- Batch upload support
- Clear instructions

#### 4.5.5 Results Page
- Split view: Image on left, Results on right
- Confidence meter (circular progress)
- Color-coded results (Green/Red)
- Download/Export buttons
- Comparison table (RegNetY320 vs VGG16)

---

## 5. Database Schema (PostgreSQL - Supabase)

### 5.1 Tables

#### Users
```sql
- id (UUID, Primary Key)
- email (VARCHAR, Unique)
- password_hash (VARCHAR)
- full_name (VARCHAR)
- role (ENUM: admin, doctor, researcher, student)
- institution (VARCHAR)
- profile_picture_url (VARCHAR)
- is_verified (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### Images
```sql
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key -> Users)
- filename (VARCHAR)
- file_url (VARCHAR)
- file_size (INTEGER)
- upload_date (TIMESTAMP)
- status (ENUM: pending, processed, failed)
```

#### DetectionResults
```sql
- id (UUID, Primary Key)
- image_id (UUID, Foreign Key -> Images)
- user_id (UUID, Foreign Key -> Users)
- model_name (VARCHAR: RegNetY320, VGG16)
- prediction (VARCHAR: Cancer, Non-Cancer)
- confidence_score (FLOAT)
- processing_time (FLOAT)
- created_at (TIMESTAMP)
```

#### Reports
```sql
- id (UUID, Primary Key)
- detection_result_id (UUID, Foreign Key)
- user_id (UUID, Foreign Key -> Users)
- patient_name (VARCHAR, Optional)
- patient_age (INTEGER, Optional)
- notes (TEXT)
- report_pdf_url (VARCHAR)
- created_at (TIMESTAMP)
```

#### AuditLogs
```sql
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key -> Users)
- action (VARCHAR)
- ip_address (VARCHAR)
- timestamp (TIMESTAMP)
```

---

## 6. Technical Architecture

### 6.1 System Architecture
```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django Frontend│
│   (Templates)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django Backend │
│   (Views/APIs)  │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌──────────┐ ┌────────┐
│Supabase│ │ML     │ │Supabase  │ │Django  │
│ Auth   │ │Model  │ │Storage   │ │ ORM    │
└────────┘ └──────┘ └──────────┘ └────┬───┘
                                       ▼
                                  ┌──────────┐
                                  │PostgreSQL│
                                  │(Supabase)│
                                  └──────────┘
```

### 6.2 Project Structure
```
oral_cancer/
├── manage.py
├── requirements.txt
├── .env
├── README.md
├── PRD.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── detection/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── ml_models.py
│   │   ├── utils.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── dashboard/
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   └── reports/
│       ├── models.py
│       ├── views.py
│       ├── pdf_generator.py
│       ├── urls.py
│       └── templates/
├── ml_models/
│   ├── regnet_y320.h5
│   ├── vgg16.h5
│   └── preprocessing.py
├── static/
│   ├── css/
│   │   ├── main.css
│   │   ├── dashboard.css
│   │   └── components.css
│   ├── js/
│   │   ├── main.js
│   │   ├── upload.js
│   │   └── charts.js
│   └── images/
├── media/
│   └── uploads/
└── templates/
    ├── base.html
    ├── landing.html
    ├── login.html
    └── components/
```

---

## 7. API Endpoints (Django Views)

### 7.1 Authentication
- `POST /accounts/register/` - User registration
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `POST /accounts/password-reset/` - Password reset
- `GET /accounts/profile/` - View profile
- `PUT /accounts/profile/update/` - Update profile

### 7.2 Detection
- `GET /detection/upload/` - Upload page
- `POST /detection/upload/` - Upload image
- `POST /detection/process/` - Process image
- `GET /detection/results/<id>/` - View results
- `GET /detection/history/` - View history
- `DELETE /detection/delete/<id>/` - Delete detection

### 7.3 Dashboard
- `GET /dashboard/` - Main dashboard
- `GET /dashboard/stats/` - Get statistics
- `GET /dashboard/recent/` - Recent activity

### 7.4 Reports
- `GET /reports/generate/<id>/` - Generate PDF
- `GET /reports/download/<id>/` - Download report
- `POST /reports/export/` - Export data

---

## 8. Development Phases

### Phase 1: Setup & Foundation (Week 1-2)
- [ ] Project initialization
- [ ] Django setup
- [ ] Supabase configuration
- [ ] Database schema creation
- [ ] Authentication system
- [ ] Base templates and UI framework

### Phase 2: Core Features (Week 3-4)
- [ ] Image upload functionality
- [ ] Supabase Storage integration
- [ ] ML model integration (RegNetY320)
- [ ] Detection processing pipeline
- [ ] Results display

### Phase 3: Dashboard & Analytics (Week 5)
- [ ] User dashboard
- [ ] Admin dashboard
- [ ] Statistics and charts
- [ ] History management

### Phase 4: Reports & Export (Week 6)
- [ ] PDF report generation
- [ ] Export functionality
- [ ] Email notifications

### Phase 5: Testing & Deployment (Week 7-8)
- [ ] Unit testing
- [ ] Integration testing
- [ ] Security audit
- [ ] Performance optimization
- [ ] Deployment

---

## 9. Success Metrics

### 9.1 Technical Metrics
- Model accuracy: > 89% (RegNetY320)
- Image processing time: < 10 seconds
- Page load time: < 2 seconds
- Uptime: > 99.5%

### 9.2 User Metrics
- User registration rate
- Daily active users
- Images processed per day
- User satisfaction score

### 9.3 Business Metrics
- Detection accuracy feedback
- Clinical adoption rate
- User retention rate

---

## 10. Risk & Mitigation

### 10.1 Technical Risks
- **Risk**: Model accuracy issues
  - **Mitigation**: Continuous model training, validation dataset
- **Risk**: Scalability issues
  - **Mitigation**: Cloud infrastructure, load balancing
- **Risk**: Data security breach
  - **Mitigation**: Encryption, security audits, compliance

### 10.2 User Risks
- **Risk**: Low adoption
  - **Mitigation**: User training, documentation, demo videos
- **Risk**: Misinterpretation of results
  - **Mitigation**: Clear disclaimers, doctor verification required

---

## 11. Future Enhancements

### 11.1 Phase 2 Features
- Multi-class classification (different cancer types)
- Real-time collaboration
- Mobile app (iOS/Android)
- AI-powered recommendations
- Integration with hospital systems

### 11.2 Phase 3 Features
- Telemedicine integration
- 3D image analysis
- Predictive analytics
- Multi-language support

---

## 12. Compliance & Legal

### 12.1 Medical Compliance
- Disclaimer: "Not a substitute for professional medical advice"
- HIPAA compliance (if applicable)
- Data privacy regulations (GDPR)

### 12.2 Terms & Conditions
- User agreement
- Privacy policy
- Cookie policy
- Data retention policy

---

## 13. Documentation

### 13.1 Technical Documentation
- API documentation
- Database schema
- Deployment guide
- Development setup guide

### 13.2 User Documentation
- User manual
- FAQ
- Video tutorials
- Troubleshooting guide

---

## 14. Support & Maintenance

### 14.1 Support Channels
- Email support
- Documentation portal
- Issue tracker

### 14.2 Maintenance
- Regular updates
- Security patches
- Performance monitoring
- Backup and recovery

---

**Document Version**: 1.0
**Last Updated**: 2025-10-03
**Author**: Development Team
**Status**: Approved
