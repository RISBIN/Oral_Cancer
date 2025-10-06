# Supabase Setup Guide for OralCare AI

## Your Supabase Project Details

**Project URL**: https://cvsweqhdqqgggzsbbpgu.supabase.co
**Project ID**: cvsweqhdqqgggzsbbpgu
**Dashboard**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu

---

## Step 1: Set Up PostgreSQL Database

### 1.1 Get Database Connection String

1. Go to: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/settings/database
2. Scroll to **Connection String** section
3. Select **URI** format
4. Copy the connection string (looks like this):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.cvsweqhdqqgggzsbbpgu.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password

### 1.2 Update .env File

Update your `.env` file with the Supabase PostgreSQL connection:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.cvsweqhdqqgggzsbbpgu.supabase.co:5432/postgres
```

### 1.3 Run Migrations to Supabase

```bash
source venv/bin/activate
python manage.py migrate
```

This will create all tables in your Supabase PostgreSQL database!

---

## Step 2: Set Up Storage Bucket for Images

### 2.1 Create Storage Bucket

1. Go to: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets
2. Click **"New bucket"**
3. Enter bucket name: `oral-cancer-images`
4. Set **Public bucket**: ✅ YES (to allow public image access)
5. Click **"Create bucket"**

### 2.2 Set Bucket Policies (Important!)

After creating the bucket, set up storage policies:

1. Go to bucket settings (click on the bucket name)
2. Click **"Policies"** tab
3. Click **"New Policy"**

**Policy 1: Public Read Access**
```sql
CREATE POLICY "Public read access"
ON storage.objects FOR SELECT
USING (bucket_id = 'oral-cancer-images');
```

**Policy 2: Authenticated Upload**
```sql
CREATE POLICY "Authenticated users can upload"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'oral-cancer-images' AND auth.role() = 'authenticated');
```

**Policy 3: Users can update their own files**
```sql
CREATE POLICY "Users can update own files"
ON storage.objects FOR UPDATE
USING (bucket_id = 'oral-cancer-images' AND auth.uid() = owner)
WITH CHECK (bucket_id = 'oral-cancer-images');
```

---

## Step 3: Sync Django Users to Supabase Auth

### Option A: Manual Sync Script

Create a management command to sync existing Django users to Supabase Auth:

```python
# apps/accounts/management/commands/sync_users_to_supabase.py
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from config.supabase import get_supabase_admin_client

class Command(BaseCommand):
    def handle(self, *args, **options):
        supabase = get_supabase_admin_client()

        for user in User.objects.all():
            try:
                # Create user in Supabase Auth
                supabase.auth.admin.create_user({
                    "email": user.email,
                    "password": "change-me-123",  # Temporary password
                    "email_confirm": True,
                    "user_metadata": {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role,
                    }
                })
                print(f"✓ Synced: {user.email}")
            except Exception as e:
                print(f"✗ Error syncing {user.email}: {e}")
```

Run: `python manage.py sync_users_to_supabase`

### Option B: Automatic Sync on User Registration

Already implemented in your `register` view! Each new user is automatically saved to Django DB.

---

## Step 4: View Data in Supabase Dashboard

### 4.1 View Database Tables

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor

You'll see these tables after running migrations:
- `users` - All user accounts
- `user_activities` - User activity logs
- `images` - Uploaded images
- `detection_results` - AI detection results
- `reports` - Generated reports

### 4.2 View Storage Files

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets/oral-cancer-images

All uploaded images will appear here organized by:
- User ID
- Date (YYYY/MM/DD)
- Filename

### 4.3 View Authentication Users

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/auth/users

Note: Django users won't automatically appear here unless you:
- Enable Supabase Auth integration (Option A above)
- OR use Supabase Auth instead of Django Auth

---

## Step 5: Test Image Upload to Supabase Storage

### 5.1 Upload Test

1. Login to your app: http://localhost:8000/accounts/login/
2. Go to Upload: http://localhost:8000/detection/upload/
3. Upload an image
4. Check Supabase Storage dashboard - you should see the image!

### 5.2 Verify Storage URL

After upload, check the database:
```sql
SELECT filename, file_url FROM images ORDER BY upload_date DESC LIMIT 5;
```

The `file_url` should contain your Supabase Storage URL.

---

## Step 6: View Real-Time Data

### 6.1 Table Editor

Go to: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor

Here you can:
- View all table data in real-time
- Edit records directly
- Run SQL queries
- Export data as CSV

### 6.2 SQL Editor

Go to: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/sql/new

Run custom queries:

```sql
-- View all users
SELECT id, email, first_name, last_name, role, created_at
FROM users
ORDER BY created_at DESC;

-- View recent uploads
SELECT u.email, i.filename, i.upload_date, i.status
FROM images i
JOIN users u ON i.user_id = u.id
ORDER BY i.upload_date DESC
LIMIT 10;

-- Detection statistics
SELECT
  model_name,
  prediction,
  COUNT(*) as count,
  AVG(confidence_score) as avg_confidence
FROM detection_results
GROUP BY model_name, prediction;
```

---

## Troubleshooting

### Database Connection Issues

If you can't connect to Supabase PostgreSQL:

1. Check your database password in Supabase dashboard
2. Verify connection string format:
   ```
   postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
   ```
3. Make sure you have `psycopg2-binary` installed:
   ```bash
   pip install psycopg2-binary
   ```

### Storage Upload Issues

If images aren't uploading to Supabase:

1. Verify bucket exists and is public
2. Check bucket policies are set correctly
3. Verify `SUPABASE_KEY` in `.env` is correct
4. Check Django logs for Supabase errors

### Tables Not Appearing

If tables don't appear in Supabase dashboard:

1. Make sure you ran migrations with Supabase DATABASE_URL
2. Check if migrations were successful
3. Refresh the dashboard page

---

## Current Configuration Status

✅ Supabase credentials configured in `.env`
✅ Supabase client code ready (`config/supabase.py`)
✅ Image upload with Supabase Storage integrated
✅ Fallback to local storage if Supabase fails
⏳ **TODO**: Switch DATABASE_URL to Supabase PostgreSQL
⏳ **TODO**: Create storage bucket `oral-cancer-images`
⏳ **TODO**: Set up bucket policies

---

## Quick Commands

```bash
# Install Supabase dependencies
pip install supabase psycopg2-binary

# Run migrations to Supabase
python manage.py migrate

# Create new superuser
python manage.py createsuperuser

# Test Supabase connection
python -c "from config.supabase import get_supabase_client; print(get_supabase_client())"
```

---

## Important Links

🌐 **Supabase Dashboard**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu
📊 **Database Editor**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor
🗄️ **Storage**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets
🔐 **Auth Users**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/auth/users
⚙️ **Settings**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/settings/general

---

**Next Step**: Follow Step 1 to switch your database to Supabase PostgreSQL!
