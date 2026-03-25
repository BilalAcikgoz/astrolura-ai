from typing import List, Dict, Optional
from loguru import logger
from pymilvus import (
    connections, Collection, CollectionSchema,
    FieldSchema, DataType, utility, db
)
import json

from config import vectordb_settings, embedding_settings


class MilvusVectorStore:
    """astrolura-ai Milvus vector database manager with HNSW index."""

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.database = vectordb_settings.milvus_database
        self.host = vectordb_settings.milvus_host
        self.port = vectordb_settings.milvus_port
        self.embedding_dim = embedding_settings.embedding_dimension

        # Index parameters (HNSW)
        self.index_type = vectordb_settings.milvus_index_type
        self.metric_type = vectordb_settings.milvus_metric_type
        self.hnsw_m = vectordb_settings.milvus_hnsw_m
        self.hnsw_ef_construction = vectordb_settings.milvus_hnsw_ef_construction
        self.hnsw_ef_search = vectordb_settings.milvus_hnsw_ef_search

        self.alias = "default"
        self.collection = None

        logger.info(
            f"Initialized MilvusVectorStore: {self.host}:{self.port}, "
            f"database={self.database}, collection={self.collection_name}, dim={self.embedding_dim}"
        )

    def connect(self):
        try:
            # Step 1: Connect to default database to manage databases
            connections.connect(alias=self.alias, host=self.host, port=self.port)

            # Step 2: Create our database if it doesn't exist
            existing_dbs = db.list_database()
            if self.database not in existing_dbs:
                db.create_database(self.database)
                logger.info(f"Created database: {self.database}")
            else:
                logger.info(f"Database '{self.database}' already exists")

            # Step 3: Reconnect using our database
            connections.disconnect(alias=self.alias)
            connections.connect(
                alias=self.alias,
                host=self.host,
                port=self.port,
                db_name=self.database,
            )
            logger.info(f"Connected to Milvus at {self.host}:{self.port}, database={self.database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {str(e)}")
            raise

    def disconnect(self):
        try:
            connections.disconnect(alias=self.alias)
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.warning(f"Error disconnecting from Milvus: {str(e)}")

    def create_collection(self, drop_existing: bool = False):
        if drop_existing and utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            logger.info(f"Dropped existing collection: {self.collection_name}")

        if utility.has_collection(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' already exists")
            self.collection = Collection(self.collection_name)
            return self.collection

        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=256),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="source_file", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="page_number", dtype=DataType.INT64),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="astrolura-ai astrology knowledge base",
            enable_dynamic_field=False,
        )

        self.collection = Collection(
            name=self.collection_name, schema=schema, using=self.alias
        )
        logger.info(f"Created collection: {self.collection_name}")
        return self.collection

    def create_index(self):
        if self.collection is None:
            raise ValueError("Collection not loaded.")

        index_params = {
            "metric_type": self.metric_type,
            "index_type": self.index_type,
            "params": {
                "M": self.hnsw_m,
                "efConstruction": self.hnsw_ef_construction,
            },
        }

        self.collection.create_index(field_name="embedding", index_params=index_params)
        logger.info(
            f"Created HNSW index: metric={self.metric_type}, "
            f"M={self.hnsw_m}, efConstruction={self.hnsw_ef_construction}"
        )

    def load_collection(self):
        if self.collection is None:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
            else:
                raise ValueError(f"Collection '{self.collection_name}' does not exist")
        self.collection.load()
        logger.info(f"Loaded collection '{self.collection_name}' into memory")

    def insert_documents(self, embedded_docs: List[Dict], batch_size: int = 100) -> List[str]:
        if self.collection is None:
            raise ValueError("Collection not loaded")

        total_docs = len(embedded_docs)
        all_inserted_ids = []

        logger.info(f"Inserting {total_docs} documents in batches of {batch_size}...")

        for i in range(0, total_docs, batch_size):
            batch = embedded_docs[i : i + batch_size]

            ids, texts, embeddings = [], [], []
            source_files, categories = [], []
            page_numbers, chunk_indices, metadatas = [], [], []

            for doc in batch:
                metadata = doc.get("metadata", {})
                ids.append(metadata.get("chunk_id", f"unknown_{i}"))
                texts.append(doc["text"])
                embeddings.append(doc["embedding"])
                source_files.append(metadata.get("source_file", "unknown"))
                categories.append(metadata.get("category", "general"))
                page_numbers.append(metadata.get("page_number", 0))
                chunk_indices.append(metadata.get("chunk_index", 0))
                metadatas.append(json.dumps(metadata))

            data = [ids, texts, embeddings, source_files, categories, page_numbers, chunk_indices, metadatas]
            insert_result = self.collection.insert(data)
            all_inserted_ids.extend(insert_result.primary_keys)

            batch_num = (i // batch_size) + 1
            total_batches = (total_docs + batch_size - 1) // batch_size
            logger.info(f"Inserted batch {batch_num}/{total_batches}")

        self.collection.flush()
        logger.info(f"Successfully inserted {len(all_inserted_ids)} documents")
        return all_inserted_ids

    def search(
        self, query_embedding: List[float], top_k: int = 5, filter_expr: Optional[str] = None
    ) -> List[Dict]:
        if self.collection is None:
            raise ValueError("Collection not loaded")

        search_params = {
            "metric_type": self.metric_type,
            "params": {"ef": self.hnsw_ef_search},
        }

        output_fields = ["text", "source_file", "category", "page_number", "chunk_index", "metadata"]

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=output_fields,
        )

        formatted_results = []
        for hits in results:
            for hit in hits:
                metadata_str = getattr(hit.entity, "metadata", "{}")
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "distance": hit.distance,
                    "text": getattr(hit.entity, "text", ""),
                    "source_file": getattr(hit.entity, "source_file", ""),
                    "category": getattr(hit.entity, "category", ""),
                    "page_number": getattr(hit.entity, "page_number", 0),
                    "chunk_index": getattr(hit.entity, "chunk_index", 0),
                    "metadata": json.loads(metadata_str) if metadata_str else {},
                }
                formatted_results.append(result)

        return formatted_results

    def search_with_filters(
        self, query_embedding: List[float], top_k: int = 5,
        category: Optional[str] = None, source_file: Optional[str] = None
    ) -> List[Dict]:
        filter_conditions = []
        if category:
            filter_conditions.append(f'category == "{category}"')
        if source_file:
            filter_conditions.append(f'source_file == "{source_file}"')
        filter_expr = " and ".join(filter_conditions) if filter_conditions else None
        return self.search(query_embedding=query_embedding, top_k=top_k, filter_expr=filter_expr)

    def get_collection_stats(self) -> Dict:
        if self.collection is None:
            raise ValueError("Collection not loaded")
        stats = {
            "name": self.collection.name,
            "num_entities": self.collection.num_entities,
            "schema": str(self.collection.schema),
            "indexes": [str(index) for index in self.collection.indexes],
        }
        logger.info(f"Collection stats: {stats['num_entities']} entities")
        return stats

    def delete_by_ids(self, ids: List[str]):
        if self.collection is None:
            raise ValueError("Collection not loaded")
        expr = f"id in {json.dumps(ids)}"
        self.collection.delete(expr)
        self.collection.flush()
        logger.info(f"Deleted {len(ids)} documents")

    def drop_collection(self):
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            self.collection = None
            logger.info(f"Dropped collection: {self.collection_name}")
        else:
            logger.warning(f"Collection '{self.collection_name}' does not exist")


def get_birth_chart_store() -> MilvusVectorStore:
    return MilvusVectorStore(
        collection_name=vectordb_settings.milvus_birth_chart_collection
    )


def get_transit_chart_store() -> MilvusVectorStore:
    return MilvusVectorStore(
        collection_name=vectordb_settings.milvus_transit_chart_collection
    )
