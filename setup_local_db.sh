#!/bin/bash

# OralCare AI - Local PostgreSQL Database Setup

echo "🗄️  OralCare AI - Local PostgreSQL Setup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Database configuration
DB_NAME="oral_cancer"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

echo -e "${BLUE}Database Configuration:${NC}"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Prompt for password
echo -e "${YELLOW}Enter PostgreSQL password for user '$DB_USER':${NC}"
read -s DB_PASSWORD
echo ""

# Update .env file
echo -e "${BLUE}Step 1: Updating .env file...${NC}"
sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME|g" .env
echo -e "${GREEN}✅ .env updated${NC}"
echo ""

# Test connection
echo -e "${BLUE}Step 2: Testing PostgreSQL connection...${NC}"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "SELECT version();" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Connection successful!${NC}"
else
    echo -e "${RED}❌ Connection failed. Please check your password and PostgreSQL service.${NC}"
    exit 1
fi
echo ""

# Check if database exists
echo -e "${BLUE}Step 3: Checking database '$DB_NAME'...${NC}"
DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${GREEN}✅ Database '$DB_NAME' exists${NC}"
else
    echo -e "${YELLOW}⚠️  Database '$DB_NAME' not found. Creating...${NC}"
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database '$DB_NAME' created successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to create database${NC}"
        exit 1
    fi
fi
echo ""

# Activate virtual environment and run migrations
echo -e "${BLUE}Step 4: Running Django migrations...${NC}"
source venv/bin/activate

# Run migrations
python manage.py migrate

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Migrations completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Migration failed${NC}"
    exit 1
fi
echo ""

# Create superuser prompt
echo -e "${BLUE}Step 5: Create admin user${NC}"
echo -e "${YELLOW}Do you want to create a new admin user? (y/n)${NC}"
read -r CREATE_ADMIN

if [ "$CREATE_ADMIN" = "y" ] || [ "$CREATE_ADMIN" = "Y" ]; then
    python manage.py createsuperuser
fi
echo ""

# Summary
echo -e "${GREEN}🎉 Database Setup Complete!${NC}"
echo ""
echo "Database Details:"
echo "  📍 Host: $DB_HOST:$DB_PORT"
echo "  🗄️  Database: $DB_NAME"
echo "  👤 User: $DB_USER"
echo ""
echo "Next steps:"
echo "  1. Start server: python manage.py runserver"
echo "  2. Access app: http://localhost:8000"
echo "  3. Admin panel: http://localhost:8000/admin/"
echo ""
echo "View database:"
echo "  psql -h $DB_HOST -U $DB_USER -d $DB_NAME"
echo ""
