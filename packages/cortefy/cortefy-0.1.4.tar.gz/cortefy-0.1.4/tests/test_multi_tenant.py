#!/usr/bin/env python3
"""
Quick manual test script for multi-tenant support
Run: python tests/test_multi_tenant.py
"""
import os
import sys
import django

# Setup Django - adjust path to project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

import requests
from django.contrib.auth.models import User
from memory.models import APIKey, MemoryContainer, Memory
import numpy as np

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def setup_test_data():
    print_section("SETTING UP TEST DATA")
    print("Cleaning up existing test data...")
    User.objects.filter(username__in=['test_user1', 'test_user2']).delete()
    
    print("\n1. Creating users...")
    user1 = User.objects.create_user('test_user1', 'user1@test.com', 'testpass123')
    user2 = User.objects.create_user('test_user2', 'user2@test.com', 'testpass123')
    print(f"   ✓ Created user1: {user1.username}")
    print(f"   ✓ Created user2: {user2.username}")
    
    print("\n2. Creating containers...")
    c1_profile = MemoryContainer.objects.create(name='user1_profile', owner=user1)
    c1_recent = MemoryContainer.objects.create(name='user1_recent', owner=user1)
    c2_profile = MemoryContainer.objects.create(name='user2_profile', owner=user2)
    print(f"   ✓ Created containers")
    
    print("\n3. Creating API keys...")
    key1 = APIKey.objects.create(name='User1 General Key', user=user1)
    key1_container = APIKey.objects.create(name='User1 Container Key', user=user1, container=c1_profile)
    key2 = APIKey.objects.create(name='User2 General Key', user=user2)
    print(f"   ✓ Created API keys")
    
    print("\n4. Creating test memories...")
    dummy_embedding = np.random.rand(384).astype(np.float32).tolist()
    m1 = Memory.objects.create(content='User1 profile memory: I love Python and Django development.', container=c1_profile, embedding_status='completed')
    m1.embedding = dummy_embedding
    m1.save()
    m2 = Memory.objects.create(content='User1 recent memory: Working on a multi-tenant API system.', container=c1_recent, embedding_status='completed')
    m2.embedding = dummy_embedding
    m2.save()
    m3 = Memory.objects.create(content='User2 profile memory: I prefer JavaScript and React.', container=c2_profile, embedding_status='completed')
    m3.embedding = dummy_embedding
    m3.save()
    print(f"   ✓ Created test memories")
    
    return {'user1': user1, 'user2': user2, 'key1': key1, 'key1_container': key1_container, 'key2': key2, 'containers': {'c1_profile': c1_profile, 'c1_recent': c1_recent, 'c2_profile': c2_profile}, 'memories': {'m1': m1, 'm2': m2, 'm3': m3}}

def test_user_isolation(test_data):
    print_section("TEST 1: User Isolation")
    key1, key2 = test_data['key1'], test_data['key2']
    m1_id, m3_id = test_data['memories']['m1'].id, test_data['memories']['m3'].id
    
    print("\n🔑 Testing User1 API key...")
    response1 = requests.get(f"{BASE_URL}/memories/", headers={"Authorization": f"Bearer {key1.key}"})
    if response1.status_code == 200:
        memories1 = response1.json().get('results', [])
        memory_ids1 = [m['id'] for m in memories1]
        assert m1_id in memory_ids1 and m3_id not in memory_ids1
        print(f"   ✓ User1 isolation verified")
    
    print("\n🔑 Testing User2 API key...")
    response2 = requests.get(f"{BASE_URL}/memories/", headers={"Authorization": f"Bearer {key2.key}"})
    if response2.status_code == 200:
        memories2 = response2.json().get('results', [])
        memory_ids2 = [m['id'] for m in memories2]
        assert m3_id in memory_ids2 and m1_id not in memory_ids2
        print(f"   ✓ User2 isolation verified")
        return True
    return False

def test_unauthorized_access(test_data):
    print_section("TEST 2: Unauthorized Access (404 Check)")
    key1 = test_data['key1']
    m3_id = test_data['memories']['m3'].id
    response = requests.get(f"{BASE_URL}/memories/{m3_id}/", headers={"Authorization": f"Bearer {key1.key}"})
    if response.status_code == 404:
        print("   ✓ Correctly returned 404")
        return True
    return False

def test_container_ownership(test_data):
    print_section("TEST 3: Container Ownership Validation")
    key1 = test_data['key1']
    c2_profile = test_data['containers']['c2_profile']
    response = requests.post(f"{BASE_URL}/memories/ingest/", headers={"Authorization": f"Bearer {key1.key}"}, json={'content': 'Test', 'container': c2_profile.name})
    if response.status_code == 403:
        print("   ✓ Correctly returned 403")
        return True
    return False

def test_multi_container_search(test_data):
    print_section("TEST 4: Multi-Container Search")
    key1 = test_data['key1']
    response = requests.post(f"{BASE_URL}/memories/search/", headers={"Authorization": f"Bearer {key1.key}"}, json={'q': 'Python', 'containerTags': ['user1_profile', 'user1_recent'], 'limit': 10})
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Found {result.get('total', 0)} results")
        return True
    return False

def test_api_key_container_scoping(test_data):
    print_section("TEST 5: API Key Container Scoping")
    key1_container = test_data['key1_container']
    c1_profile = test_data['containers']['c1_profile']
    m1_id, m2_id = test_data['memories']['m1'].id, test_data['memories']['m2'].id
    response = requests.get(f"{BASE_URL}/memories/", headers={"Authorization": f"Bearer {key1_container.key}"})
    if response.status_code == 200:
        memories = response.json().get('results', [])
        memory_ids = [m['id'] for m in memories]
        assert m1_id in memory_ids and m2_id not in memory_ids
        print("   ✓ Container scoping verified")
        return True
    return False

def test_container_list_isolation(test_data):
    print_section("TEST 6: Container List Isolation")
    key1, key2 = test_data['key1'], test_data['key2']
    response1 = requests.get(f"{BASE_URL}/containers/", headers={"Authorization": f"Bearer {key1.key}"})
    response2 = requests.get(f"{BASE_URL}/containers/", headers={"Authorization": f"Bearer {key2.key}"})
    if response1.status_code == 200 and response2.status_code == 200:
        containers1 = [c['name'] for c in response1.json().get('results', [])]
        containers2 = [c['name'] for c in response2.json().get('results', [])]
        assert 'user1_profile' in containers1 and 'user2_profile' not in containers1
        assert 'user2_profile' in containers2 and 'user1_profile' not in containers2
        print("   ✓ Container list isolation verified")
        return True
    return False

def check_server_running():
    try:
        requests.get("http://localhost:8000/api/", timeout=2)
        return True
    except:
        return False

def main():
    print("\n" + "="*70)
    print("  MULTI-TENANT API TEST SUITE")
    print("="*70)
    
    print("\n🔍 Checking if Django server is running...")
    if not check_server_running():
        print("\n❌ ERROR: Django server is not running!")
        print("Please start: python manage.py runserver")
        sys.exit(1)
    print("   ✓ Server is running")
    
    try:
        test_data = setup_test_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print_section("API KEYS FOR MANUAL TESTING")
    print(f"\nUser1 General Key: {test_data['key1'].key}")
    print(f"User1 Container Key: {test_data['key1_container'].key}")
    print(f"User2 General Key: {test_data['key2'].key}")
    
    print_section("RUNNING TESTS")
    results = []
    try:
        results.append(("User Isolation", test_user_isolation(test_data)))
        results.append(("Unauthorized Access", test_unauthorized_access(test_data)))
        results.append(("Container Ownership", test_container_ownership(test_data)))
        results.append(("Multi-Container Search", test_multi_container_search(test_data)))
        results.append(("API Key Container Scoping", test_api_key_container_scoping(test_data)))
        results.append(("Container List Isolation", test_container_list_isolation(test_data)))
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print_section("TEST SUMMARY")
    passed = sum(1 for _, r in results if r)
    for name, result in results:
        print(f"  {'✓' if result else '✗'}: {name}")
    print(f"\n  Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n  🎉 All tests passed!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
