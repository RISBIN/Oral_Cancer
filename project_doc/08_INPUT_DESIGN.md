# 4.3 INPUT DESIGN

Input design focuses on creating user interfaces that efficiently and accurately capture data from users while minimizing errors, supporting user productivity, and providing clear feedback. For the OralCare AI system, input design encompasses forms for user registration and authentication, image upload interfaces, report generation forms, and administrative data entry screens.

## User Registration Form

The registration form captures information needed to create new user accounts.

### Form Fields

| Field Name | Type | Required | Validation | Description |
|------------|------|----------|------------|-------------|
| First Name | Text | Yes | Max 150 chars | User's given name |
| Last Name | Text | Yes | Max 150 chars | User's family name |
| Email | Email | Yes | Valid email format, unique | Primary identifier |
| Username | Text | Yes | Max 150 chars, unique | Login identifier |
| Password | Password | Yes | Min 8 chars, complexity rules | Account credential |
| Confirm Password | Password | Yes | Must match password | Verification field |
| Role | Dropdown | Yes | admin/doctor/researcher/student | User type |
| Institution | Text | No | Max 255 chars | Affiliated organization |
| Phone Number | Tel | No | Valid phone format | Contact number |

### Design Features

**Progressive Disclosure:**
- Basic fields shown initially
- Advanced fields (bio, phone) appear after core fields completed
- Reduces visual complexity and cognitive load

**Inline Validation:**
- Real-time feedback as users complete each field
- Email uniqueness checked via AJAX before submission
- Password strength indicator (weak/medium/strong)
- Clear error messages guide correction

**User Experience Enhancements:**
- Auto-capitalization of name fields
- Email becomes suggested username
- Tab navigation between fields
- Enter key submits form
- Mobile-optimized input types (email, tel)

**Security Features:**
- Password requirements displayed
- CSRF token protection
- Rate limiting on submissions
- Captcha for public access (optional)

---

## Login Form

Simple authentication form with security features.

### Form Fields

| Field Name | Type | Required | Validation | Description |
|------------|------|----------|------------|-------------|
| Email/Username | Text | Yes | Non-empty | Login identifier |
| Password | Password | Yes | Non-empty | Account credential |
| Remember Me | Checkbox | No | - | Extend session duration |

### Design Features

**Usability:**
- Accepts both email and username
- "Forgot Password?" link prominently placed
- "Sign Up" link for new users
- Redirect to intended page after login

**Security:**
- Generic error messages (don't reveal if email/password wrong)
- Rate limiting after failed attempts
- Account lockout after 5 failed attempts
- HTTPS enforced
- CSRF protection

**Accessibility:**
- Clear labels and placeholders
- Keyboard navigation support
- Screen reader compatible
- High contrast error messages

---

## Image Upload Interface

Drag-and-drop interface for uploading oral lesion images.

### Upload Methods

1. **Drag-and-Drop Zone**
   - Large visual target area
   - Hover effect when file dragged over
   - Multiple file support

2. **Click to Browse**
   - Traditional file selection dialog
   - File filter: .jpg, .jpeg, .png only

3. **Camera Capture** (Mobile)
   - Direct camera integration
   - Real-time preview

### Design Features

**Visual Feedback:**
```
┌─────────────────────────────────────┐
│                                     │
│         📷  Drag & Drop            │
│      or Click to Upload Image       │
│                                     │
│   Supported: JPG, PNG (Max 10MB)   │
│                                     │
└─────────────────────────────────────┘
```

**File Validation:**
- Type validation: Only JPEG, PNG accepted
- Size validation: Max 10MB enforced
- Dimension validation: Min 224x224 pixels
- Instant feedback on rejection

**Upload Progress:**
- Progress bar during upload
- Percentage indicator
- Cancel button
- Success/error notifications

**Image Preview:**
- Thumbnail display after upload
- Zoom capability
- Remove/replace options
- EXIF data display (optional)

**Metadata Entry:**
| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| Lesion Location | Dropdown | No | Tongue, Palate, Gingiva, etc. |
| Patient ID | Text | No | Anonymous identifier |
| Clinical Notes | Textarea | No | Observations |

---

## Report Generation Form

Form for creating PDF reports from detection results.

### Form Fields

| Field Name | Type | Required | Max Length | Description |
|------------|------|----------|------------|-------------|
| Patient Name | Text | No | 255 | Patient identifier (optional) |
| Patient Age | Number | No | 0-150 | Demographics |
| Patient Gender | Dropdown | No | - | Male/Female/Other/Prefer not to say |
| Medical Record Number | Text | No | 100 | Hospital MRN |
| Clinical Notes | Textarea | No | 5000 | Provider observations |
| Include Model Comparison | Checkbox | Yes | - | Show both RegNetY320 & VGG16 |
| Include Images | Checkbox | Yes | - | Embed lesion photo |

### Design Features

**Layout:**
- Single column on mobile
- Two columns on desktop
- Logical field grouping
- Clear section headers

**User Assistance:**
- Character count on textarea
- Helpful placeholders with examples
- Tooltips on hover
- Preview button before generation

**Data Handling:**
- Auto-save to prevent data loss
- Session storage for draft reports
- Confirmation before navigation away
- Loading indicator during PDF generation

---

## Form Validation Strategy

### Client-Side Validation

**HTML5 Attributes:**
```html
<input type="email" required pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$">
<input type="number" min="0" max="150">
<input type="text" maxlength="255">
```

**JavaScript Validation:**
- Password strength checking
- Email format validation
- Cross-field validation (password match)
- Real-time feedback

**Visual Indicators:**
```
✓ Valid field   (green border, checkmark)
✗ Invalid field (red border, error icon)
⚠ Warning       (yellow border, warning icon)
```

### Server-Side Validation

**Django Form Validation:**
```python
def clean_email(self):
    email = self.cleaned_data['email']
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already exists")
    return email

def clean_password(self):
    password = self.cleaned_data['password']
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    return password
```

**Validation Layers:**
1. HTML5 browser validation
2. JavaScript client-side validation
3. Django form validation
4. Model validation
5. Database constraints

### Error Display

**Field-Level Errors:**
```
┌─────────────────────────────────┐
│ Email: [user@example        ]  │
│ ✗ This email is already taken  │
└─────────────────────────────────┘
```

**Form-Level Errors:**
```
╔═════════════════════════════════╗
║ ⚠ Please correct the following:║
║ • Email is already registered   ║
║ • Password is too weak          ║
╚═════════════════════════════════╝
```

**Success Messages:**
```
╔═════════════════════════════════╗
║ ✓ Registration successful!      ║
║   Please check your email.      ║
╚═════════════════════════════════╝
```

---

## Input Security Measures

### CSRF Protection
```python
<form method="POST">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### SQL Injection Prevention
- Parameterized queries via Django ORM
- No raw SQL with user input
- Input sanitization

### XSS Prevention
- Automatic template escaping
- Content Security Policy headers
- Input sanitization for rich text

### File Upload Security
- File type validation (whitelist)
- File size limits
- Virus scanning (optional)
- Sandboxed storage
- Filename sanitization

### Rate Limiting
```python
@ratelimit(key='ip', rate='5/m')
def login_view(request):
    # Login logic
```

---

## Accessibility Features

**WCAG 2.1 Compliance:**
- Semantic HTML5 elements
- ARIA labels and roles
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus indicators

**Form Labels:**
```html
<label for="email">Email Address *</label>
<input id="email" type="email" required
       aria-required="true"
       aria-describedby="email-help">
<small id="email-help">We'll never share your email</small>
```

**Error Announcements:**
```html
<div role="alert" aria-live="assertive">
    Please correct the errors in the form
</div>
```

---

## Mobile Optimization

**Responsive Design:**
- Touch-friendly tap targets (min 44x44px)
- Optimized for portrait orientation
- Minimal text input required
- Auto-zoom disabled on input focus

**Input Types:**
```html
<input type="email">      <!-- Email keyboard -->
<input type="tel">        <!-- Phone keyboard -->
<input type="number">     <!-- Numeric keyboard -->
<input type="date">       <!-- Date picker -->
```

**File Upload on Mobile:**
- Camera access for direct capture
- Photo library access
- Reduced file size requirements
- Preview before upload

The input design ensures efficient data capture while maintaining security, accessibility, and excellent user experience across all devices and user skill levels.

