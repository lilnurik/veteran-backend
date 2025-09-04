#!/usr/bin/env python3
"""
Simple test script to validate the Veterans Backend API functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    print("✓ Health check passed")

def test_authentication():
    """Test authentication system"""
    # Test login
    login_data = {"username": "admin", "password": "admin"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert 'token' in data
    assert 'user' in data
    token = data['token']
    print("✓ Authentication login passed")
    
    # Test token verification
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/verify", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['valid'] is True
    print("✓ Authentication verification passed")
    
    return token

def test_laws_api():
    """Test laws API endpoints"""
    # Test get all laws
    response = requests.get(f"{BASE_URL}/api/laws")
    assert response.status_code == 200
    data = response.json()
    assert 'laws' in data
    assert 'total' in data
    print("✓ Laws API get all passed")
    
    # Test get specific law
    if data['total'] > 0:
        law_id = data['laws'][0]['id']
        response = requests.get(f"{BASE_URL}/api/laws/{law_id}")
        assert response.status_code == 200
        law_data = response.json()
        assert 'id' in law_data
        print("✓ Laws API get specific passed")

def test_news_api():
    """Test news API endpoints"""
    # Test get all news
    response = requests.get(f"{BASE_URL}/api/news")
    assert response.status_code == 200
    data = response.json()
    assert 'news' in data
    assert 'total' in data
    print("✓ News API get all passed")
    
    # Test get specific news
    if data['total'] > 0:
        news_id = data['news'][0]['id']
        response = requests.get(f"{BASE_URL}/api/news/{news_id}")
        assert response.status_code == 200
        news_data = response.json()
        assert 'id' in news_data
        print("✓ News API get specific passed")

def test_comrades_api():
    """Test comrades API endpoints"""
    # Test search comrades
    response = requests.get(f"{BASE_URL}/api/comrades")
    assert response.status_code == 200
    data = response.json()
    assert 'comrades' in data
    assert 'total' in data
    print("✓ Comrades API search passed")
    
    # Test get specific comrade
    if data['total'] > 0:
        comrade_id = data['comrades'][0]['id']
        response = requests.get(f"{BASE_URL}/api/comrades/{comrade_id}")
        assert response.status_code == 200
        comrade_data = response.json()
        assert 'id' in comrade_data
        print("✓ Comrades API get specific passed")

def test_swagger_docs():
    """Test that Swagger documentation is accessible"""
    response = requests.get(f"{BASE_URL}/docs/")
    assert response.status_code == 200
    assert 'Veterans Association API' in response.text
    print("✓ Swagger documentation accessible")

def main():
    """Run all tests"""
    print("Running Veterans Backend API Tests...")
    print("="*50)
    
    try:
        test_health_check()
        token = test_authentication()
        test_laws_api()
        test_news_api()
        test_comrades_api()
        test_swagger_docs()
        
        print("="*50)
        print("All tests passed! ✓")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    main()