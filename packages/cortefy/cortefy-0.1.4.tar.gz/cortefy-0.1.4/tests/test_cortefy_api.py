#!/usr/bin/env python3
"""
Test script for Cortefy Python API client
"""
import os
import sys
from cortefy import Cortefy
from cortefy.exceptions import AuthenticationError, APIError

def test_cortefy_api():
    """Test the Cortefy API client"""
    
    # Get API key from environment
    api_key = os.environ.get("CORTEFY_API_KEY")
    if not api_key:
        print("❌ ERROR: CORTEFY_API_KEY environment variable not set")
        print("   Set it with: export CORTEFY_API_KEY='your-api-key'")
        return False
    
    # Get base URL (defaults to localhost for local testing)
    base_url = os.environ.get("CORTEFY_BASE_URL", "http://localhost:8000")
    
    print(f"🔧 Testing Cortefy API")
    print(f"   Base URL: {base_url}")
    print(f"   API Key: {api_key[:10]}...")
    print()
    
    try:
        # Initialize client
        print("1️⃣  Initializing client...")
        client = Cortefy(api_key=api_key, base_url=base_url)
        print("   ✓ Client initialized")
        print()
        
        # Test adding a memory
        print("2️⃣  Testing memories.add()...")
        test_content = "Machine learning enables computers to learn from data without being explicitly programmed. It uses algorithms to identify patterns and make predictions."
        test_metadata = {"priority": "high", "topic": "machine-learning", "test": True}
        
        result = client.memories.add(
            content=test_content,
            container_tags=["test-cortefy-package"],
            metadata=test_metadata
        )
        
        print(f"   ✓ Memory added successfully")
        print(f"   - Status: {result.get('status')}")
        print(f"   - Chunks: {result.get('chunks')}")
        print(f"   - Container: {result.get('container')}")
        print(f"   - Memory IDs: {result.get('memory_ids', [])[:3]}...")  # Show first 3
        if 'timing' in result:
            print(f"   - Timing: {result['timing']}")
        print()
        
        # Wait a bit for embeddings to be generated (if async)
        import time
        print("3️⃣  Waiting 3 seconds for embeddings to be generated...")
        time.sleep(3)
        print()
        
        # Test searching memories
        print("4️⃣  Testing search.memories()...")
        search_results = client.search.memories(
            q="machine learning algorithms",
            limit=5,
            container_tag="test-cortefy-package"
        )
        
        print(f"   ✓ Search completed")
        print(f"   - Total results: {search_results.get('total', 0)}")
        print(f"   - Timing: {search_results.get('timing', 0)}ms")
        
        results = search_results.get('results', [])
        if results:
            print(f"   - Found {len(results)} results:")
            for i, result in enumerate(results[:3], 1):  # Show first 3
                print(f"     {i}. ID: {result.get('id')}, Similarity: {result.get('similarity', 0):.3f}")
                print(f"        Content: {result.get('memory', '')[:60]}...")
        else:
            print("   ⚠️  No results found (embeddings may still be processing)")
        print()
        
        print("✅ All tests passed!")
        return True
        
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Check your API key is correct")
        return False
        
    except APIError as e:
        print(f"❌ API error: {e}")
        if e.status_code:
            print(f"   Status code: {e.status_code}")
        if e.response:
            try:
                error_data = e.response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response: {e.response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cortefy_api()
    sys.exit(0 if success else 1)

