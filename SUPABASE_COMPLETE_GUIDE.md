# 🎯 Complete Supabase Setup Guide - OralCare AI

## ✅ Current Status

**Supabase Connection**: ✅ WORKING
**Project URL**: https://cvsweqhdqqgggzsbbpgu.supabase.co
**Dashboard**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu

---

## 📋 Table of Contents

1. [View Your Supabase Data](#1-view-your-supabase-data)
2. [Storage Bucket Setup](#2-storage-bucket-setup)
3. [Database Migration](#3-database-migration-optional)
4. [View Users & Auth](#4-view-users--auth)
5. [Test Image Upload](#5-test-image-upload)

---

## 1. View Your Supabase Data

### 🗄️ Database Tables

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor

Currently using **SQLite locally**. To view data in Supabase, follow Step 3 to migrate.

After migration, you'll see:
- `users` - User accounts
- `user_activities` - Activity logs
- `images` - Uploaded images
- `detection_results` - AI results
- `reports` - Generated reports

### 📊 Run SQL Queries

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/sql/new

Example queries:
```sql
-- View all users
SELECT * FROM users ORDER BY created_at DESC;

-- View recent uploads
SELECT * FROM images ORDER BY upload_date DESC LIMIT 10;

-- Detection statistics
SELECT model_name, prediction, COUNT(*)
FROM detection_results
GROUP BY model_name, prediction;
```

---

## 2. Storage Bucket Setup

### Step-by-Step Instructions:

1. **Go to Storage Dashboard**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets

2. **Click "New bucket"**

3. **Enter Details:**
   - Bucket name: `oral-cancer-images`
   - Public bucket: ✅ **YES** (important!)
   - File size limit: 10MB (optional)

4. **Click "Create bucket"**

5. **Set Policies** (Click on bucket → Policies tab)

   Click **"New Policy"** and add these 3 policies:

   **Policy 1: Public Read**
   ```sql
   CREATE POLICY "Public read access"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'oral-cancer-images');
   ```

   **Policy 2: Authenticated Upload**
   ```sql
   CREATE POLICY "Authenticated upload"
   ON storage.objects FOR INSERT
   TO authenticated
   WITH CHECK (bucket_id = 'oral-cancer-images');
   ```

   **Policy 3: User Update Own Files**
   ```sql
   CREATE POLICY "Users update own files"
   ON storage.objects FOR UPDATE
   TO authenticated
   USING (bucket_id = 'oral-cancer-images');
   ```

✅ **Done!** Images will now upload to Supabase Storage.

---

## 3. Database Migration (Optional)

### Switch from SQLite to Supabase PostgreSQL

#### Step 1: Get Database Password

1. Go to: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/settings/database
2. Scroll to **Database Settings**
3. Click **"Reset Database Password"** (if you don't remember it)
4. Copy the new password

#### Step 2: Get Connection String

1. Still on the Database page
2. Scroll to **Connection String**
3. Select **URI** format
4. Copy the connection string (looks like this):
   ```
   postgresql://postgres.cvsweqhdqqgggzsbbpgu:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual password

#### Step 3: Update .env

Open `.env` file and update:

```env
DATABASE_URL=postgresql://postgres.cvsweqhdqqgggzsbbpgu:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

#### Step 4: Run Migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser  # Create admin again
```

✅ **Done!** Your database is now on Supabase!

#### Verify Migration

Check in Supabase:
https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor

You should see all tables appear!

---

## 4. View Users & Auth

### Current Setup

**Django is handling authentication** (not Supabase Auth).

### View Django Users in Database

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor

After migrating to Supabase PostgreSQL, you can view users:

```sql
SELECT id, email, username, first_name, last_name, role, created_at
FROM users
ORDER BY created_at DESC;
```

### Supabase Auth Users

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/auth/users

Note: Users registered through Django won't appear here unless you enable Supabase Auth integration.

**To sync Django users to Supabase Auth** (optional):

Create file `apps/accounts/management/commands/sync_to_supabase.py`:

```python
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from config.supabase import get_supabase_admin_client

class Command(BaseCommand):
    help = 'Sync Django users to Supabase Auth'

    def handle(self, *args, **options):
        supabase = get_supabase_admin_client()

        for user in User.objects.all():
            try:
                result = supabase.auth.admin.create_user({
                    "email": user.email,
                    "password": "ChangeMe123!",  # Temp password
                    "email_confirm": True,
                    "user_metadata": {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role,
                    }
                })
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Synced: {user.email}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error: {user.email} - {e}')
                )
```

Run: `python manage.py sync_to_supabase`

---

## 5. Test Image Upload

### Test Supabase Storage Integration

1. **Login to your app**

   http://localhost:8000/accounts/login/

   Use admin credentials:
   - Email: `admin@oralcare.ai`
   - Password: `admin123`

2. **Go to Upload Page**

   http://localhost:8000/detection/upload/

3. **Upload an Image**

   - Drag & drop or browse
   - Click "Upload & Process"

4. **Verify in Supabase Storage**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets/oral-cancer-images

   You should see your uploaded image organized by:
   - User ID
   - Date (YYYY/MM/DD)
   - Filename

5. **Check Database Record**

   Go to Table Editor and check `images` table:
   ```sql
   SELECT * FROM images ORDER BY upload_date DESC LIMIT 5;
   ```

   The `file_url` column should contain Supabase Storage URL.

---

## 📊 Supabase Dashboard Overview

### Main Sections:

1. **📋 Table Editor**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor

   View and edit all database tables

2. **🗄️ Storage**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets

   View uploaded files

3. **🔐 Authentication**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/auth/users

   View authenticated users (if using Supabase Auth)

4. **⚡ SQL Editor**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/sql/new

   Run custom SQL queries

5. **⚙️ Database Settings**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/settings/database

   Connection strings, password reset

6. **🔑 API Settings**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/settings/api

   View your API keys (already in .env)

---

## 🔍 Monitor Your Data

### Real-Time Queries

After migrating database, monitor your app data:

**Total Users:**
```sql
SELECT COUNT(*) as total_users FROM users;
```

**Users by Role:**
```sql
SELECT role, COUNT(*) as count
FROM users
GROUP BY role;
```

**Recent Uploads:**
```sql
SELECT u.email, i.filename, i.upload_date, i.status
FROM images i
JOIN users u ON i.user_id = u.id
ORDER BY i.upload_date DESC
LIMIT 20;
```

**Detection Statistics:**
```sql
SELECT
  model_name,
  prediction,
  COUNT(*) as count,
  AVG(confidence_score) as avg_confidence,
  MIN(confidence_score) as min_confidence,
  MAX(confidence_score) as max_confidence
FROM detection_results
GROUP BY model_name, prediction;
```

**Storage Usage:**
```sql
SELECT
  COUNT(*) as total_images,
  SUM(file_size) as total_size_bytes,
  SUM(file_size)/1024/1024 as total_size_mb
FROM images;
```

---

## 🚨 Troubleshooting

### Issue: Can't see tables in Supabase

**Solution**: Make sure you've migrated to Supabase PostgreSQL (Step 3)

### Issue: Image upload fails

**Solution**:
1. Check storage bucket exists: `oral-cancer-images`
2. Verify bucket is public
3. Check bucket policies are set
4. Verify `SUPABASE_KEY` in .env

### Issue: Database connection error

**Solution**:
1. Verify `DATABASE_URL` format is correct
2. Check database password is correct
3. Install: `pip install psycopg2-binary`

### Issue: Slow database queries

**Solution**:
1. Use connection pooling (already configured)
2. Add indexes to frequently queried columns
3. Use Supabase connection pooler (port 6543)

---

## 📱 Quick Reference

### Important Commands

```bash
# Test Supabase connection
python -c "from config.supabase import get_supabase_client; print(get_supabase_client())"

# Migrate to Supabase PostgreSQL
python manage.py migrate

# Create new admin
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Important URLs

- **App**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **Supabase Dashboard**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu

---

## ✨ What's Working Now

✅ Supabase credentials configured
✅ Supabase client connection working
✅ Image upload to Supabase Storage (after bucket setup)
✅ Fallback to local storage
⏳ Database migration (optional - follow Step 3)
⏳ Storage bucket creation (follow Step 2)

---

## 🎯 Next Steps

1. ✅ **Create Storage Bucket** (Step 2) - 5 minutes
2. 🔄 **Migrate Database** (Step 3) - Optional, 10 minutes
3. 🧪 **Test Upload** (Step 5) - 2 minutes
4. 📊 **Monitor Data** in Supabase Dashboard

---

**Need Help?**
Check SUPABASE_SETUP.md for detailed instructions or visit: https://supabase.com/docs
