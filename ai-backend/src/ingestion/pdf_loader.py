from pathlib import Path
from typing import List, Dict
from loguru import logger
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class AstrologyPDFLoaderService:
    """astrolura-ai PDF loader service for the astrology knowledge base."""

    def __init__(self, pdf_directory: str = "./data/astrology-documents"):
        self.pdf_directory = Path(pdf_directory)
        if not self.pdf_directory.exists():
            raise ValueError(f"PDF directory does not exist: {pdf_directory}")

        logger.info(f"Initialized PDFLoaderService with directory: {self.pdf_directory}")

    def get_pdf_files(self) -> List[Path]:
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {self.pdf_directory}")
        return pdf_files

    def load_single_pdf(self, pdf_path: Path) -> List[Document]:
        try:
            logger.info(f"Loading PDF: {pdf_path.name}")
            loader = PyPDFLoader(str(pdf_path))
            documents = loader.load()

            for i, doc in enumerate(documents):
                doc.metadata.update({
                    "source_file": pdf_path.name,
                    "source_path": str(pdf_path),
                    "page_number": i + 1,
                    "total_pages": len(documents),
                    "file_type": "pdf",
                    "category": self._categorize_document(pdf_path.name),
                })

            logger.info(f"Loaded {len(documents)} pages from {pdf_path.name}")
            return documents

        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path.name}: {str(e)}")
            raise

    def load_all_pdfs(self) -> Dict[str, List[Document]]:
        all_documents = {}
        pdf_files = self.get_pdf_files()

        if not pdf_files:
            logger.warning("No PDF files found to load")
            return all_documents

        logger.info(f"Loading {len(pdf_files)} PDF files...")

        for pdf_path in pdf_files:
            try:
                documents = self.load_single_pdf(pdf_path)
                all_documents[pdf_path.name] = documents
            except Exception as e:
                logger.error(f"Failed to load {pdf_path.name}: {str(e)}")
                continue

        total_pages = sum(len(docs) for docs in all_documents.values())
        logger.info(
            f"Successfully loaded {len(all_documents)} PDFs "
            f"with {total_pages} total pages"
        )
        return all_documents

    def load_all_pdfs_flat(self) -> List[Document]:
        all_docs_dict = self.load_all_pdfs()
        flat_documents = []
        for documents in all_docs_dict.values():
            flat_documents.extend(documents)
        logger.info(f"Flattened {len(flat_documents)} total documents")
        return flat_documents

    def _categorize_document(self, filename: str) -> str:
        filename_lower = filename.lower()
        if "aspect" in filename_lower:
            return "aspects"
        elif "house" in filename_lower:
            return "houses"
        elif "element" in filename_lower:
            return "elements"
        elif "hellenistic" in filename_lower:
            return "hellenistic_astrology"
        elif "psychology" in filename_lower:
            return "psychological_astrology"
        elif "interpretation" in filename_lower or "chart" in filename_lower:
            return "chart_interpretation"
        else:
            return "general_astrology"


def get_astrology_pdf_loader(
    pdf_directory: str = "./data/astrology-documents",
) -> AstrologyPDFLoaderService:
    return AstrologyPDFLoaderService(pdf_directory=pdf_directory)
