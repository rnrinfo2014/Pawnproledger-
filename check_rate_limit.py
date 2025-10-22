#!/usr/bin/env python3
"""
Rate Limit Management Script
Provides utilities to manage rate limiting during development
"""

import requests
import os
import sys

def test_rate_limit_status():
    """Test current rate limit status"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing rate limit status...")
    
    # Test a simple endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Server is responding normally")
        elif response.status_code == 429:
            print("❌ Rate limit is active - too many requests")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_environment_settings():
    """Check current rate limit environment settings"""
    
    print("\n📋 Current Environment Settings:")
    
    # Check development environment file
    env_file = "config/env.development"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            if "RATE_LIMIT" in line:
                print(f"   {line.strip()}")
    else:
        print("   ❌ env.development file not found")

def restart_server_message():
    """Display restart instructions"""
    
    print("\n🔄 To apply rate limit changes:")
    print("   1. Stop the current server (Ctrl+C)")
    print("   2. Restart with: python run_server.py")
    print("   3. The new rate limits will take effect")

def main():
    """Main function"""
    
    print("🛡️ PawnSoft Rate Limit Manager")
    print("=" * 40)
    
    # Show current status
    check_environment_settings()
    test_rate_limit_status()
    
    print("\n💡 Rate Limit Information:")
    print("   - Current limit: 1000 requests per hour")
    print("   - Local IPs (192.168.x.x, 127.0.0.1) have relaxed limits")
    print("   - Authentication endpoints are exempt")
    print("   - Docs endpoints (/docs, /redoc) are exempt")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--restart-info":
        restart_server_message()
    
    print("\n🎯 Solutions:")
    print("   1. ✅ Rate limits are now more generous (1000/hour)")
    print("   2. ✅ Local network IPs have relaxed limits") 
    print("   3. ✅ Essential endpoints are exempt")
    print("   4. 🔄 Restart server if changes don't take effect")

if __name__ == "__main__":
    main()