import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("=" * 60)
        print("✅ SUCCESS! PostgreSQL connected successfully!")
        print("=" * 60)
        print(f"Database version: {version[0]}")
        print("=" * 60)
except Exception as e:
    print("=" * 60)
    print("❌ FAILED! Connection to PostgreSQL failed!")
    print("=" * 60)
    print(f"Error: {e}")
    print("=" * 60)
    print("\nPossible solutions:")
    print("1. Check if PostgreSQL service is running")
    print("2. Verify password in settings.py")
    print("3. Verify database name is 'product_management_db'")