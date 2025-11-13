#!/usr/bin/env python3
"""
Test listing memories - equivalent to:
curl "https://cortefy.com/api/memories/?container=test_project" \
  -H "Authorization: Api-Key zYyUpqa1uYreMyMHSqgfxxRbaM-BFfo7ffMM3j1dfVj5T80aDXUgnmiEOlAncBks"
"""
import os
from cortefy import Cortefy
from cortefy.exceptions import AuthenticationError, APIError

def test_list_memories():
    """Test listing memories from a container"""
    
    # API key from the curl example
    api_key = os.environ.get("CORTEFY_API_KEY", "zYyUpqa1uYreMyMHSqgfxxRbaM-BFfo7ffMM3j1dfVj5T80aDXUgnmiEOlAncBks")
    base_url = os.environ.get("CORTEFY_BASE_URL", "https://cortefy.com")
    container = os.environ.get("CORTEFY_CONTAINER", "test_project")
    
    print(f"🔧 Testing List Memories API")
    print(f"   Base URL: {base_url}")
    print(f"   Container: {container}")
    print(f"   API Key: {api_key[:10]}...")
    print()
    
    try:
        # Initialize client
        client = Cortefy(api_key=api_key, base_url=base_url)
        
        # Make the request directly (since there's no list method in the client yet)
        # We'll use the _request method to call the GET endpoint
        print("📋 Fetching memories...")
        response = client._request(
            method="GET",
            endpoint=f"/api/memories/",
            params={"container": container}
        )
        
        print("✅ Success!")
        print()
        
        # Display results
        if isinstance(response, dict):
            if "results" in response:
                results = response["results"]
                count = response.get("count", len(results))
                print(f"Found {count} memories:")
                print()
                for i, memory in enumerate(results[:10], 1):  # Show first 10
                    print(f"{i}. ID: {memory.get('id')}")
                    print(f"   Content: {memory.get('content', '')[:80]}...")
                    print(f"   Container: {memory.get('container_name', 'N/A')}")
                    if memory.get('metadata'):
                        print(f"   Metadata: {memory.get('metadata')}")
                    print()
            else:
                # Direct list response
                print(f"Response: {response}")
        else:
            print(f"Response: {response}")
            
        return True
        
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
        
    except APIError as e:
        print(f"❌ API error: {e}")
        if e.status_code:
            print(f"   Status code: {e.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_list_memories()

