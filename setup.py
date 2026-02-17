# setup.py (installation script)
#!/usr/bin/env python3
"""
Setup script for Timesheet Manager
Run this after creating the Django project structure
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        sys.exit(1)
    print(f"✅ {description} completed successfully")

def main():
    print("🚀 Timesheet Manager Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Install requirements
    run_command('pip install -r requirements.txt', 'Installing dependencies')
    
    # Run migrations
    run_command('python manage.py makemigrations', 'Creating migrations')
    run_command('python manage.py migrate', 'Running migrations')
    
    # Create superuser (optional)
    print(f"\n{'='*60}")
    print("👤 Create Admin User")
    print(f"{'='*60}")
    response = input("Would you like to create an admin user now? (y/n): ")
    if response.lower() == 'y':
        run_command('python manage.py createsuperuser', 'Creating admin user')
    
    # Collect static files
    run_command('python manage.py collectstatic --noinput', 'Collecting static files')
    
    print(f"\n{'='*60}")
    print("🎉 Setup Complete!")
    print(f"{'='*60}")
    print("\nTo start the development server, run:")
    print("  python manage.py runserver")
    print("\nThen visit:")
    print("  http://127.0.0.1:8000/          - Timesheet App")
    print("  http://127.0.0.1:8000/admin/    - Admin Panel")
    print("\nFirst steps:")
    print("  1. Go to Admin Panel and add your companies with their schedules")
    print("  2. Create timesheets using the web interface")
    print("  3. Download Excel files for each timesheet")

if __name__ == '__main__':
    main()