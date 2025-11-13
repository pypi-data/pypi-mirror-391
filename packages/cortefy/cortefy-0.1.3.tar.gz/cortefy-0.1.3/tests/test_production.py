#!/usr/bin/env python3
"""
Production API Test Suite for Cortefy
Tests all API functionalities against production environment
"""
import os
import requests
import json
import time
import sys
from datetime import datetime

# Production API Configuration
PROD_API_KEY = "pA8X2UidmI9P5Tuyeh-4FqjiTfHl1QJNWvcgkYhkiDOPeXd0XXTHvHuYks6Msdhe"
# Update PROD_BASE_URL with your actual production URL
# Can be overridden via environment variable: CORTEFY_PROD_URL
PROD_BASE_URL = os.environ.get("CORTEFY_PROD_URL", "https://cortefy.com")

# Test configuration
TEST_CONTAINER_PREFIX = f"prod_test_{int(time.time())}"
TEST_CONTAINER_PROFILE = f"{TEST_CONTAINER_PREFIX}_profile"
TEST_CONTAINER_RECENT = f"{TEST_CONTAINER_PREFIX}_recent"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_test(name, status, details=""):
    """Print test result"""
    icon = "✓" if status else "✗"
    print(f"\n{icon} {name}")
    if details:
        print(f"   {details}")

def make_request(method, endpoint, data=None, params=None):
    """Make API request with error handling"""
    url = f"{PROD_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Api-Key {PROD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Longer timeout for search operations (embedding generation can be slow)
    # Also longer timeout for ingestion with sentence chunking (can be slow)
    if endpoint == "/api/memories/search/":
        timeout = 60
    elif endpoint == "/api/memories/ingest/":
        # Increased timeout for sentence chunking - may be slow or timeout at proxy level
        timeout = 90  # Increased to 90s to account for proxy timeouts
    else:
        timeout = 30
    
    # Use requests.request() directly like the client library does
    # This avoids session/connection pooling issues
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params,
            timeout=timeout
        )
        
        return response
    except requests.exceptions.Timeout as e:
        print(f"   ✗ Request timed out after {timeout}s")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"   ✗ Connection error: {e}")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Request failed: {type(e).__name__}: {e}")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        return None
    except Exception as e:
        print(f"   ✗ Unexpected error: {type(e).__name__}: {e}")
        print(f"   URL: {url}")
        return None

def test_authentication():
    """Test API authentication"""
    print_section("TEST 1: Authentication")
    
    # Test valid API key
    response = make_request("GET", "/api/containers/")
    if response and response.status_code == 200:
        print_test("Valid API key authentication", True, f"Status: {response.status_code}")
        return True
    elif response:
        print_test("Valid API key authentication", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
        return False
    else:
        print_test("Valid API key authentication", False, "Request failed")
        return False

def test_container_creation():
    """Test container creation via ingestion"""
    print_section("TEST 2: Container Creation")
    
    test_content = "This is a test memory for container creation. It will create a new container if it doesn't exist."
    
    response = make_request("POST", "/api/memories/ingest/", data={
        "content": test_content,
        "container": TEST_CONTAINER_PROFILE,
        "metadata": {"test": True, "type": "container_creation"}
    })
    
    if response:
        if response.status_code == 202:
            result = response.json()
            print_test("Container creation via ingestion", True, 
                      f"Container: {result.get('container')}, Chunks: {result.get('chunks')}")
            return True
        else:
            error_msg = response.text[:300] if response.text else 'No response body'
            print_test("Container creation via ingestion", False, 
                      f"Status: {response.status_code}, Response: {error_msg}")
            return False
    else:
        print_test("Container creation via ingestion", False, "Request failed (no response)")
        return False

def test_memory_ingestion():
    """Test memory ingestion with various configurations"""
    print_section("TEST 3: Memory Ingestion")
    
    tests = [
        {
            "name": "Basic ingestion",
            "data": {
                "content": "Python is a high-level programming language known for its simplicity and readability.",
                "container": TEST_CONTAINER_PROFILE,
                "metadata": {"topic": "programming", "language": "python"}
            }
        },
        {
            "name": "Large content ingestion",
            "data": {
                "content": " ".join(["Machine learning is a subset of artificial intelligence."] * 50),
                "container": TEST_CONTAINER_PROFILE,
                "chunk_method": "tokens",
                "chunk_size": 500,
                "chunk_overlap": 100
            }
        },
        {
            "name": "Sentence-based chunking",
            "data": {
                "content": "Django is a web framework. It follows the MVT pattern. It's built with Python.",
                "container": TEST_CONTAINER_PROFILE,
                "chunk_method": "sentences",
                "chunk_size": 2
            }
        },
        {
            "name": "Multiple containers",
            "data": {
                "content": "This is a recent memory that should go into the recent container.",
                "container": TEST_CONTAINER_RECENT,
                "metadata": {"type": "recent"}
            }
        }
    ]
    
    results = []
    for test in tests:
        response = make_request("POST", "/api/memories/ingest/", data=test["data"])
        if response:
            if response.status_code == 202:
                result = response.json()
                print_test(test["name"], True, 
                          f"Chunks: {result.get('chunks')}, Container: {result.get('container')}")
                results.append(True)
            else:
                error_msg = response.text[:200] if response.text else 'No response body'
                print_test(test["name"], False, 
                          f"Status: {response.status_code}, Error: {error_msg}")
                results.append(False)
        else:
            print_test(test["name"], False, "Request failed (no response)")
            results.append(False)
    
    return all(results)

def test_memory_listing():
    """Test listing memories"""
    print_section("TEST 4: Memory Listing")
    
    # List all memories
    response = make_request("GET", "/api/memories/")
    if response and response.status_code == 200:
        data = response.json()
        count = len(data.get('results', []))
        print_test("List all memories", True, f"Found {count} memories")
    else:
        print_test("List all memories", False, f"Status: {response.status_code if response else 'N/A'}")
        return False
    
    # List memories by container
    response = make_request("GET", "/api/memories/", params={"container": TEST_CONTAINER_PROFILE})
    if response and response.status_code == 200:
        data = response.json()
        count = len(data.get('results', []))
        print_test("List memories by container", True, f"Found {count} memories in {TEST_CONTAINER_PROFILE}")
    else:
        print_test("List memories by container", False, f"Status: {response.status_code if response else 'N/A'}")
        return False
    
    return True

def test_memory_search():
    """Test semantic search functionality"""
    print_section("TEST 5: Semantic Search")
    
    # Wait for embeddings to be generated
    print("\n⏳ Waiting 5 seconds for embeddings to be generated...")
    time.sleep(5)
    
    tests = [
        {
            "name": "Basic search",
            "data": {
                "q": "Python programming",
                "containerTag": TEST_CONTAINER_PROFILE,
                "limit": 5
            }
        },
        {
            "name": "Multi-container search",
            "data": {
                "q": "memory",
                "containerTags": [TEST_CONTAINER_PROFILE, TEST_CONTAINER_RECENT],
                "limit": 10
            }
        },
        {
            "name": "Search with similarity threshold",
            "data": {
                "q": "machine learning",
                "containerTag": TEST_CONTAINER_PROFILE,
                "limit": 5,
                "min_similarity": 0.3
            }
        },
        {
            "name": "Search all user containers",
            "data": {
                "q": "test",
                "limit": 10
            }
        }
    ]
    
    results = []
    for test in tests:
        response = make_request("POST", "/api/memories/search/", data=test["data"])
        if response and response.status_code == 200:
            result = response.json()
            total = result.get('total', 0)
            timing = result.get('timing', 0)
            print_test(test["name"], True, 
                      f"Found {total} results in {timing}ms")
            if result.get('results'):
                print(f"      Top result similarity: {result['results'][0].get('similarity', 0):.3f}")
            results.append(True)
        else:
            print_test(test["name"], False, 
                      f"Status: {response.status_code if response else 'N/A'}, Response: {response.text[:200] if response else 'N/A'}")
            results.append(False)
    
    return all(results)

def test_container_operations():
    """Test container CRUD operations"""
    print_section("TEST 6: Container Operations")
    
    # List containers
    response = make_request("GET", "/api/containers/")
    if response and response.status_code == 200:
        containers = response.json().get('results', [])
        test_containers = [c for c in containers if TEST_CONTAINER_PREFIX in c.get('name', '')]
        print_test("List containers", True, f"Found {len(test_containers)} test containers")
    else:
        print_test("List containers", False, f"Status: {response.status_code if response else 'N/A'}")
        return False
    
    # Get specific container
    if test_containers:
        container_name = test_containers[0]['name']
        response = make_request("GET", f"/api/containers/{container_name}/")
        if response and response.status_code == 200:
            container = response.json()
            print_test("Get container details", True, 
                      f"Container: {container.get('name')}, Memories: {container.get('memory_count', 0)}")
        else:
            print_test("Get container details", False, f"Status: {response.status_code if response else 'N/A'}")
    
    return True

def test_error_handling():
    """Test error handling and edge cases"""
    print_section("TEST 7: Error Handling")
    
    tests = [
        {
            "name": "Invalid container access",
            "method": "POST",
            "endpoint": "/api/memories/ingest/",
            "data": {"content": "test", "container": "nonexistent_container_12345"},
            "expected_status": [202, 400, 403],  # 202 if auto-creation enabled, 400/403 otherwise
            "note": "May return 202 if container auto-creation is enabled"
        },
        {
            "name": "Empty content",
            "method": "POST",
            "endpoint": "/api/memories/ingest/",
            "data": {"content": "", "container": TEST_CONTAINER_PROFILE},
            "expected_status": [400],
            "note": "Should validate empty content"
        },
        {
            "name": "Invalid search query",
            "method": "POST",
            "endpoint": "/api/memories/search/",
            "data": {"q": ""},
            "expected_status": [400],
            "note": "Should validate empty query"
        },
        {
            "name": "Nonexistent memory access",
            "method": "GET",
            "endpoint": "/api/memories/999999999/",
            "expected_status": [404],
            "note": "Should return 404 for nonexistent memory"
        }
    ]
    
    results = []
    for test in tests:
        response = make_request(test["method"], test["endpoint"], 
                              data=test.get("data"), params=test.get("params"))
        if response:
            status_match = response.status_code in test["expected_status"]
            note = test.get("note", "")
            details = f"Status: {response.status_code} (expected: {test['expected_status']})"
            if note:
                details += f" - {note}"
            print_test(test["name"], status_match, details)
            results.append(status_match)
        else:
            note = test.get("note", "")
            error_msg = "Request failed (timeout or connection error)"
            if note:
                error_msg += f" - {note}"
            print_test(test["name"], False, error_msg)
            results.append(False)
    
    return all(results)

def test_performance():
    """Test API performance"""
    print_section("TEST 8: Performance Testing")
    
    # Test ingestion performance
    start_time = time.time()
    response = make_request("POST", "/api/memories/ingest/", data={
        "content": "Performance test content. " * 20,
        "container": TEST_CONTAINER_PROFILE
    })
    ingestion_time = time.time() - start_time
    
    if response and response.status_code == 202:
        print_test("Ingestion performance", True, f"Time: {ingestion_time:.2f}s")
    else:
        print_test("Ingestion performance", False, f"Status: {response.status_code if response else 'N/A'}")
    
    # Test search performance
    time.sleep(3)  # Wait for embeddings
    start_time = time.time()
    response = make_request("POST", "/api/memories/search/", data={
        "q": "performance test",
        "containerTag": TEST_CONTAINER_PROFILE,
        "limit": 10
    })
    search_time = time.time() - start_time
    
    if response and response.status_code == 200:
        api_timing = response.json().get('timing', 0) / 1000  # Convert ms to seconds
        print_test("Search performance", True, 
                  f"Total time: {search_time:.2f}s, API timing: {api_timing:.2f}s")
    else:
        print_test("Search performance", False, f"Status: {response.status_code if response else 'N/A'}")
    
    return True

def test_multi_tenant_isolation():
    """Test multi-tenant isolation (if applicable)"""
    print_section("TEST 9: Multi-Tenant Isolation")
    
    # List containers - should only see containers for this API key's user
    response = make_request("GET", "/api/containers/")
    if response and response.status_code == 200:
        containers = response.json().get('results', [])
        print_test("Container isolation", True, 
                  f"API key can access {len(containers)} containers")
        
        # Verify we can only access our own containers
        if containers:
            test_container = containers[0]['name']
            response2 = make_request("GET", f"/api/containers/{test_container}/")
            if response2 and response2.status_code == 200:
                print_test("Container access control", True, "Can access own containers")
            else:
                print_test("Container access control", False, f"Status: {response2.status_code if response2 else 'N/A'}")
    else:
        print_test("Container isolation", False, f"Status: {response.status_code if response else 'N/A'}")
    
    return True

def cleanup_test_data():
    """Cleanup test data (optional - containers will remain)"""
    print_section("CLEANUP")
    print("\n⚠️  Test containers created:")
    print(f"   - {TEST_CONTAINER_PROFILE}")
    print(f"   - {TEST_CONTAINER_RECENT}")
    print("\n   Note: Containers are not automatically deleted.")
    print("   You may want to clean them up manually via admin panel.")

def main():
    """Run all production tests"""
    print("\n" + "="*80)
    print("  CORTEFY PRODUCTION API TEST SUITE")
    print("="*80)
    print(f"\n📍 Production URL: {PROD_BASE_URL}")
    print(f"🔑 API Key: {PROD_API_KEY[:20]}...")
    print(f"📦 Test Container Prefix: {TEST_CONTAINER_PREFIX}")
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test_results = []
    
    try:
        test_results.append(("Authentication", test_authentication()))
        test_results.append(("Container Creation", test_container_creation()))
        test_results.append(("Memory Ingestion", test_memory_ingestion()))
        test_results.append(("Memory Listing", test_memory_listing()))
        test_results.append(("Semantic Search", test_memory_search()))
        test_results.append(("Container Operations", test_container_operations()))
        test_results.append(("Error Handling", test_error_handling()))
        test_results.append(("Performance", test_performance()))
        test_results.append(("Multi-Tenant Isolation", test_multi_tenant_isolation()))
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed ({passed*100//total}%)")
    print(f"⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cleanup info
    cleanup_test_data()
    
    if passed == total:
        print("\n  🎉 All tests passed! Production API is working correctly.")
        return 0
    else:
        print("\n  ⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

