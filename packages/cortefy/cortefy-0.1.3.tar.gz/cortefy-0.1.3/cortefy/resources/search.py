"""
Search resource for querying memories
"""
from typing import Optional, List, Union


class SearchResource:
    """Resource for search operations"""
    
    def __init__(self, client):
        self.client = client
    
    def memories(
        self,
        q: str,
        container_tag: Optional[Union[str, List[str]]] = None,
        container_tags: Optional[List[str]] = None,
        limit: int = 5,
        min_similarity: float = 0.0
    ) -> dict:
        """
        Search memories using semantic search
        
        Args:
            q: Search query text
            container_tag: Optional single container tag to filter by (deprecated: use container_tags)
            container_tags: Optional list of container tags to search across multiple containers
            limit: Maximum number of results (default: 5)
            min_similarity: Minimum similarity score (0.0 to 1.0, default: 0.0)
            
        Returns:
            Response dict with results, timing, and total count
            
        Example:
            # Search in a single container
            results = client.search.memories(
                q="machine learning accuracy",
                limit=5,
                container_tag="research"
            )
            
            # Search across multiple containers
            results = client.search.memories(
                q="machine learning accuracy",
                container_tags=["research", "notes", "docs"]
            )
        """
        if not q:
            raise ValueError("query (q) is required")
        
        payload = {
            "q": q,
            "limit": limit,
            "min_similarity": min_similarity
        }
        
        # Support both container_tag (single, deprecated) and container_tags (multiple)
        if container_tags:
            payload["containerTags"] = container_tags
        elif container_tag:
            # If container_tag is provided, use it (backwards compatibility)
            if isinstance(container_tag, list):
                payload["containerTags"] = container_tag
            else:
                payload["containerTag"] = container_tag
        
        return self.client._request(
            method="POST",
            endpoint="/api/memories/search/",
            json=payload
        )

