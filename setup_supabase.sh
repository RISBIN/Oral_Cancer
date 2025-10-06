#!/bin/bash

# OralCare AI - Supabase Setup Script

echo "🚀 OralCare AI - Supabase Configuration"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Checking Supabase Configuration...${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# Check Supabase credentials
SUPABASE_URL=$(grep SUPABASE_URL .env | cut -d '=' -f2)
SUPABASE_KEY=$(grep SUPABASE_KEY .env | cut -d '=' -f2)

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo -e "${RED}❌ Supabase credentials not found in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Supabase credentials found${NC}"
echo "   URL: $SUPABASE_URL"
echo ""

# Activate virtual environment
echo -e "${BLUE}Step 2: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Install required packages
echo -e "${BLUE}Step 3: Installing Supabase packages...${NC}"
pip install supabase psycopg2-binary -q
echo -e "${GREEN}✅ Packages installed${NC}"
echo ""

# Test Supabase connection
echo -e "${BLUE}Step 4: Testing Supabase connection...${NC}"
python3 << EOF
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from config.supabase import get_supabase_client

try:
    client = get_supabase_client()
    if client:
        print("✅ Supabase connection successful!")
    else:
        print("❌ Failed to connect to Supabase")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
echo ""

# Prompt for database migration
echo -e "${YELLOW}⚠️  IMPORTANT: Database Migration${NC}"
echo ""
echo "To use Supabase PostgreSQL database:"
echo "1. Go to: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/settings/database"
echo "2. Copy your PostgreSQL connection string"
echo "3. Update DATABASE_URL in .env file"
echo "4. Run: python manage.py migrate"
echo ""

# Create storage bucket instructions
echo -e "${YELLOW}📦 Storage Bucket Setup${NC}"
echo ""
echo "To enable image uploads to Supabase Storage:"
echo "1. Go to: https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu/storage/buckets"
echo "2. Click 'New bucket'"
echo "3. Bucket name: oral-cancer-images"
echo "4. Make it public: ✅ YES"
echo "5. Create the bucket"
echo ""

echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Create storage bucket (see instructions above)"
echo "2. (Optional) Switch to Supabase PostgreSQL database"
echo "3. Upload an image to test: http://localhost:8000/detection/upload/"
echo ""
echo "View your Supabase dashboard:"
echo "🔗 https://supabase.com/dashboard/project/cvsweqhdqqgggzsbbpgu"
echo ""
