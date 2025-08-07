#!/usr/bin/env python3
import os
import sys
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Install required packages if not available
try:
    import django
except ImportError:
    print("Installing Django...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'django'], check=True)

try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], check=True)

# Now run the Django command
if __name__ == '__main__':
    try:
        # Import Django settings
        import django
        django.setup()
        
        # Import and run the command
        from django.core.management import execute_from_command_line
        
        # Set up command line arguments
        argv = ['manage.py', 'test_shopify_api', '--listings', '--json']
        execute_from_command_line(argv)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
