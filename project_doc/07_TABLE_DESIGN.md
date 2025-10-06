# 4.2 TABLE DESIGN

The OralCare AI database schema consists of interconnected tables representing users, images, detection results, reports, and system activity. Each table is carefully designed with appropriate data types, constraints, and relationships that enforce business rules at the database level while supporting efficient querying and data integrity.

## Users Table

The Users table extends Django's AbstractUser model with additional fields specific to the healthcare context.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for each user |
| username | VARCHAR(150) | UNIQUE, NOT NULL | Login username |
| email | VARCHAR(254) | UNIQUE, NOT NULL | User email address (used for login) |
| password | VARCHAR(128) | NOT NULL | Hashed password (PBKDF2) |
| first_name | VARCHAR(150) | NOT NULL | User's first name |
| last_name | VARCHAR(150) | NOT NULL | User's last name |
| role | VARCHAR(20) | NOT NULL, CHECK | User role: admin, doctor, researcher, student |
| institution | VARCHAR(255) | NULL | Affiliated institution/hospital |
| phone_number | VARCHAR(20) | NULL | Contact phone number |
| bio | TEXT | NULL | User biography/description |
| profile_picture_url | TEXT | NULL | URL to profile picture |
| is_verified | BOOLEAN | DEFAULT FALSE | Email verification status |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| is_staff | BOOLEAN | DEFAULT FALSE | Staff access permission |
| is_superuser | BOOLEAN | DEFAULT FALSE | Superuser permission |
| date_joined | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| last_login | TIMESTAMP | NULL | Last login timestamp |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Record update timestamp |

**Indexes:**
- `idx_users_email` on `email`
- `idx_users_role` on `role`
- `idx_users_institution` on `institution`

**Constraints:**
- `CHECK (role IN ('admin', 'doctor', 'researcher', 'student'))`

---

## Images Table

The Images table stores metadata about uploaded oral lesion photographs.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for each image |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to user who uploaded |
| filename | VARCHAR(255) | NOT NULL | Original filename |
| file_url | TEXT | NULL | Supabase Storage public URL |
| file_path | VARCHAR(500) | NULL | Storage path/key |
| file_size | INTEGER | NULL | File size in bytes |
| status | VARCHAR(20) | NOT NULL, CHECK | Processing status |
| upload_date | TIMESTAMP | DEFAULT NOW() | Upload timestamp |
| processed_date | TIMESTAMP | NULL | Processing completion timestamp |
| notes | TEXT | NULL | User notes about the image |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Record update timestamp |

**Indexes:**
- `idx_images_user_id` on `user_id`
- `idx_images_status` on `status`
- `idx_images_upload_date` on `upload_date DESC`

**Foreign Keys:**
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Constraints:**
- `CHECK (status IN ('pending', 'processing', 'processed', 'failed'))`
- `CHECK (file_size > 0)`

---

## Detection Results Table

The DetectionResults table stores AI model predictions for uploaded images.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for each detection result |
| image_id | UUID | FOREIGN KEY, NOT NULL | Reference to analyzed image |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to user who ran detection |
| model_name | VARCHAR(50) | NOT NULL, CHECK | AI model used: RegNetY320 or VGG16 |
| prediction | VARCHAR(20) | NOT NULL, CHECK | Classification result |
| confidence_score | DECIMAL(5,4) | NOT NULL, CHECK | Confidence score (0.0000-1.0000) |
| processing_time | DECIMAL(10,6) | NULL | Inference time in seconds |
| model_version | VARCHAR(50) | NULL | Model version identifier |
| created_at | TIMESTAMP | DEFAULT NOW() | Prediction timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Record update timestamp |

**Indexes:**
- `idx_detection_results_image_id` on `image_id`
- `idx_detection_results_user_id` on `user_id`
- `idx_detection_results_model_name` on `model_name`
- `idx_detection_results_prediction` on `prediction`
- `idx_detection_results_created_at` on `created_at DESC`

**Foreign Keys:**
- `image_id` REFERENCES `images(id)` ON DELETE CASCADE
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Constraints:**
- `CHECK (model_name IN ('RegNetY320', 'VGG16'))`
- `CHECK (prediction IN ('Cancer', 'Non-Cancer'))`
- `CHECK (confidence_score >= 0 AND confidence_score <= 1)`
- `CHECK (processing_time >= 0)`

---

## Reports Table

The Reports table stores generated PDF reports for detection results.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for each report |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to user who generated report |
| detection_result_id | UUID | FOREIGN KEY, NULL | Reference to detection result |
| patient_name | VARCHAR(255) | NULL | Patient name (optional for privacy) |
| patient_age | INTEGER | NULL, CHECK | Patient age |
| patient_gender | VARCHAR(20) | NULL | Patient gender |
| medical_record_number | VARCHAR(100) | NULL | Hospital/clinic MRN |
| clinical_notes | TEXT | NULL | Provider's clinical observations |
| report_pdf_url | TEXT | NULL | Supabase Storage URL for PDF |
| report_pdf_path | VARCHAR(500) | NULL | Storage path/key for PDF |
| generated_date | TIMESTAMP | DEFAULT NOW() | Report generation timestamp |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Record update timestamp |

**Indexes:**
- `idx_reports_user_id` on `user_id`
- `idx_reports_detection_result_id` on `detection_result_id`
- `idx_reports_generated_date` on `generated_date DESC`
- `idx_reports_patient_name` on `patient_name`

**Foreign Keys:**
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE
- `detection_result_id` REFERENCES `detection_results(id)` ON DELETE SET NULL

**Constraints:**
- `CHECK (patient_age >= 0 AND patient_age <= 150)`

---

## User Activities Table

The UserActivity table provides audit logging for security and compliance.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for each activity |
| user_id | UUID | FOREIGN KEY, NULL | Reference to user (null if deleted) |
| activity_type | VARCHAR(50) | NOT NULL | Type of activity |
| description | TEXT | NULL | Detailed activity description |
| ip_address | VARCHAR(45) | NULL | User's IP address (IPv4/IPv6) |
| user_agent | TEXT | NULL | Browser/device information |
| timestamp | TIMESTAMP | DEFAULT NOW() | Activity occurrence time |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `idx_user_activities_user_id` on `user_id`
- `idx_user_activities_timestamp` on `timestamp DESC`
- `idx_user_activities_activity_type` on `activity_type`

**Foreign Keys:**
- `user_id` REFERENCES `users(id)` ON DELETE SET NULL

---

## Table Relationships Summary

```
users (1) ────── (∞) images
  │                    │
  │                    │
  └─── (∞) detection_results (∞) ───┘
         │
         │
         └─── (∞) reports

users (1) ────── (∞) user_activities
```

**Relationship Details:**

1. **Users → Images** (One-to-Many)
   - One user can upload many images
   - CASCADE delete: When user deleted, all their images are deleted

2. **Images → Detection Results** (One-to-Many)
   - One image can have multiple detection results (from different models)
   - CASCADE delete: When image deleted, all its detection results are deleted

3. **Users → Detection Results** (One-to-Many)
   - One user can have many detection results
   - CASCADE delete: When user deleted, all their detection results are deleted

4. **Detection Results → Reports** (One-to-Many)
   - One detection result can be referenced in multiple reports
   - SET NULL on delete: When detection result deleted, report remains but reference is nullified

5. **Users → Reports** (One-to-Many)
   - One user can generate many reports
   - CASCADE delete: When user deleted, all their reports are deleted

6. **Users → User Activities** (One-to-Many)
   - One user can have many activity logs
   - SET NULL on delete: When user deleted, activity logs remain for audit purposes

---

## SQL Table Creation Scripts

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'doctor', 'researcher', 'student')),
    institution VARCHAR(255),
    phone_number VARCHAR(20),
    bio TEXT,
    profile_picture_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_institution ON users(institution);
```

### Images Table
```sql
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_url TEXT,
    file_path VARCHAR(500),
    file_size INTEGER CHECK (file_size > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'processed', 'failed')),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_images_user_id ON images(user_id);
CREATE INDEX idx_images_status ON images(status);
CREATE INDEX idx_images_upload_date ON images(upload_date DESC);
```

### Detection Results Table
```sql
CREATE TABLE detection_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_name VARCHAR(50) NOT NULL CHECK (model_name IN ('RegNetY320', 'VGG16')),
    prediction VARCHAR(20) NOT NULL CHECK (prediction IN ('Cancer', 'Non-Cancer')),
    confidence_score DECIMAL(5,4) NOT NULL
        CHECK (confidence_score >= 0 AND confidence_score <= 1),
    processing_time DECIMAL(10,6) CHECK (processing_time >= 0),
    model_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_detection_results_image_id ON detection_results(image_id);
CREATE INDEX idx_detection_results_user_id ON detection_results(user_id);
CREATE INDEX idx_detection_results_model_name ON detection_results(model_name);
CREATE INDEX idx_detection_results_prediction ON detection_results(prediction);
CREATE INDEX idx_detection_results_created_at ON detection_results(created_at DESC);
```

### Reports Table
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    detection_result_id UUID REFERENCES detection_results(id) ON DELETE SET NULL,
    patient_name VARCHAR(255),
    patient_age INTEGER CHECK (patient_age >= 0 AND patient_age <= 150),
    patient_gender VARCHAR(20),
    medical_record_number VARCHAR(100),
    clinical_notes TEXT,
    report_pdf_url TEXT,
    report_pdf_path VARCHAR(500),
    generated_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_detection_result_id ON reports(detection_result_id);
CREATE INDEX idx_reports_generated_date ON reports(generated_date DESC);
CREATE INDEX idx_reports_patient_name ON reports(patient_name);
```

### User Activities Table
```sql
CREATE TABLE user_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    activity_type VARCHAR(50) NOT NULL,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_activities_user_id ON user_activities(user_id);
CREATE INDEX idx_user_activities_timestamp ON user_activities(timestamp DESC);
CREATE INDEX idx_user_activities_activity_type ON user_activities(activity_type);
```

