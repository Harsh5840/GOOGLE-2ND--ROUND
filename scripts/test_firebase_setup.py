#!/usr/bin/env python3
"""
Firebase/Firestore Setup Test Script

This script helps you verify that your Firebase/Firestore authentication is working correctly.
Run this script to test your setup before using the main application.
"""

import os
import sys

from dotenv import load_dotenv


def test_environment_variables():
    """Test if environment variables are set correctly"""
    print("🔍 Testing Environment Variables...")
    
    # Check for Firebase credentials
    firebase_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    firebase_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    print(f"  FIREBASE_SERVICE_ACCOUNT_PATH: {'✅ Set' if firebase_path else '❌ Not set'}")
    if firebase_path:
        print(f"    Path: {firebase_path}")
        print(f"    File exists: {'✅ Yes' if os.path.exists(firebase_path) else '❌ No'}")
    
    print(f"  FIREBASE_SERVICE_ACCOUNT_JSON: {'✅ Set' if firebase_json else '❌ Not set'}")
    print(f"  GOOGLE_APPLICATION_CREDENTIALS: {'✅ Set' if google_creds else '❌ Not set'}")
    
    if google_creds:
        print(f"    Path: {google_creds}")
        print(f"    File exists: {'✅ Yes' if os.path.exists(google_creds) else '❌ No'}")
    
    return any([firebase_path, firebase_json, google_creds])

def test_firebase_import():
    """Test if Firebase libraries can be imported"""
    print("\n📦 Testing Firebase Libraries...")
    
    try:
        from google.cloud import firestore
        print("  ✅ google.cloud.firestore imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import google.cloud.firestore: {e}")
        return False
    
    try:
        from google.oauth2 import service_account
        print("  ✅ google.oauth2.service_account imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import google.oauth2.service_account: {e}")
        return False
    
    return True

def test_firestore_connection():
    """Test Firestore connection"""
    print("\n🔗 Testing Firestore Connection...")
    
    try:
        from tools.firestore import db
        
        if db is None:
            print("  ❌ Firestore client is None")
            return False
        
        # Test a simple operation
        test_collection = db.collection('test_connection')
        test_doc = test_collection.document('test')
        
        # Try to read (this will fail if not authenticated, but won't crash)
        test_doc.get()
        
        print("  ✅ Firestore client initialized successfully")
        print("  ✅ Basic Firestore operations working")
        return True
        
    except Exception as e:
        print(f"  ❌ Firestore connection failed: {e}")
        return False

def test_query_history():
    """Test query history functionality"""
    print("\n📝 Testing Query History...")
    
    try:
        from tools.firestore import get_user_query_history, store_user_query_history

        # Test storing a query
        test_user_id = "test_setup_user"
        test_query = "test query from setup script"
        test_response = {"intent": "test", "entities": {}, "reply": "test reply"}
        
        result = store_user_query_history(test_user_id, test_query, test_response)
        print(f"  ✅ Query storage test: {result}")
        
        # Test retrieving queries
        history = get_user_query_history(test_user_id, 5)
        print(f"  ✅ Query retrieval test: Found {len(history)} queries")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Query history test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Firebase/Firestore Setup Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    env_ok = test_environment_variables()
    import_ok = test_firebase_import()
    connection_ok = test_firestore_connection()
    query_ok = test_query_history()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Firebase Libraries: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"Firestore Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Query History: {'✅ PASS' if query_ok else '❌ FAIL'}")
    
    if all([env_ok, import_ok, connection_ok, query_ok]):
        print("\n🎉 All tests passed! Your Firebase setup is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the FIREBASE_SETUP.md guide.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 