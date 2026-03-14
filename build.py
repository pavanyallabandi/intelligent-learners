import os
import subprocess

if __name__ == '__main__':
    print("Starting Vercel build process...")
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run(['python3.9', '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    
    # Collect static files
    print("Collecting static files...")
    subprocess.run(['python3.9', 'manage.py', 'collectstatic', '--noinput'], check=True)
    
    # Run database migrations
    print("Running migrations...")
    subprocess.run(['python3.9', 'manage.py', 'migrate'], check=True)
    
    print("Build completed successfully.")
