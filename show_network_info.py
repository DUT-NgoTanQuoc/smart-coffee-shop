#!/usr/bin/env python
"""
Script to display network information and how to access the server
"""

import socket
import subprocess
import sys
import os

def get_local_ip():
    """Get local machine IP address"""
    try:
        # Connect to a public DNS server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return None

def get_all_ips():
    """Get all IP addresses of the machine"""
    ips = []
    try:
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
    except Exception:
        pass
    return ips

def main():
    print("\n" + "="*80)
    print("🌐 SMART COFFEE SHOP - Network Access Information")
    print("="*80)
    
    local_ip = get_local_ip()
    all_ips = get_all_ips()
    
    print("\n📍 Server Information:")
    print("   • Port: 8000")
    print("   • Status: Ready to receive connections")
    
    if local_ip:
        print(f"\n✅ Primary IP Address: {local_ip}")
        print(f"   Access URL: http://{local_ip}:8000/")
    
    if all_ips:
        print(f"\n📋 All IP Addresses on this machine:")
        for i, ip in enumerate(all_ips, 1):
            print(f"   {i}. http://{ip}:8000/")
    
    print("\n🔧 How to access from another machine:")
    print("   1. Make sure both machines are on the same network")
    print("   2. Use one of the IP addresses above to access the server")
    print("   3. Example: http://192.168.1.100:8000/ (replace with actual IP)")
    
    print("\n⚠️  Firewall Note:")
    print("   • Make sure port 8000 is not blocked by firewall")
    print("   • Windows: Allow Python through firewall or add port 8000 to exceptions")
    
    print("\n📝 Credentials for testing:")
    print("   • Username: barista4, cashier1, quan_ly, etc.")
    print("   • Password: 123456")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
