from typing import Optional
from loguru import logger

from app.rag.embeddings.service import AstrologyEmbeddingService, get_astrology_embedding_service
from app.rag.knowledge_base.vector_store import MilvusVectorStore, get_vector_store
from app.rag.retrieval.service import AstrologyRetrievalService
from app.rag.generation.service import AstrologyGenerationService, get_astrology_generation_service

class AstrologyRAGServiceManager:
    """
    Singleton manager for RAG services.
    Handles initialization, connection management, and cleanup.
    """
    _instance: Optional['AstrologyRAGServiceManager'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not AstrologyRAGServiceManager._initialized:
            self._embedding_service: Optional[AstrologyEmbeddingService] = None
            self._vector_store: Optional[MilvusVectorStore] = None
            self._retrieval_service: Optional[AstrologyRetrievalService] = None
            self._generation_service: Optional[AstrologyGenerationService] = None
            self._connected: bool = False
            AstrologyRAGServiceManager._initialized = True

    async def initialize(self) -> bool:
        """Initialize all RAG services and connect to Milvus."""
        try:
            logger.info("Initializing RAG services...")

            # Initialize embedding service
            self._embedding_service = get_astrology_embedding_service()
            logger.info("Embedding service initialized")

            # Initialize vector store and connect
            self._vector_store = get_vector_store()
            self._vector_store.connect()

            # Load collection if it exists
            try:
                self._vector_store.load_collection()
                logger.info("Vector store collection loaded successfully")
            except Exception as e:
                logger.warning(f"Collection not found or could not be loaded: {e}")
                logger.info("Run 'python scripts/ingest_pdfs.py' to populate the knowledge base")
                # Mark as not connected if collection can't be loaded
                self._connected = False

            # Initialize generation service
            self._generation_service = get_astrology_generation_service()
            logger.info("Generation service initialized")

            self._connected = True
            logger.info("RAG services initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize RAG services: {e}")
            self._connected = False
            return False

    async def shutdown(self):
        """Cleanup and disconnect all services."""
        try:
            logger.info("Shutting down RAG services...")

            if self._vector_store:
                self._vector_store.disconnect()

            self._connected = False
            logger.info("RAG services shut down successfully")

        except Exception as e:
            logger.error(f"Error during RAG services shutdown: {e}")

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def embedding_service(self) -> AstrologyEmbeddingService:
        if not self._embedding_service:
            raise RuntimeError("RAG services not initialized. Call initialize() first.")
        return self._embedding_service

    @property
    def vector_store(self) -> MilvusVectorStore:
        if not self._vector_store:
            raise RuntimeError("RAG services not initialized. Call initialize() first.")
        return self._vector_store

    @property
    def generation_service(self) -> AstrologyGenerationService:
        if not self._generation_service:
            raise RuntimeError("RAG services not initialized. Call initialize() first.")
        return self._generation_service

    def get_retrieval_service(
        self,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> 'ManagedAstrologyRetrievalService':
        """Get a retrieval service that uses managed connections."""
        if not self._connected:
            raise RuntimeError("RAG services not initialized. Call initialize() first.")

        return ManagedAstrologyRetrievalService(
            embedding_service=self._embedding_service,
            vector_store=self._vector_store,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )


class ManagedAstrologyRetrievalService:
    """
    Retrieval service that uses pre-initialized connections.
    Unlike RetrievalService, this doesn't create its own connections.
    """

    def __init__(
        self,
        embedding_service: AstrologyEmbeddingService,
        vector_store: MilvusVectorStore,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

        logger.info(
            f"Initialized ManagedRetrievalService with top_k={top_k}, "
            f"threshold={similarity_threshold}"
        )

    def generate_queries_from_chart(self, chart_data: dict) -> list:
        """Generate search queries from birth chart data."""
        queries = []

        # Query for Sun sign
        if 'planets' in chart_data and len(chart_data['planets']) > 0:
            sun = chart_data['planets'][0]
            queries.append(f"Sun in {sun['sign_en']} personality traits and characteristics")
            queries.append(f"Sun in {sun['sign_en']} in house {sun['house']}")

        # Query for Moon sign
        if 'planets' in chart_data and len(chart_data['planets']) > 1:
            moon = chart_data['planets'][1]
            queries.append(f"Moon in {moon['sign_en']} emotional nature")
            queries.append(f"Moon in {moon['sign_en']} in house {moon['house']}")

        # Query for Ascendant
        if 'ascendant' in chart_data:
            asc = chart_data['ascendant']
            queries.append(f"Ascendant in {asc['sign_en']} rising sign meaning")
            queries.append(f"{asc['sign_en']} rising appearance and first impression")

        # Query for major planets (Mercury, Venus, Mars, Jupiter, Saturn)
        planet_names = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        if 'planets' in chart_data:
            for planet in chart_data['planets']:
                if planet['name_en'] in planet_names:
                    queries.append(
                        f"{planet['name_en']} in {planet['sign_en']} interpretation"
                    )

        # Query for houses (first 4)
        if 'houses' in chart_data:
            for house in chart_data['houses'][:4]:
                queries.append(
                    f"{house['sign_en']} on the cusp of house {house['number']}"
                )

        # Query for major aspects
        if 'aspects' in chart_data:
            major_aspects = ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']
            aspect_count = 0
            for aspect in chart_data['aspects']:
                if aspect['aspect_en'] in major_aspects and aspect_count < 5:
                    queries.append(
                        f"{aspect['planet1']} {aspect['aspect_en']} {aspect['planet2']} aspect meaning"
                    )
                    aspect_count += 1

        # Query for element balance
        if 'elements' in chart_data:
            elements = chart_data['elements']
            dominant_element = max(elements.items(), key=lambda x: x[1])[0]
            queries.append(f"Dominant {dominant_element} element in astrology")

        # Query for quality balance
        if 'qualities' in chart_data:
            qualities = chart_data['qualities']
            dominant_quality = max(qualities.items(), key=lambda x: x[1])[0]
            queries.append(f"Dominant {dominant_quality} quality modality in astrology")

        logger.info(f"Generated {len(queries)} queries from birth chart")
        return queries

    def retrieve_context(
        self,
        chart_data: dict,
        max_queries: int = 10,
        deduplicate: bool = True
    ) -> list:
        """Retrieve relevant context from vector database based on birth chart."""
        # Generate queries
        all_queries = self.generate_queries_from_chart(chart_data)

        # Limit number of queries if specified
        if max_queries and len(all_queries) > max_queries:
            queries = all_queries[:max_queries]
            logger.info(f"Limited to {max_queries} queries (from {len(all_queries)})")
        else:
            queries = all_queries

        # Retrieve documents for each query
        all_results = []
        seen_chunk_ids = set()
        total_searched = 0

        logger.info(f"🔍 Starting RAG retrieval with {len(queries)} queries...")

        for i, query in enumerate(queries, 1):
            logger.debug(f"Query {i}/{len(queries)}: {query}")

            # Generate embedding for query
            query_embedding = self.embedding_service.embed_text(query)

            # Search in vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=self.top_k
            )
            total_searched += len(results)

            # Filter by similarity threshold and deduplicate
            for result in results:
                # L2 distance: lower is better, so we check <= threshold
                if result['score'] <= self.similarity_threshold:
                    if deduplicate:
                        if result['id'] not in seen_chunk_ids:
                            result['query'] = query
                            all_results.append(result)
                            seen_chunk_ids.add(result['id'])
                    else:
                        result['query'] = query
                        all_results.append(result)

        # Sort by score (lower is better for L2 distance)
        all_results.sort(key=lambda x: x['score'])

        # Calculate some stats
        avg_score = sum(r['score'] for r in all_results) / len(all_results) if all_results else 0

        logger.info(
            f"📚 RAG Retrieval Complete:\n"
            f"├─ Queries: {len(queries)}\n"
            f"├─ Total Searched: {total_searched}\n"
            f"├─ Relevant Chunks: {len(all_results)}\n"
            f"├─ Unique Sources: {len(set(r['source_file'] for r in all_results))}\n"
            f"└─ Avg Similarity Score: {avg_score:.4f}"
        )

        return all_results

    def format_context(
        self,
        results: list,
        max_chunks: int = 15
    ) -> str:
        """Format retrieved results into context string for LLM."""
        # Limit number of chunks
        if max_chunks:
            results = results[:max_chunks]

        if not results:
            return "No relevant astrological knowledge found in the database."

        context_parts = []

        for i, result in enumerate(results, 1):
            context_part = f"""[Source {i}]
Category: {result['category']}
Relevance: {1 - result['score']:.2%}

{result['text']}
"""
            context_parts.append(context_part.strip())

        formatted_context = "\n\n---\n\n".join(context_parts)

        logger.info(f"Formatted {len(results)} chunks into context string")

        return formatted_context


# Global service manager instance
_service_manager: Optional[AstrologyRAGServiceManager] = None

def get_astrology_rag_service_manager() -> AstrologyRAGServiceManager:
    """Get the global RAG service manager instance."""
    global _service_manager
    if _service_manager is None:
        _service_manager = AstrologyRAGServiceManager()
    return _service_manager
