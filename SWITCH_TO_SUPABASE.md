# 🚀 Switch to Supabase PostgreSQL Database

## Current Setup

✅ **Local PostgreSQL**: Currently using `localhost:5432/oral_cancer`
✅ **Supabase Keys**: Already configured in `.env`

## Switch to Supabase Database (10 minutes)

### Step 1: Get Supabase Database Password

1. **Go to Supabase Dashboard**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/settings/database

2. **Find Database Settings Section**

3. **Reset Database Password** (if you don't remember it)
   - Click "Reset Database Password"
   - Copy the new password (save it securely!)

### Step 2: Get Connection String

1. **On the same page**, scroll to **Connection String**

2. **Select "URI" format**

3. **Copy the connection string** (will look like this):
   ```
   postgresql://postgres.cvsweqhdqqgggzsbbpgu:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```

4. **Replace `[YOUR-PASSWORD]`** with your actual password

### Step 3: Update .env File

Open `.env` and update the DATABASE_URL:

```env
# Current (Local PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/oral_cancer

# Change to (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres.cvsweqhdqqgggzsbbpgu:YOUR_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

### Step 4: Run Migrations to Supabase

```bash
source venv/bin/activate
python manage.py migrate
```

This will create all tables in Supabase!

### Step 5: Create Admin User in Supabase

```bash
python manage.py createsuperuser
```

Or create programmatically:

```bash
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.accounts.models import User
User.objects.create_superuser(
    username='admin',
    email='admin@oralcare.ai',
    password='admin123',
    first_name='Admin',
    last_name='User'
)
print('✅ Admin created in Supabase!')
"
```

### Step 6: Restart Server

```bash
# Stop current server (Ctrl+C)
# Start again
python manage.py runserver
```

## View Data in Supabase

### 📊 Table Editor

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor

After migration, you'll see all tables:
- `users`
- `user_activities`
- `images`
- `detection_results`
- `reports`
- And Django tables

### 🔍 SQL Editor

**URL**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/sql/new

Run queries:

```sql
-- View all users
SELECT id, email, username, first_name, last_name, role, created_at
FROM users
ORDER BY created_at DESC;

-- View uploaded images
SELECT u.email, i.filename, i.upload_date, i.status
FROM images i
JOIN users u ON i.user_id = u.id
ORDER BY i.upload_date DESC;

-- Detection statistics
SELECT
  model_name,
  prediction,
  COUNT(*) as count,
  AVG(confidence_score) as avg_confidence
FROM detection_results
GROUP BY model_name, prediction;

-- Total counts
SELECT
  (SELECT COUNT(*) FROM users) as total_users,
  (SELECT COUNT(*) FROM images) as total_images,
  (SELECT COUNT(*) FROM detection_results) as total_results;
```

## Storage Bucket Setup (For Images)

### Create Bucket

1. **Go to Storage**

   https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets

2. **Click "New bucket"**

3. **Configuration:**
   - Name: `oral-cancer-images`
   - Public: ✅ **YES**
   - File size limit: 10 MB

4. **Click "Create bucket"**

### Set Bucket Policies

After creating bucket, add these policies:

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

**Policy 3: User Update**
```sql
CREATE POLICY "Users update own files"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'oral-cancer-images');
```

## Compare: Local vs Supabase

### Local PostgreSQL (Current)
✅ Fast (localhost)
✅ No internet needed
✅ Full control
❌ Not accessible remotely
❌ Manual backups

### Supabase PostgreSQL
✅ Cloud-based (accessible anywhere)
✅ Automatic backups
✅ Built-in dashboard
✅ Real-time features
✅ Storage included
❌ Requires internet
❌ Slight network latency

## Migration Status Checklist

### Before Switching:
- [ ] Get Supabase database password
- [ ] Get connection string
- [ ] Backup local data (optional)

### During Switch:
- [ ] Update DATABASE_URL in .env
- [ ] Run migrations
- [ ] Create admin user
- [ ] Restart server

### After Switch:
- [ ] Verify tables in Supabase dashboard
- [ ] Test login
- [ ] Test image upload
- [ ] Create storage bucket
- [ ] Test storage upload

## Quick Commands

### Test Supabase Connection
```bash
python -c "from config.supabase import get_supabase_client; print('✅ Connected!' if get_supabase_client() else '❌ Failed')"
```

### View Database
```bash
# Local PostgreSQL
psql -U postgres -d oral_cancer

# Supabase PostgreSQL (use Supabase Dashboard)
# https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor
```

### Migrate Data from Local to Supabase (Optional)
```bash
# Export from local
pg_dump -U postgres oral_cancer > backup.sql

# Import to Supabase (use connection string)
psql "postgresql://postgres.cvsweqhdqqgggzsbbpgu:PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres" < backup.sql
```

## Troubleshooting

### Can't connect to Supabase
- Check password is correct
- Verify connection string format
- Check internet connection
- Verify project is not paused

### Tables not appearing
- Make sure you ran `python manage.py migrate`
- Refresh Supabase dashboard
- Check if migrations succeeded

### Storage upload fails
- Verify bucket exists and is public
- Check bucket policies are set
- Verify SUPABASE_KEY in .env

## Important Links

🌐 **Dashboard**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu
📊 **Table Editor**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/editor
🗄️ **Storage**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets
⚙️ **Database Settings**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/settings/database
⚡ **SQL Editor**: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/sql/new

---

**Current Status:**
- ✅ Supabase credentials configured
- ✅ Local PostgreSQL working
- ⏳ Supabase database migration (follow steps above)
- ⏳ Storage bucket creation (follow steps above)

**Next:** Follow Step 1 to get your Supabase database password and switch!
