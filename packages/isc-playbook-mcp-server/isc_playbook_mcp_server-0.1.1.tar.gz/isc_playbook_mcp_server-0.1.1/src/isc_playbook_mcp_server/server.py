#!/usr/bin/env python3
"""
IBM ISC Playbook MCP Server
Provides hybrid search (semantic + keyword) for IBM ISC Playbook documentation.
"""

import logging
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from .hybrid_indexer import HybridSearchIndexer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("IBM ISC Playbook")

# Initialize hybrid search indexer
DB_PATH = Path(__file__).parent.parent.parent / "data" / "index" / "playbook_hybrid.db"
indexer = HybridSearchIndexer(str(DB_PATH))

logger.info(f"MCP Server initialized with hybrid search index: {DB_PATH}")


class SearchResult(BaseModel):
    """Hybrid search result"""
    url: str = Field(description="Page URL")
    title: str = Field(description="Page title")
    type: str = Field(description="Content type (document/folder)")
    path: str = Field(description="Navigation path")
    text_preview: str = Field(description="Text preview/snippet")
    score: float = Field(description="Hybrid search score")
    text_length: int = Field(description="Full text length")


class DocumentContent(BaseModel):
    """Full document content"""
    url: str = Field(description="Document URL")
    title: str = Field(description="Document title")
    type: str = Field(description="Content type")
    path: str = Field(description="Navigation path")
    full_text: str = Field(description="Complete document text")
    text_length: int = Field(description="Text length")


@mcp.tool()
def search_playbook(
    query: str,
    limit: int = 10,
    type_filter: Optional[str] = None
) -> List[SearchResult]:
    """
    Search IBM ISC Playbook using hybrid search (semantic + keyword).
    
    Args:
        query: Search query (natural language or keywords)
        limit: Maximum number of results (default: 10, max: 50)
        type_filter: Filter by type: "document" or "folder" (optional)
    
    Returns:
        List of search results ranked by relevance
        
    Examples:
        - "How to deploy to production"
        - "Customer creation process"
        - "Troubleshooting database issues"
        - "API documentation"
    """
    try:
        # Validate limit
        limit = min(max(1, limit), 50)
        
        # Validate type filter
        if type_filter and type_filter not in ["document", "folder"]:
            raise ValueError("type_filter must be 'document' or 'folder'")
        
        # Perform hybrid search
        logger.info(f"Searching: '{query}' (limit={limit}, type_filter={type_filter})")
        results = indexer.hybrid_search(
            query=query,
            limit=limit,
            type_filter=type_filter
        )
        
        # Convert to SearchResult models
        search_results = [
            SearchResult(
                url=r["url"],
                title=r["title"],
                type=r["type"],
                path=r["path"],
                text_preview=r["text"][:1000] + "..." if len(r["text"]) > 1000 else r["text"],
                score=r["score"],
                text_length=r["text_length"]
            )
            for r in results
        ]
        
        logger.info(f"Found {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise


@mcp.tool()
def get_document(url: str) -> DocumentContent:
    """
    Get full content of a specific playbook document by URL.
    
    Args:
        url: The exact URL of the document to retrieve
    
    Returns:
        Complete document with full text content
        
    Example:
        url = "https://isc.playbook.ibm.com/docs/deployment-guide"
    """
    try:
        logger.info(f"Retrieving document: {url}")
        doc = indexer.get_document(url)
        
        if not doc:
            raise ValueError(f"Document not found: {url}")
        
        return DocumentContent(
            url=doc["url"],
            title=doc["title"],
            type=doc["type"],
            path=doc["path"],
            full_text=doc["text"],
            text_length=doc["text_length"]
        )
        
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        raise


@mcp.tool()
def browse_by_type(type_filter: str, limit: int = 20) -> List[SearchResult]:
    """
    Browse playbook content by type (all documents or all folders).
    
    Args:
        type_filter: "document" or "folder"
        limit: Maximum number of results (default: 20, max: 100)
    
    Returns:
        List of pages filtered by type
    """
    try:
        if type_filter not in ["document", "folder"]:
            raise ValueError("type_filter must be 'document' or 'folder'")
        
        # Validate limit
        limit = min(max(1, limit), 100)
        
        # Use a broad query to get all items of this type
        logger.info(f"Browsing {type_filter}s (limit={limit})")
        results = indexer.hybrid_search(
            query="playbook content",  # Generic query
            limit=limit,
            type_filter=type_filter
        )
        
        # Convert to SearchResult models
        browse_results = [
            SearchResult(
                url=r["url"],
                title=r["title"],
                type=r["type"],
                path=r["path"],
                text_preview=r["text"][:500] + "..." if len(r["text"]) > 500 else r["text"],
                score=r["score"],
                text_length=r["text_length"]
            )
            for r in results
        ]
        
        logger.info(f"Found {len(browse_results)} {type_filter}s")
        return browse_results
        
    except Exception as e:
        logger.error(f"Browse error: {e}")
        raise


@mcp.tool()
def get_index_stats() -> dict:
    """
    Get statistics about the playbook index.
    
    Returns:
        Dictionary with index statistics (total pages, documents, folders)
    """
    try:
        stats = indexer.get_stats()
        logger.info(f"Index stats: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise


@mcp.tool()
def search_by_path(path_pattern: str, limit: int = 20) -> List[SearchResult]:
    """
    Search documents by navigation path pattern.
    
    Args:
        path_pattern: Path pattern to match (e.g., "UPX > PRM DevOps", "ISC Sales > Development")
        limit: Maximum number of results (default: 20, max: 50)
    
    Returns:
        List of documents matching the path pattern
        
    Examples:
        - "UPX > PRM DevOps"
        - "ISC Sales > Development"
        - "Cross Program"
        - "Salesforce Admin"
    """
    try:
        # Validate limit
        limit = min(max(1, limit), 50)
        
        logger.info(f"Searching by path: '{path_pattern}' (limit={limit})")
        results = indexer.search_by_path(
            path_pattern=path_pattern,
            limit=limit
        )
        
        # Convert to SearchResult models
        path_results = [
            SearchResult(
                url=r["url"],
                title=r["title"],
                type=r["type"],
                path=r["path"],
                text_preview=r["text"][:1000] + "..." if len(r["text"]) > 1000 else r["text"],
                score=r["score"],
                text_length=r["text_length"]
            )
            for r in results
        ]
        
        logger.info(f"Found {len(path_results)} results for path pattern")
        return path_results
        
    except Exception as e:
        logger.error(f"Path search error: {e}")
        raise


@mcp.tool()
def get_related_documents(url: str, limit: int = 5) -> List[SearchResult]:
    """
    Find documents similar to a given document using semantic similarity.
    
    Args:
        url: The URL of the reference document
        limit: Maximum number of related documents (default: 5, max: 10)
    
    Returns:
        List of semantically similar documents (excludes the reference document)
        
    Example:
        url = "https://w3.ibm.com/isc/playbook/#/documents/5b984503ef8d215af41fa6eb4a444cbf"
        
    Use cases:
        - "Show me related documentation"
        - "Find similar topics"
        - "What else should I read?"
    """
    try:
        # Validate limit
        limit = min(max(1, limit), 10)
        
        logger.info(f"Finding related documents for: {url} (limit={limit})")
        results = indexer.get_related_documents(
            url=url,
            limit=limit
        )
        
        if not results:
            logger.warning(f"No related documents found or document not found: {url}")
            return []
        
        # Convert to SearchResult models
        related_results = [
            SearchResult(
                url=r["url"],
                title=r["title"],
                type=r["type"],
                path=r["path"],
                text_preview=r["text"][:1000] + "..." if len(r["text"]) > 1000 else r["text"],
                score=r["score"],
                text_length=r["text_length"]
            )
            for r in results
        ]
        
        logger.info(f"Found {len(related_results)} related documents")
        return related_results
        
    except Exception as e:
        logger.error(f"Related documents error: {e}")
        raise


# Resources - provide direct access to documents
@mcp.resource("playbook://document/{url_path}")
def get_playbook_document(url_path: str) -> str:
    """
    Get a playbook document as a resource.
    
    The url_path should be URL-encoded.
    """
    try:
        # Decode URL path
        import urllib.parse
        url = urllib.parse.unquote(url_path)
        
        doc = indexer.get_document(url)
        if not doc:
            return f"Document not found: {url}"
        
        # Format as markdown
        content = f"""# {doc['title']}

**Type:** {doc['type']}
**Path:** {doc['path']}
**URL:** {doc['url']}

---

{doc['text']}
"""
        return content
        
    except Exception as e:
        logger.error(f"Error getting resource: {e}")
        return f"Error: {str(e)}"


# Prompts - pre-defined search patterns
@mcp.prompt()
def deployment_guide() -> str:
    """Search for deployment and installation guides"""
    return "deployment installation setup production environment configuration"


@mcp.prompt()
def troubleshooting() -> str:
    """Search for troubleshooting and debugging information"""
    return "troubleshooting debug error issue problem fix solution"


@mcp.prompt()
def api_docs() -> str:
    """Search for API documentation and endpoints"""
    return "API endpoint REST GraphQL authentication authorization swagger"


@mcp.prompt()
def getting_started() -> str:
    """Search for getting started and quick start guides"""
    return "getting started quick start tutorial beginner introduction overview"


def main():
    """Main entry point for the MCP server"""
    logger.info("Starting IBM ISC Playbook MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
