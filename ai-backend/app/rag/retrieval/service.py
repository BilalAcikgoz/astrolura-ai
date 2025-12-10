from typing import List, Dict, Optional, Set
from loguru import logger

from app.rag.embeddings.service import get_astrology_embedding_service
from app.rag.knowledge_base import get_vector_store

class AstrologyRetrievalService:
    # Service for retrieving relevant astrological knowledge based on birth chart data

    def __init__(
        self,
        top_k: int = 5,
        similarity_threshold: float = 0.8
    ):
        # Initialize retrieval service with embedding and vector store services
        self.embedding_service = get_astrology_embedding_service()
        self.vector_store = get_vector_store()
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

        # Connect to Milvus
        self.vector_store.connect()
        self.vector_store.load_collection()

        logger.info(
            f"Initialized RetrievalService with top_k={top_k}, "
            f"threshold={similarity_threshold}"
        )

    def generate_queries_from_chart(self, chart_data: Dict) -> List[str]:
        # Generate search queries from birth chart data
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

        # Query for houses
        if 'houses' in chart_data:
            for house in chart_data['houses'][:4]:  # First 4 houses
                queries.append(
                    f"{house['sign_en']} on the cusp of house {house['number']}"
                )

        # Query for major aspects
        if 'aspects' in chart_data:
            major_aspects = ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']
            for aspect in chart_data['aspects']:
                if aspect['aspect_en'] in major_aspects:
                    queries.append(
                        f"{aspect['planet1']} {aspect['aspect_en']} {aspect['planet2']} aspect meaning"
                    )

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
        chart_data: Dict,
        max_queries: Optional[int] = 10,
        deduplicate: bool = True
    ) -> List[Dict]:
        # Retrieve relevant context from vector database based on birth chart

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

        for i, query in enumerate(queries, 1):
            logger.debug(f"Query {i}/{len(queries)}: {query}")

            # Generate embedding for query
            query_embedding = self.embedding_service.embed_text(query)

            # Search in vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=self.top_k
            )

            # Filter by similarity threshold and deduplicate
            for result in results:
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

        logger.info(
            f"Retrieved {len(all_results)} relevant documents "
            f"from {len(queries)} queries"
        )

        return all_results

    def format_context(
        self,
        results: List[Dict],
        max_chunks: Optional[int] = 20
    ) -> str:
        # Format retrieved results into context string for LLM

        # Limit number of chunks
        if max_chunks:
            results = results[:max_chunks]

        context_parts = []

        for i, result in enumerate(results, 1):
            context_part = f"""
[Source {i}]
File: {result['source_file']}
Category: {result['category']}
Page: {result['page_number']}
Relevance Score: {result['score']:.4f}
Query: {result.get('query', 'N/A')}

Content:
{result['text']}

---
"""
            context_parts.append(context_part.strip())

        formatted_context = "\n\n".join(context_parts)

        logger.info(f"Formatted {len(results)} chunks into context string")

        return formatted_context

    def retrieve_by_category(
        self,
        query: str,
        category: str,
        top_k: Optional[int] = None
    ) -> List[Dict]:
        # Retrieve documents filtered by category

        top_k = top_k or self.top_k

        logger.info(f"Retrieving from category '{category}' for query: {query}")

        # Generate embedding
        query_embedding = self.embedding_service.embed_text(query)

        # Search with category filter
        results = self.vector_store.search_with_filters(
            query_embedding=query_embedding,
            top_k=top_k,
            category=category
        )

        return results

    def get_category_specific_context(
        self,
        chart_data: Dict
    ) -> Dict[str, List[Dict]]:
        # Retrieve context organized by category

        category_contexts = {
            'houses': [],
            'aspects': [],
            'planets': [],
            'general': []
        }

        # Houses context
        if 'houses' in chart_data:
            house_query = "astrological houses meanings and interpretations"
            category_contexts['houses'] = self.retrieve_by_category(
                house_query,
                'houses',
                top_k=5
            )

        # Aspects context
        if 'aspects' in chart_data:
            aspect_query = "planetary aspects interpretations"
            category_contexts['aspects'] = self.retrieve_by_category(
                aspect_query,
                'aspects',
                top_k=5
            )

        # General planet interpretations
        if 'planets' in chart_data:
            planet_query = "planets in signs and houses interpretations"
            # Search in multiple relevant categories
            for cat in ['psychological_astrology', 'hellenistic_astrology']:
                results = self.retrieve_by_category(
                    planet_query,
                    cat,
                    top_k=3
                )
                category_contexts['general'].extend(results)

        return category_contexts

    def disconnect(self):
        # Disconnect from Milvus
        self.vector_store.disconnect()
        logger.info("Disconnected retrieval service")


# Factory function to get a RetrievalService instance
def get_astrology_retrieval_service(
    top_k: int = 5,
    similarity_threshold: float = 0.8
) -> AstrologyRetrievalService:
    return AstrologyRetrievalService(
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
