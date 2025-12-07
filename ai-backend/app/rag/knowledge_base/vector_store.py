from typing import List, Dict, Optional, Any
from loguru import logger
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
import json

from app.config import get_settings


class MilvusVectorStore:
    # Milvus vector database manager for storing and retrieving document embeddings

    def __init__(
        self,
        collection_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        embedding_dim: Optional[int] = None
    ):
        # Initialize Milvus connection and collection
        settings = get_settings()

        self.collection_name = collection_name or settings.milvus_collection_name
        self.host = host or settings.milvus_host
        self.port = port or settings.milvus_port
        self.embedding_dim = embedding_dim or settings.embedding_dimension

        # Index parameters
        self.index_type = settings.milvus_index_type
        self.metric_type = settings.milvus_metric_type
        self.nlist = settings.milvus_nlist
        self.nprobe = settings.milvus_nprobe

        # Connection alias
        self.alias = "default"

        # Collection reference
        self.collection = None

        logger.info(
            f"Initialized MilvusVectorStore: {self.host}:{self.port}, "
            f"collection={self.collection_name}, dim={self.embedding_dim}"
        )

    def connect(self):
        # Connect to Milvus server
        try:
            connections.connect(
                alias=self.alias,
                host=self.host,
                port=self.port
            )
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {str(e)}")
            raise

    def disconnect(self):
        # Disconnect from Milvus server
        try:
            connections.disconnect(alias=self.alias)
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.warning(f"Error disconnecting from Milvus: {str(e)}")

    def create_collection(self, drop_existing: bool = False):
        # Create collection with schema for astrology knowledge base

        # Drop existing collection if requested
        if drop_existing and utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            logger.info(f"Dropped existing collection: {self.collection_name}")

        # Check if collection already exists
        if utility.has_collection(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' already exists")
            self.collection = Collection(self.collection_name)
            return self.collection

        # Define schema fields
        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=256,
                description="Unique identifier for the chunk"
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=65535,
                description="Text content of the chunk"
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.embedding_dim,
                description="Embedding vector"
            ),
            FieldSchema(
                name="source_file",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Source PDF filename"
            ),
            FieldSchema(
                name="category",
                dtype=DataType.VARCHAR,
                max_length=128,
                description="Document category"
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.INT64,
                description="Page number in source document"
            ),
            FieldSchema(
                name="chunk_index",
                dtype=DataType.INT64,
                description="Index of chunk in document"
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.VARCHAR,
                max_length=65535,
                description="Additional metadata as JSON string"
            )
        ]

        # Create schema
        schema = CollectionSchema(
            fields=fields,
            description="Astrology knowledge base collection",
            enable_dynamic_field=False
        )

        # Create collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema,
            using=self.alias
        )

        logger.info(f"Created collection: {self.collection_name}")
        return self.collection

    def create_index(self):
        # Create IVF_FLAT index on embedding field for similarity search

        if self.collection is None:
            raise ValueError("Collection not loaded. Call create_collection() or load_collection() first.")

        # Index parameters
        index_params = {
            "metric_type": self.metric_type,
            "index_type": self.index_type,
            "params": {"nlist": self.nlist}
        }

        # Create index on embedding field
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )

        logger.info(
            f"Created index on 'embedding' field: "
            f"type={self.index_type}, metric={self.metric_type}"
        )

    def load_collection(self):
        # Load collection into memory for search operations

        if self.collection is None:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
            else:
                raise ValueError(f"Collection '{self.collection_name}' does not exist")

        self.collection.load()
        logger.info(f"Loaded collection '{self.collection_name}' into memory")

    def insert_documents(
        self,
        embedded_docs: List[Dict],
        batch_size: int = 100
    ) -> List[str]:
        # Insert embedded documents into Milvus collection in batches

        if self.collection is None:
            raise ValueError("Collection not loaded")

        total_docs = len(embedded_docs)
        all_inserted_ids = []

        logger.info(f"Inserting {total_docs} documents in batches of {batch_size}...")

        for i in range(0, total_docs, batch_size):
            batch = embedded_docs[i:i + batch_size]

            # Prepare data for insertion
            ids = []
            texts = []
            embeddings = []
            source_files = []
            categories = []
            page_numbers = []
            chunk_indices = []
            metadatas = []

            for doc in batch:
                metadata = doc.get('metadata', {})

                ids.append(metadata.get('chunk_id', f'unknown_{i}'))
                texts.append(doc['text'])
                embeddings.append(doc['embedding'])
                source_files.append(metadata.get('source_file', 'unknown'))
                categories.append(metadata.get('category', 'general'))
                page_numbers.append(metadata.get('page_number', 0))
                chunk_indices.append(metadata.get('chunk_index', 0))
                metadatas.append(json.dumps(metadata))

            # Insert batch
            data = [
                ids,
                texts,
                embeddings,
                source_files,
                categories,
                page_numbers,
                chunk_indices,
                metadatas
            ]

            insert_result = self.collection.insert(data)
            all_inserted_ids.extend(insert_result.primary_keys)

            batch_num = (i // batch_size) + 1
            total_batches = (total_docs + batch_size - 1) // batch_size
            logger.info(f"Inserted batch {batch_num}/{total_batches}")

        # Flush to persist data
        self.collection.flush()
        logger.info(f"Successfully inserted {len(all_inserted_ids)} documents")

        return all_inserted_ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_expr: Optional[str] = None
    ) -> List[Dict]:
        # Search for similar documents using embedding vector

        if self.collection is None:
            raise ValueError("Collection not loaded")

        # Search parameters
        search_params = {
            "metric_type": self.metric_type,
            "params": {"nprobe": self.nprobe}
        }

        # Output fields to return
        output_fields = [
            "text",
            "source_file",
            "category",
            "page_number",
            "chunk_index",
            "metadata"
        ]

        # Perform search
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=output_fields
        )

        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                # Access entity fields as attributes, not dict keys
                metadata_str = getattr(hit.entity, 'metadata', '{}')
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "distance": hit.distance,
                    "text": getattr(hit.entity, 'text', ''),
                    "source_file": getattr(hit.entity, 'source_file', ''),
                    "category": getattr(hit.entity, 'category', ''),
                    "page_number": getattr(hit.entity, 'page_number', 0),
                    "chunk_index": getattr(hit.entity, 'chunk_index', 0),
                    "metadata": json.loads(metadata_str) if metadata_str else {}
                }
                formatted_results.append(result)

        return formatted_results

    def search_with_filters(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        category: Optional[str] = None,
        source_file: Optional[str] = None
    ) -> List[Dict]:
        # Search with optional category or source file filters

        filter_conditions = []

        if category:
            filter_conditions.append(f'category == "{category}"')

        if source_file:
            filter_conditions.append(f'source_file == "{source_file}"')

        filter_expr = " and ".join(filter_conditions) if filter_conditions else None

        return self.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_expr=filter_expr
        )

    def get_collection_stats(self) -> Dict:
        # Get statistics about the collection

        if self.collection is None:
            raise ValueError("Collection not loaded")

        stats = {
            "name": self.collection.name,
            "num_entities": self.collection.num_entities,
            "schema": str(self.collection.schema),
            "indexes": [str(index) for index in self.collection.indexes]
        }

        logger.info(f"Collection stats: {stats['num_entities']} entities")
        return stats

    def delete_by_ids(self, ids: List[str]):
        # Delete documents by their IDs

        if self.collection is None:
            raise ValueError("Collection not loaded")

        expr = f'id in {json.dumps(ids)}'
        self.collection.delete(expr)
        self.collection.flush()

        logger.info(f"Deleted {len(ids)} documents")

    def drop_collection(self):
        # Drop the entire collection

        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            self.collection = None
            logger.info(f"Dropped collection: {self.collection_name}")
        else:
            logger.warning(f"Collection '{self.collection_name}' does not exist")


# Factory function to get a MilvusVectorStore instance
def get_vector_store(collection_name: Optional[str] = None) -> MilvusVectorStore:
    return MilvusVectorStore(collection_name=collection_name)
