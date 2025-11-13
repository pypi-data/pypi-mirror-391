"""Hybrid search indexer using Milvus Lite with keyword + semantic search."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from pymilvus import (
    MilvusClient,
    DataType,
    AnnSearchRequest,
    RRFRanker,
)

logger = logging.getLogger(__name__)


class HybridSearchIndexer:
    """Hybrid search using Milvus Lite with dense + sparse vectors."""
    
    def __init__(self, db_path: str, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize hybrid search indexer.
        
        Args:
            db_path: Path to Milvus Lite database file
            model_name: Sentence transformer model name
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Milvus Lite client
        self.client = MilvusClient(str(self.db_path))
        
        # Load embedding model
        logger.info(f"Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully with {self.embedding_dim} dimensions")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(f"Could not load sentence transformer model: {e}")
        
        # Collection name
        self.collection_name = "playbook_pages"
        
        # Setup collection
        self._setup_collection()
    
    def _setup_collection(self):
        """Create Milvus collection with hybrid search schema."""
        # Check if collection exists
        if self.client.has_collection(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' already exists")
            return
        
        # Define schema for hybrid search
        schema = self.client.create_schema(
            auto_id=True,
            enable_dynamic_field=True,
        )
        
        # Add fields
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field(field_name="url", datatype=DataType.VARCHAR, max_length=512)
        schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=512)
        schema.add_field(field_name="type", datatype=DataType.VARCHAR, max_length=50)
        schema.add_field(field_name="path", datatype=DataType.VARCHAR, max_length=512)
        # Milvus VARCHAR limit is 65535, store full text up to this limit
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="text_length", datatype=DataType.INT64)
        
        # Dense vector for semantic search
        schema.add_field(
            field_name="dense_vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=self.embedding_dim
        )
        
        # Sparse vector for keyword search (BM25-style)
        schema.add_field(
            field_name="sparse_vector",
            datatype=DataType.SPARSE_FLOAT_VECTOR
        )
        
        # Prepare index params with metric types
        index_params = self.client.prepare_index_params()
        
        # Add index for dense vector with COSINE metric
        index_params.add_index(
            field_name="dense_vector",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )
        
        # Add index for sparse vector with IP metric
        index_params.add_index(
            field_name="sparse_vector",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="IP"
        )
        
        # Create collection with schema and index params
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        
        logger.info(f"Created collection '{self.collection_name}' with hybrid search schema")
    
    def _create_dense_embedding(self, text: str) -> List[float]:
        """Create dense embedding for semantic search."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def _create_sparse_embedding(self, text: str) -> Dict[int, float]:
        """
        Create sparse embedding for keyword search using improved BM25-like approach.
        Uses larger vocabulary size to reduce hash collisions.
        """
        # Simple word frequency-based sparse vector with larger vocabulary
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 2:  # Skip very short words
                # Increased vocabulary size to 100k to reduce collisions
                word_hash = hash(word) % 100000
                word_freq[word_hash] = word_freq.get(word_hash, 0) + 1
        
        # Normalize to TF-IDF-like scores
        max_freq = max(word_freq.values()) if word_freq else 1
        sparse_vector = {k: v / max_freq for k, v in word_freq.items()}
        
        return sparse_vector
    
    def clear_index(self):
        """Clear all indexed data."""
        if self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)
            self._setup_collection()
            logger.info("Index cleared")
    
    def index_pages(self, cleaned_pages: Dict[str, Dict]):
        """Index cleaned pages with hybrid vectors."""
        logger.info(f"Indexing {len(cleaned_pages)} pages with hybrid search...")
        
        # Prepare data for batch insertion
        data = []
        indexed = 0
        
        for url, page in cleaned_pages.items():
            try:
                # Combine title + text for embedding
                full_text = f"{page['title']} {page.get('path', '')} {page['text']}"
                
                # Create embeddings
                dense_vector = self._create_dense_embedding(full_text)
                sparse_vector = self._create_sparse_embedding(full_text)
                
                # Prepare document
                doc = {
                    "url": url,
                    "title": page['title'],
                    "type": page['type'],
                    "path": page.get('path', ''),
                    "text": page['text'][:65535],  # Milvus VARCHAR max limit
                    "text_length": page['stats']['text_length'],
                    "dense_vector": dense_vector,
                    "sparse_vector": sparse_vector,
                }
                
                data.append(doc)
                indexed += 1
                
                # Batch insert every 100 documents
                if len(data) >= 100:
                    self.client.insert(
                        collection_name=self.collection_name,
                        data=data
                    )
                    logger.info(f"Indexed {indexed}/{len(cleaned_pages)} pages")
                    data = []
                    
            except Exception as e:
                logger.error(f"Error indexing {url}: {e}")
        
        # Insert remaining documents
        if data:
            self.client.insert(
                collection_name=self.collection_name,
                data=data
            )
        
        # Flush to ensure data is persisted
        self.client.flush(self.collection_name)
        
        logger.info(f"Indexing complete: {indexed} pages indexed")
        return indexed
    
    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        semantic_weight: float = 0.5,
        type_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Perform hybrid search combining semantic and keyword search.
        
        Args:
            query: Search query
            limit: Number of results to return
            semantic_weight: Weight for semantic search (0-1), keyword weight = 1 - semantic_weight
            type_filter: Filter by page type (document/folder)
        
        Returns:
            List of search results with scores
        """
        # Load collection (required before search)
        self.client.load_collection(self.collection_name)
        
        # Create query embeddings
        dense_query = self._create_dense_embedding(query)
        sparse_query = self._create_sparse_embedding(query)
        
        # Build filter expression
        filter_expr = None
        if type_filter:
            filter_expr = f'type == "{type_filter}"'
        
        # Dense search request (semantic)
        dense_req = AnnSearchRequest(
            data=[dense_query],
            anns_field="dense_vector",
            param={"metric_type": "COSINE"},
            limit=limit * 2,  # Get more candidates for reranking
        )
        
        # Sparse search request (keyword)
        sparse_req = AnnSearchRequest(
            data=[sparse_query],
            anns_field="sparse_vector",
            param={"metric_type": "IP"},
            limit=limit * 2,
        )
        
        # Hybrid search with RRF (Reciprocal Rank Fusion)
        results = self.client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[dense_req, sparse_req],
            ranker=RRFRanker(k=60),  # RRF parameter
            limit=limit,
            output_fields=["url", "title", "type", "path", "text", "text_length"],
            filter=filter_expr,
        )
        
        # Format results
        formatted_results = []
        for hit in results[0]:  # Results are nested in a list
            formatted_results.append({
                "url": hit["entity"]["url"],
                "title": hit["entity"]["title"],
                "type": hit["entity"]["type"],
                "path": hit["entity"]["path"],
                "text": hit["entity"]["text"][:2000],  # Return 2000 char preview
                "text_length": hit["entity"]["text_length"],
                "score": hit["distance"],  # Hybrid score from RRF
            })
        
        return formatted_results
    
    def get_document(self, url: str) -> Optional[Dict]:
        """Get a specific document by URL."""
        results = self.client.query(
            collection_name=self.collection_name,
            filter=f'url == "{url}"',
            output_fields=["url", "title", "type", "path", "text", "text_length"],
            limit=1
        )
        
        if not results:
            return None
        
        doc = results[0]
        return {
            "url": doc["url"],
            "title": doc["title"],
            "type": doc["type"],
            "path": doc["path"],
            "text": doc["text"],
            "text_length": doc["text_length"],
        }
    
    def search_by_path(self, path_pattern: str, limit: int = 20) -> List[Dict]:
        """
        Search documents by navigation path pattern.
        
        Args:
            path_pattern: Path pattern to match (case-insensitive substring match)
            limit: Maximum results to return
        
        Returns:
            List of matching documents
        """
        # Use LIKE for substring matching in path
        filter_expr = f'path like "%{path_pattern}%"'
        
        results = self.client.query(
            collection_name=self.collection_name,
            filter=filter_expr,
            output_fields=["url", "title", "type", "path", "text", "text_length"],
            limit=limit
        )
        
        # Format results
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "url": doc["url"],
                "title": doc["title"],
                "type": doc["type"],
                "path": doc["path"],
                "text": doc["text"][:2000],  # Return 2000 char preview
                "text_length": doc["text_length"],
                "score": 1.0,  # Path match, perfect score
            })
        
        return formatted_results
    
    def get_related_documents(self, url: str, limit: int = 5) -> List[Dict]:
        """
        Find documents similar to a given document using semantic similarity.
        
        Args:
            url: URL of the reference document
            limit: Maximum number of related documents to return
        
        Returns:
            List of similar documents (excluding the reference document itself)
        """
        # First, get the reference document's embedding
        doc = self.get_document(url)
        if not doc:
            return []
        
        # Get the document's text to create embedding
        text = doc["text"]
        
        # Create embedding using the model
        embedding = self.model.encode(text, convert_to_tensor=False).tolist()
        
        # Search for similar documents using dense vector only
        results = self.client.search(
            collection_name=self.collection_name,
            data=[embedding],
            anns_field="dense_vector",
            limit=limit + 1,  # Get one extra to exclude the reference doc
            output_fields=["url", "title", "type", "path", "text", "text_length"],
        )
        
        # Format results and exclude the reference document
        formatted_results = []
        for hit in results[0]:
            if hit["entity"]["url"] == url:
                continue  # Skip the reference document itself
            
            formatted_results.append({
                "url": hit["entity"]["url"],
                "title": hit["entity"]["title"],
                "type": hit["entity"]["type"],
                "path": hit["entity"]["path"],
                "text": hit["entity"]["text"][:2000],  # Return 2000 char preview
                "text_length": hit["entity"]["text_length"],
                "score": hit["distance"],  # Similarity score
            })
            
            if len(formatted_results) >= limit:
                break
        
        return formatted_results
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        stats = self.client.get_collection_stats(self.collection_name)
        
        # Count documents and folders using aggregation
        # Query all entities and count by type
        all_entities = self.client.query(
            collection_name=self.collection_name,
            filter="",
            output_fields=["type"],
            limit=10000  # Get all entities
        )
        
        doc_count = sum(1 for e in all_entities if e.get("type") == "document")
        folder_count = sum(1 for e in all_entities if e.get("type") == "folder")
        
        return {
            "total_pages": stats["row_count"],
            "documents": doc_count,
            "folders": folder_count,
        }
    
    def close(self):
        """Close connection."""
        self.client.close()


def build_hybrid_index(cleaned_data_path: str, db_path: str):
    """Build hybrid search index from cleaned data."""
    logger.info("Building hybrid search index with Milvus Lite...")
    
    # Load cleaned data
    with open(cleaned_data_path, 'r', encoding='utf-8') as f:
        cleaned_pages = json.load(f)
    
    # Create indexer and index pages
    indexer = HybridSearchIndexer(db_path)
    indexer.clear_index()
    indexer.index_pages(cleaned_pages)
    
    # Show stats
    stats = indexer.get_stats()
    logger.info(f"Hybrid index built: {stats}")
    
    indexer.close()
    return stats


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Build hybrid index
    cleaned_data = "../data/cleaned/cleaned_pages.json"
    db_path = "../data/index/playbook_hybrid.db"
    
    build_hybrid_index(cleaned_data, db_path)
