#!/usr/bin/env python3
"""
OralCare AI - PostgreSQL Database Setup
"""

import os
import sys
import subprocess
from getpass import getpass

# Colors
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

def print_color(text, color):
    print(f"{color}{text}{NC}")

def main():
    print(f"{BLUE}🗄️  OralCare AI - Local PostgreSQL Setup{NC}")
    print("=" * 50)
    print()

    # Database configuration
    db_name = "oral_cancer"
    db_user = "postgres"
    db_host = "localhost"
    db_port = "5432"

    print(f"{BLUE}Database Configuration:{NC}")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  Database: {db_name}")
    print(f"  User: {db_user}")
    print()

    # Get password
    print(f"{YELLOW}Enter PostgreSQL password for user '{db_user}':{NC}")
    db_password = getpass()
    print()

    # Update .env file
    print(f"{BLUE}Step 1: Updating .env file...{NC}")
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    with open('.env', 'r') as f:
        content = f.read()

    # Replace DATABASE_URL
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            lines[i] = f"DATABASE_URL={database_url}"
            break

    with open('.env', 'w') as f:
        f.write('\n'.join(lines))

    print_color("✅ .env updated", GREEN)
    print()

    # Test connection
    print(f"{BLUE}Step 2: Testing PostgreSQL connection...{NC}")
    test_cmd = f"PGPASSWORD={db_password} psql -h {db_host} -U {db_user} -d postgres -c 'SELECT version();'"
    result = subprocess.run(test_cmd, shell=True, capture_output=True)

    if result.returncode == 0:
        print_color("✅ Connection successful!", GREEN)
    else:
        print_color("❌ Connection failed. Please check your password and PostgreSQL service.", RED)
        print("Error:", result.stderr.decode())
        sys.exit(1)
    print()

    # Check if database exists
    print(f"{BLUE}Step 3: Checking database '{db_name}'...{NC}")
    check_db = f"PGPASSWORD={db_password} psql -h {db_host} -U {db_user} -d postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='{db_name}'\""
    result = subprocess.run(check_db, shell=True, capture_output=True)
    db_exists = result.stdout.decode().strip() == "1"

    if db_exists:
        print_color(f"✅ Database '{db_name}' exists", GREEN)
    else:
        print_color(f"⚠️  Database '{db_name}' not found. Creating...", YELLOW)
        create_db = f"PGPASSWORD={db_password} psql -h {db_host} -U {db_user} -d postgres -c 'CREATE DATABASE {db_name};'"
        result = subprocess.run(create_db, shell=True, capture_output=True)

        if result.returncode == 0:
            print_color(f"✅ Database '{db_name}' created successfully!", GREEN)
        else:
            print_color("❌ Failed to create database", RED)
            print("Error:", result.stderr.decode())
            sys.exit(1)
    print()

    # Run migrations
    print(f"{BLUE}Step 4: Running Django migrations...{NC}")
    result = subprocess.run(["python", "manage.py", "migrate"], capture_output=True)

    if result.returncode == 0:
        print()
        print_color("✅ Migrations completed successfully!", GREEN)
    else:
        print()
        print_color("❌ Migration failed", RED)
        print(result.stderr.decode())
        sys.exit(1)
    print()

    # Create superuser
    print(f"{BLUE}Step 5: Create admin user{NC}")
    create_admin = input(f"{YELLOW}Do you want to create a new admin user? (y/n): {NC}")

    if create_admin.lower() in ['y', 'yes']:
        subprocess.run(["python", "manage.py", "createsuperuser"])
    print()

    # Summary
    print_color("🎉 Database Setup Complete!", GREEN)
    print()
    print("Database Details:")
    print(f"  📍 Host: {db_host}:{db_port}")
    print(f"  🗄️  Database: {db_name}")
    print(f"  👤 User: {db_user}")
    print()
    print("Next steps:")
    print("  1. Start server: python manage.py runserver")
    print("  2. Access app: http://localhost:8000")
    print("  3. Admin panel: http://localhost:8000/admin/")
    print()
    print("View database:")
    print(f"  psql -h {db_host} -U {db_user} -d {db_name}")
    print()

if __name__ == "__main__":
    main()
