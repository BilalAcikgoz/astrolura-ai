from typing import List, Dict, Optional
from loguru import logger

from config import rag_settings
from src.embedding.service import EmbeddingService, get_embedding_service
from src.vectordb.store import MilvusVectorStore, get_birth_chart_store, get_transit_chart_store


class RetrievalService:
    """astrolura-ai retrieval service for fetching relevant astrological knowledge."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[MilvusVectorStore] = None,
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or get_birth_chart_store()
        self.top_k = rag_settings.search_top_k
        self.similarity_threshold = rag_settings.similarity_threshold

        logger.info(
            f"Initialized RetrievalService with top_k={self.top_k}, "
            f"threshold={self.similarity_threshold}"
        )

    def generate_queries_from_chart(self, chart_data: Dict) -> List[str]:
        queries = []

        if "planets" in chart_data and len(chart_data["planets"]) > 0:
            sun = chart_data["planets"][0]
            queries.append(f"Sun in {sun['sign_en']} personality traits and characteristics")
            queries.append(f"Sun in {sun['sign_en']} in house {sun['house']}")

        if "planets" in chart_data and len(chart_data["planets"]) > 1:
            moon = chart_data["planets"][1]
            queries.append(f"Moon in {moon['sign_en']} emotional nature")
            queries.append(f"Moon in {moon['sign_en']} in house {moon['house']}")

        if "ascendant" in chart_data:
            asc = chart_data["ascendant"]
            queries.append(f"Ascendant in {asc['sign_en']} rising sign meaning")
            queries.append(f"{asc['sign_en']} rising appearance and first impression")

        planet_names = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        if "planets" in chart_data:
            for planet in chart_data["planets"]:
                if planet["name_en"] in planet_names:
                    queries.append(f"{planet['name_en']} in {planet['sign_en']} interpretation")

        if "houses" in chart_data:
            for house in chart_data["houses"][:4]:
                queries.append(f"{house['sign_en']} on the cusp of house {house['number']}")

        if "aspects" in chart_data:
            major_aspects = ["Conjunction", "Opposition", "Trine", "Square", "Sextile"]
            aspect_count = 0
            for aspect in chart_data["aspects"]:
                if aspect["aspect_en"] in major_aspects and aspect_count < 5:
                    queries.append(
                        f"{aspect['planet1']} {aspect['aspect_en']} {aspect['planet2']} aspect meaning"
                    )
                    aspect_count += 1

        if "elements" in chart_data:
            elements = chart_data["elements"]
            dominant_element = max(elements.items(), key=lambda x: x[1])[0]
            queries.append(f"Dominant {dominant_element} element in astrology")

        if "qualities" in chart_data:
            qualities = chart_data["qualities"]
            dominant_quality = max(qualities.items(), key=lambda x: x[1])[0]
            queries.append(f"Dominant {dominant_quality} quality modality in astrology")

        logger.info(f"Generated {len(queries)} queries from birth chart")
        return queries

    def retrieve_context(
        self,
        chart_data: Dict,
        queries: Optional[List[str]] = None,
        max_queries: Optional[int] = None,
        deduplicate: bool = True,
    ) -> List[Dict]:
        max_queries = max_queries or rag_settings.max_queries

        if queries is None:
            queries = self.generate_queries_from_chart(chart_data)

        if max_queries and len(queries) > max_queries:
            original_count = len(queries)
            queries = queries[:max_queries]
            logger.info(f"Limited to {max_queries} queries (from {original_count})")

        all_results = []
        seen_chunk_ids = set()
        total_searched = 0

        logger.info(f"Starting RAG retrieval with {len(queries)} queries...")

        for i, query in enumerate(queries, 1):
            logger.debug(f"Query {i}/{len(queries)}: {query}")

            query_embedding = self.embedding_service.embed_text(query)
            results = self.vector_store.search(
                query_embedding=query_embedding, top_k=self.top_k
            )
            total_searched += len(results)

            for result in results:
                # COSINE similarity: higher is better (1=identical, 0=orthogonal)
                if result["score"] >= self.similarity_threshold:
                    if deduplicate:
                        if result["id"] not in seen_chunk_ids:
                            result["query"] = query
                            all_results.append(result)
                            seen_chunk_ids.add(result["id"])
                    else:
                        result["query"] = query
                        all_results.append(result)

        # Sort by score (higher is better for COSINE similarity)
        all_results.sort(key=lambda x: x["score"], reverse=True)

        avg_score = sum(r["score"] for r in all_results) / len(all_results) if all_results else 0

        logger.info(
            f"RAG Retrieval Complete:\n"
            f"  Queries: {len(queries)}\n"
            f"  Total Searched: {total_searched}\n"
            f"  Relevant Chunks: {len(all_results)}\n"
            f"  Unique Sources: {len(set(r['source_file'] for r in all_results))}\n"
            f"  Avg Similarity Score: {avg_score:.4f}"
        )

        return all_results

    def format_context(self, results: List[Dict], max_chunks: Optional[int] = None) -> str:
        max_chunks = max_chunks or rag_settings.max_context_chunks
        if max_chunks:
            results = results[:max_chunks]

        if not results:
            return "No relevant astrological knowledge found in the database."

        context_parts = []
        for i, result in enumerate(results, 1):
            context_part = f"""[Source {i}]
Category: {result['category']}
Relevance: {result['score']:.2%}

{result['text']}
"""
            context_parts.append(context_part.strip())

        formatted_context = "\n\n---\n\n".join(context_parts)
        logger.info(f"Formatted {len(results)} chunks into context string")
        return formatted_context

    def disconnect(self):
        self.vector_store.disconnect()
        logger.info("Disconnected retrieval service")


def get_retrieval_service(
    embedding_service: Optional[EmbeddingService] = None,
    vector_store: Optional[MilvusVectorStore] = None,
) -> RetrievalService:
    return RetrievalService(
        embedding_service=embedding_service, vector_store=vector_store
    )


def generate_transit_queries(natal_chart_data: Dict, transit_aspects: List[Dict]) -> List[str]:
    """Generate RAG search queries focused on transit aspects."""
    queries = []

    # Prioritize tight applying aspects (orb < 1.0°)
    priority = [a for a in transit_aspects if a.get("applying") and a.get("orb", 99) < 1.0]
    others = [a for a in transit_aspects if a not in priority]
    ordered = priority + others

    for aspect in ordered[:8]:
        t_en = aspect.get("transit_planet_en", "")
        n_en = aspect.get("natal_planet_en", "")
        asp_en = aspect.get("aspect_en", "")
        queries.append(f"{t_en} transit {asp_en} natal {n_en} meaning effects")

    # Add a few sign-based queries for the most active transit planets
    seen_planets: set = set()
    if "planets" in natal_chart_data:
        natal_planet_map = {
            p.get("name_en", ""): p for p in natal_chart_data["planets"]
            if isinstance(p, dict)
        }
    else:
        natal_planet_map = {}

    for aspect in ordered[:4]:
        t_en = aspect.get("transit_planet_en", "")
        if t_en not in seen_planets:
            seen_planets.add(t_en)
            n_en = aspect.get("natal_planet_en", "")
            natal_p = natal_planet_map.get(n_en, {})
            sign_en = natal_p.get("sign_en", "")
            if sign_en:
                queries.append(f"{t_en} transit through {sign_en} effects")

    logger.info(f"Generated {len(queries)} transit RAG queries")
    return queries


def get_transit_retrieval_service(
    embedding_service: Optional[EmbeddingService] = None,
) -> RetrievalService:
    """Return a RetrievalService using the transit chart vector store."""
    return RetrievalService(
        embedding_service=embedding_service,
        vector_store=get_transit_chart_store(),
    )
