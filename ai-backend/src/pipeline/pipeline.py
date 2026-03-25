from typing import Optional
from typing_extensions import TypedDict
from loguru import logger
from langgraph.graph import StateGraph, END

from src.retrieval.service import RetrievalService, get_retrieval_service, get_transit_retrieval_service, generate_transit_queries
from src.llm.service import LLMService, get_llm_service


class BirthChartPipelineState(TypedDict):
    chart_data: dict
    language: str
    queries: list
    retrieved_chunks: list
    formatted_context: str
    interpretation: str


class BirthChartPipeline:
    """astrolura-ai LangGraph pipeline for birth chart interpretation."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        llm_service: Optional[LLMService] = None,
    ):
        self.retrieval_service = retrieval_service or get_retrieval_service()
        self.llm_service = llm_service or get_llm_service()
        self.graph = self._build_graph()
        logger.info("Initialized BirthChartPipeline with LangGraph")

    def _build_graph(self):
        workflow = StateGraph(BirthChartPipelineState)

        workflow.add_node("generate_queries", self._generate_queries)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("format_context", self._format_context)
        workflow.add_node("generate_interpretation", self._generate_interpretation)

        workflow.set_entry_point("generate_queries")
        workflow.add_edge("generate_queries", "retrieve_context")
        workflow.add_edge("retrieve_context", "format_context")
        workflow.add_edge("format_context", "generate_interpretation")
        workflow.add_edge("generate_interpretation", END)

        return workflow.compile()

    def _generate_queries(self, state: BirthChartPipelineState) -> dict:
        logger.info("Pipeline node: generate_queries")
        queries = self.retrieval_service.generate_queries_from_chart(state["chart_data"])
        return {"queries": queries}

    def _retrieve_context(self, state: BirthChartPipelineState) -> dict:
        logger.info("Pipeline node: retrieve_context")
        chunks = self.retrieval_service.retrieve_context(
            chart_data=state["chart_data"],
            queries=state["queries"],
        )
        return {"retrieved_chunks": chunks}

    def _format_context(self, state: BirthChartPipelineState) -> dict:
        logger.info("Pipeline node: format_context")
        formatted = self.retrieval_service.format_context(state["retrieved_chunks"])
        return {"formatted_context": formatted}

    def _generate_interpretation(self, state: BirthChartPipelineState) -> dict:
        logger.info("Pipeline node: generate_interpretation")
        interpretation = self.llm_service.generate_interpretation(
            chart_data=state["chart_data"],
            context=state["formatted_context"],
            language=state["language"],
        )
        return {"interpretation": interpretation}

    def run(self, chart_data: dict, language: str = "tr") -> str:
        logger.info(
            f"Running pipeline for {chart_data.get('chart_info', {}).get('name', 'Unknown')}, "
            f"language={language}"
        )
        initial_state: BirthChartPipelineState = {
            "chart_data": chart_data,
            "language": language,
            "queries": [],
            "retrieved_chunks": [],
            "formatted_context": "",
            "interpretation": "",
        }
        result = self.graph.invoke(initial_state)
        logger.info("Pipeline completed")
        return result["interpretation"]


_birth_chart_pipeline: Optional[BirthChartPipeline] = None


def get_birth_chart_pipeline(
    retrieval_service: Optional[RetrievalService] = None,
    llm_service: Optional[LLMService] = None,
) -> BirthChartPipeline:
    global _birth_chart_pipeline
    if _birth_chart_pipeline is None:
        _birth_chart_pipeline = BirthChartPipeline(
            retrieval_service=retrieval_service,
            llm_service=llm_service,
        )
    return _birth_chart_pipeline


def set_birth_chart_pipeline(pipeline: BirthChartPipeline) -> None:
    global _birth_chart_pipeline
    _birth_chart_pipeline = pipeline


# ─────────────────────────────────────────────────────────────────────────────
# Transit Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class TransitPipelineState(TypedDict):
    natal_chart_data: dict
    transit_data: dict
    language: str
    queries: list
    retrieved_chunks: list
    formatted_context: str
    interpretation: str


class TransitPipeline:
    """LangGraph pipeline for transit chart interpretation."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        llm_service: Optional[LLMService] = None,
    ):
        self.retrieval_service = retrieval_service or get_transit_retrieval_service()
        self.llm_service = llm_service or get_llm_service()
        self.graph = self._build_graph()
        logger.info("Initialized TransitPipeline with LangGraph")

    def _build_graph(self):
        workflow = StateGraph(TransitPipelineState)

        workflow.add_node("generate_queries", self._generate_queries)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("format_context", self._format_context)
        workflow.add_node("generate_interpretation", self._generate_interpretation)

        workflow.set_entry_point("generate_queries")
        workflow.add_edge("generate_queries", "retrieve_context")
        workflow.add_edge("retrieve_context", "format_context")
        workflow.add_edge("format_context", "generate_interpretation")
        workflow.add_edge("generate_interpretation", END)

        return workflow.compile()

    def _generate_queries(self, state: TransitPipelineState) -> dict:
        logger.info("Transit pipeline node: generate_queries")
        transit_aspects = state["transit_data"].get("transit_aspects", [])
        queries = generate_transit_queries(state["natal_chart_data"], transit_aspects)
        return {"queries": queries}

    def _retrieve_context(self, state: TransitPipelineState) -> dict:
        logger.info("Transit pipeline node: retrieve_context")
        try:
            chunks = self.retrieval_service.retrieve_context(
                chart_data=state["natal_chart_data"],
                queries=state["queries"],
            )
        except Exception as e:
            logger.warning(f"Transit RAG retrieval failed (graceful fallback): {e}")
            chunks = []
        return {"retrieved_chunks": chunks}

    def _format_context(self, state: TransitPipelineState) -> dict:
        logger.info("Transit pipeline node: format_context")
        chunks = state["retrieved_chunks"]
        if chunks:
            formatted = self.retrieval_service.format_context(chunks)
        else:
            formatted = "No transit knowledge base context available — using LLM knowledge directly."
        from config import rag_settings
        used = min(len(chunks), rag_settings.max_context_chunks or len(chunks))
        logger.info(f"Transit context: {len(chunks)} chunks retrieved, {used} used in prompt")
        return {"formatted_context": formatted}

    def _generate_interpretation(self, state: TransitPipelineState) -> dict:
        logger.info("Transit pipeline node: generate_interpretation")
        interpretation = self.llm_service.generate_transit_interpretation(
            natal_chart_data=state["natal_chart_data"],
            transit_data=state["transit_data"],
            context=state["formatted_context"],
            language=state["language"],
        )
        return {"interpretation": interpretation}

    def run(self, natal_chart_data: dict, transit_data: dict, language: str = "tr") -> str:
        person_name = natal_chart_data.get("chart_info", {}).get("name", "Unknown")
        transit_date = transit_data.get("transit_date", "unknown")
        logger.info(f"Running TransitPipeline for {person_name} on {transit_date}, language={language}")

        initial_state: TransitPipelineState = {
            "natal_chart_data": natal_chart_data,
            "transit_data": transit_data,
            "language": language,
            "queries": [],
            "retrieved_chunks": [],
            "formatted_context": "",
            "interpretation": "",
        }
        result = self.graph.invoke(initial_state)
        logger.info("TransitPipeline completed")
        return result["interpretation"]


_transit_pipeline: Optional[TransitPipeline] = None


def get_transit_pipeline(
    retrieval_service: Optional[RetrievalService] = None,
    llm_service: Optional[LLMService] = None,
) -> TransitPipeline:
    global _transit_pipeline
    if _transit_pipeline is None:
        _transit_pipeline = TransitPipeline(
            retrieval_service=retrieval_service,
            llm_service=llm_service,
        )
    return _transit_pipeline


def set_transit_pipeline(pipeline: TransitPipeline) -> None:
    global _transit_pipeline
    _transit_pipeline = pipeline
