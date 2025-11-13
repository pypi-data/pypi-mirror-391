"""
Memories resource for adding and managing memories
"""
from typing import Optional, List, Dict, Any


class MemoriesResource:
    """Resource for memory operations"""
    
    def __init__(self, client):
        self.client = client
    
    def add(
        self,
        content: str,
        container_tag: Optional[str] = None,
        container_tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        custom_id: Optional[str] = None,
        raw: Optional[str] = None,
        chunk_method: str = "tokens",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> dict:
        """
        Add a memory to the Cortefy API
        
        Args:
            content: The text content to store (required)
            container_tag: Single container tag/name (recommended, preferred over container_tags)
            container_tags: List of container tags/names (deprecated: use container_tag)
            metadata: Optional metadata dictionary (values must be strings, numbers, or booleans)
            custom_id: Custom identifier for deduplication and updates (max 255 chars)
            raw: Raw content to store alongside processed content
            chunk_method: Chunking method ('tokens' or 'sentences', default: 'tokens')
            chunk_size: Size of chunks (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            
        Returns:
            Response dict with status, chunks, memory_ids, container, and timing
            
        Example:
            result = client.memories.add(
                content="Machine learning enables computers to learn from data",
                container_tag="ai-research",
                metadata={"priority": "high", "source": "research-paper"},
                custom_id="doc_2024_01_research_ml"
            )
        """
        if not content:
            raise ValueError("content is required")
        
        # Prefer container_tag over container_tags
        container = container_tag
        if not container and container_tags:
            if isinstance(container_tags, list) and len(container_tags) > 0:
                container = container_tags[0]
            elif isinstance(container_tags, str):
                container = container_tags
        
        payload = {
            "content": content,
            "metadata": metadata or {}
        }
        
        # Use containerTag (singular, recommended) if provided
        if container:
            payload["containerTag"] = container
        
        if custom_id:
            payload["customId"] = custom_id
        
        if raw:
            payload["raw"] = raw
        
        if chunk_method:
            payload["chunk_method"] = chunk_method
        if chunk_size:
            payload["chunk_size"] = chunk_size
        if chunk_overlap:
            payload["chunk_overlap"] = chunk_overlap
        
        return self.client._request(
            method="POST",
            endpoint="/api/memories/ingest/",
            json=payload
        )
    
    def upload_file(
        self,
        file_path: str,
        container_tags: Optional[str] = None,
        container_tag: Optional[str] = None
    ) -> dict:
        """
        Upload a file and process it into memories
        
        Args:
            file_path: Path to the file to upload
            container_tags: Container tag for the uploaded file (plural for file uploads)
            container_tag: Container tag (alternative to container_tags)
            
        Returns:
            Response dict with status, chunks, memory_ids, container, filename, and timing
            
        Supported formats:
            - Documents: PDF, DOC, DOCX, TXT, MD
            - Images: JPG, PNG, GIF, WebP (requires OCR libraries)
            - Videos: MP4, WebM, AVI (not yet supported)
            
        Maximum file size: 50MB
            
        Example:
            result = client.memories.upload_file(
                file_path="./document.pdf",
                container_tags="research"
            )
        """
        import os
        
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Use container_tag if provided, otherwise container_tags
        container_tag_value = container_tag or container_tags
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            data = {}
            if container_tag_value:
                data['containerTags'] = container_tag_value
            
            return self.client._request_file(
                method="POST",
                endpoint="/api/memories/v3/documents/file/",
                files=files,
                data=data
            )

