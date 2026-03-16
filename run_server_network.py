#!/usr/bin/env python
"""
Script to run Django development server with network access
Allows other machines to access the server
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 80)
    print("🚀 Smart Coffee Shop - Development Server")
    print("=" * 80)
    print("\n📡 Listening on: http://0.0.0.0:8000/")
    print("   → Local access: http://127.0.0.1:8000/")
    print("   → Network access: http://<YOUR_IP>:8000/")
    print("\n💡 Để tìm IP máy này, chạy: ipconfig (Windows) hoặc ifconfig (Mac/Linux)")
    print("   Tìm dòng có 'IPv4 Address' hoặc 'inet'")
    print("\n⚠️  Bấm Ctrl+C để dừng server")
    print("=" * 80 + "\n")
    
    # Run server on 0.0.0.0:8000
    subprocess.run([
        sys.executable, 
        'manage.py', 
        'runserver', 
        '0.0.0.0:8000'
    ])
